"""
New Energy Vocab - Backend Server
Flask + SQLite + JWT authentication for spaced_repetition_app.html
"""
import os
import json
import sqlite3
import datetime
from functools import wraps

from flask import Flask, request, jsonify, g, send_file
from flask_cors import CORS
import jwt
import bcrypt

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ---------- Config ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "vocab_server.db")
JWT_SECRET = os.environ.get("JWT_SECRET", "new-energy-vocab-jwt-secret-key-2024")
JWT_EXPIRY_DAYS = 30

# ---------- Database ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            data_json TEXT NOT NULL DEFAULT '{}',
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_jti TEXT NOT NULL UNIQUE,
            device_name TEXT DEFAULT 'Unknown',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_active TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    db.commit()
    db.close()

# ---------- Auth Helpers ----------
def generate_token(user_id, username, device_name="Unknown"):
    now = datetime.datetime.utcnow()
    jti = os.urandom(16).hex()
    payload = {
        "sub": str(user_id),
        "username": username,
        "jti": jti,
        "device_name": device_name,
        "iat": now,
        "exp": now + datetime.timedelta(days=JWT_EXPIRY_DAYS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # Record session
    db = get_db()
    db.execute(
        "INSERT INTO sessions (user_id, token_jti, device_name) VALUES (?, ?, ?)",
        (user_id, jti, device_name),
    )
    db.commit()
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        # Verify JTI exists in sessions
        db = get_db()
        row = db.execute(
            "SELECT id FROM sessions WHERE token_jti = ? AND user_id = ?",
            (payload["jti"], int(payload["sub"])),
        ).fetchone()
        if not row:
            return None
        # Update last active
        db.execute(
            "UPDATE sessions SET last_active = datetime('now') WHERE token_jti = ?",
            (payload["jti"],),
        )
        db.commit()
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header[7:]
        payload = verify_token(token)
        if payload is None:
            return jsonify({"error": "Token expired or invalid"}), 401
        g.current_user_id = int(payload["sub"])
        g.current_username = payload["username"]
        g.current_jti = payload["jti"]
        return f(*args, **kwargs)
    return decorated

# ---------- Routes ----------

@app.route("/", methods=["GET"])
def serve_app():
    app_path = os.path.join(os.path.dirname(BASE_DIR), "spaced_repetition_app.html")
    return send_file(app_path, mimetype="text/html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "server": "new-energy-vocab", "version": "1.0.0"})

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    username = (data.get("username") or "").strip()
    password = (data.get("password") or "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        return jsonify({"error": "Username already exists"}), 409

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    db.commit()
    user_id = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()["id"]
    db.execute("INSERT INTO user_data (user_id, data_json) VALUES (?, '{}')", (user_id,))
    db.commit()

    device_name = data.get("device_name", "Unknown")
    token = generate_token(user_id, username, device_name)

    return jsonify({
        "token": token,
        "user": {"id": user_id, "username": username},
        "message": "Registration successful",
    }), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    username = (data.get("username") or "").strip()
    password = (data.get("password") or "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    user = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"error": "Invalid username or password"}), 401

    device_name = data.get("device_name", "Unknown")
    token = generate_token(user["id"], user["username"], device_name)

    return jsonify({
        "token": token,
        "user": {"id": user["id"], "username": user["username"]},
        "message": "Login successful",
    })

@app.route("/api/user/data", methods=["GET"])
@require_auth
def get_user_data():
    db = get_db()
    row = db.execute("SELECT data_json, updated_at FROM user_data WHERE user_id = ?", (g.current_user_id,)).fetchone()
    if not row:
        return jsonify({"data": {}, "updated_at": None})

    try:
        data = json.loads(row["data_json"])
    except (json.JSONDecodeError, TypeError):
        data = {}

    return jsonify({
        "data": data,
        "updated_at": row["updated_at"],
    })

@app.route("/api/user/data", methods=["POST"])
@require_auth
def save_user_data():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    learning_data = data.get("data")
    if learning_data is None:
        return jsonify({"error": "Missing 'data' field"}), 400

    try:
        data_json = json.dumps(learning_data, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Data serialization failed: {str(e)}"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO user_data (user_id, data_json, updated_at) VALUES (?, ?, datetime('now')) "
        "ON CONFLICT(user_id) DO UPDATE SET data_json = excluded.data_json, updated_at = datetime('now')",
        (g.current_user_id, data_json),
    )
    db.commit()

    return jsonify({"message": "Data saved successfully", "updated_at": datetime.datetime.utcnow().isoformat()})

@app.route("/api/user/sessions", methods=["GET"])
@require_auth
def get_sessions():
    db = get_db()
    rows = db.execute(
        "SELECT token_jti, device_name, created_at, last_active FROM sessions WHERE user_id = ? ORDER BY last_active DESC",
        (g.current_user_id,),
    ).fetchall()
    sessions_list = []
    for row in rows:
        sessions_list.append({
            "jti": row["token_jti"],
            "device_name": row["device_name"],
            "created_at": row["created_at"],
            "last_active": row["last_active"],
        })
    return jsonify({"sessions": sessions_list})

@app.route("/api/user/sessions/<jti>", methods=["DELETE"])
@require_auth
def revoke_session(jti):
    db = get_db()
    # Prevent revoking current session
    if jti == g.current_jti:
        return jsonify({"error": "Cannot revoke current session"}), 400
    db.execute("DELETE FROM sessions WHERE token_jti = ? AND user_id = ?", (jti, g.current_user_id))
    db.commit()
    return jsonify({"message": "Session revoked"})

@app.route("/api/user/logout", methods=["POST"])
@require_auth
def logout():
    db = get_db()
    db.execute("DELETE FROM sessions WHERE token_jti = ?", (g.current_jti,))
    db.commit()
    return jsonify({"message": "Logged out successfully"})

# ---------- Main ----------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"[Server] New Energy Vocab server starting on http://localhost:{port}")
    print(f"[Server] Database: {DB_PATH}")
    app.run(host="0.0.0.0", port=port, debug=True)
