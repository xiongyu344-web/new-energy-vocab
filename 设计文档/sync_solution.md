---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 4c863aa1cbdbc6d8f2f9a928a9496dfd_2ddfc138769711f1a7da5254006c9bbf
    ReservedCode1: IIMdO7CIUxpwnuEx3nq2s1ottjvIuRyPqkauGUI4STsw6zgh/FE5Htoz1EinygffGZZIJHrd/j1gOJKWRuHgV1BHsO+8wUqpCU6X8cEcoIEkSTx7hEzIbfdL9kegTGdp5VfH7aU0FggSzCe/gCcE2tbnfDlbk1s+GqGsGYCMe0xEL9BWASmctffGGVI=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 4c863aa1cbdbc6d8f2f9a928a9496dfd_2ddfc138769711f1a7da5254006c9bbf
    ReservedCode2: IIMdO7CIUxpwnuEx3nq2s1ottjvIuRyPqkauGUI4STsw6zgh/FE5Htoz1EinygffGZZIJHrd/j1gOJKWRuHgV1BHsO+8wUqpCU6X8cEcoIEkSTx7hEzIbfdL9kegTGdp5VfH7aU0FggSzCe/gCcE2tbnfDlbk1s+GqGsGYCMe0xEL9BWASmctffGGVI=
---

# 手机电脑同步方案

## 1. 架构总览

```
┌──────────────────────────────────────────────────────┐
│                    云存储层                          │
│   WebDAV / 腾讯云COS / 阿里云OSS / OneDrive          │
└────────────┬──────────────────────────┬──────────────┘
             │                          │
      ┌──────▼──────┐           ┌──────▼──────┐
      │  PC 客户端   │           │  手机客户端   │
      │ (Windows/    │◄─────────►│ (iOS/        │
      │  Mac/Linux)  │  双向同步   │  Android)    │
      └──────┬──────┘           └──────┬──────┘
             │                          │
      ┌──────▼──────┐           ┌──────▼──────┐
      │  本地 JSON   │           │  本地 SQLite │
      │  (单词库+    │           │  (学习进度+  │
      │   学习进度)   │           │   统计数据)   │
      └─────────────┘           └─────────────┘
```

## 2. 数据存储结构

### 2.1 本地数据文件

| 文件 | 用途 | 大小估算 | 同步策略 |
|------|------|---------|---------|
| `words_database.json` | 6000词完整词库（只读） | ~2MB | 仅首次下载，版本更新时替换 |
| `user_progress.json` | 用户学习进度（高频写入） | ~500KB | 每次学习后自动同步 |
| `study_stats.json` | 学习统计数据（每日汇总） | ~100KB | 每日同步一次 |
| `settings.json` | 用户偏好设置 | ~5KB | 手动/自动同步 |

### 2.2 user_progress.json 结构

```json
{
  "user_id": "xxx",
  "version": 1,
  "last_synced": "2026-07-03T12:00:00Z",
  "words": [
    {
      "word_id": 0,
      "stage": 3,
      "next_review": "2026-07-08",
      "consecutive_hard_count": 0,
      "total_reviews": 5,
      "correct_count": 4,
      "mastery_level": 0.85
    }
  ],
  "daily_stats": {
    "2026-07-01": {
      "new_words_learned": 30,
      "words_reviewed": 120,
      "correct_rate": 0.87,
      "study_minutes": 52
    }
  }
}
```

## 3. 同步方案对比

### 方案A：WebDAV 同步（推荐）

| 特点 | 说明 |
|------|------|
| 成本 | 免费（坚果云/NextCloud 自建） |
| 速度 | 快，差量同步 |
| 可靠性 | 高，HTTP 标准协议 |
| 隐私 | 数据完全自控 |
| 冲突处理 | 基于时间戳的 Last-Write-Wins |

**实现要点**：
```
1. PC端启动时：从 WebDAV 下载 user_progress.json → 合并到本地
2. 每次学习后：加密压缩 → 上传到 WebDAV
3. 手机端启动时：同上流程
4. 冲突检测：比较本地和远程的 last_modified 时间戳，取新版本
```

### 方案B：腾讯云COS / 阿里云OSS

| 特点 | 说明 |
|------|------|
| 成本 | 极低（每月 <1元，2MB × 低频访问） |
| 速度 | 快，CDN 加速 |
| 可靠性 | 极高，99.99% SLA |
| 扩展性 | 可按区域部署 |

### 方案C：iCloud / Google Drive 文件同步

| 特点 | 说明 |
|------|------|
| 成本 | 免费（利用系统自带云盘） |
| 实现难度 | 极低，直接读写云盘目录 |
| 局限性 | 仅限对应生态（iCloud仅苹果、Google Drive需科学上网） |

### 方案D：自建同步服务

适用于高隐私需求，使用：
- Syncthing：P2P 同步，无需中心服务器
- Resilio Sync：基于 BitTorrent 协议

## 4. 推荐实施方案：WebDAV + 本地优先

### 4.1 同步流程

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ 本地操作  │ ──► │ 本地存储  │ ──► │ 同步队列  │
└──────────┘     └──────────┘     └────┬─────┘
                                       │
                              ┌────────▼─────┐
                              │  冲突检测     │
                              │ (timestamp)  │
                              └────────┬─────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
              ┌──────────┐      ┌──────────┐      ┌──────────┐
              │ 本地较新  │      │ 远程较新  │      │ 时间相同  │
              │ → 上传    │      │ → 下载    │      │ → 跳过   │
              └──────────┘      └──────────┘      └──────────┘
```

### 4.2 同步时机

| 触发条件 | 动作 |
|---------|------|
| 每次完成一组复习/新学 | 写入本地 + 标记 dirty flag |
| 应用进入后台（手机） | 检查 dirty flag → 上传 |
| 应用回到前台 | 检查远程更新 → 下载合并 |
| 手动点击同步按钮 | 强制全量同步 |
| 每5分钟定时器 | 静默差量同步 |

### 4.3 冲突解决策略

```
规则1: 同一 word_id 的进度，取 stage 值更大的一方（进度更靠前）
规则2: stage 相同，取 next_review 更晚的一方（已复习过）
规则3: 上述都相同，取 correct_count 更高的一方
规则4: 合并 daily_stats，相同日期取 later study_minutes
```

## 5. 离线模式

- **本地优先原则**：所有操作先写入本地，联网后再同步
- **离线学习**：完全支持，学习进度暂存本地
- **恢复联网**：自动触发同步队列，按时间顺序上传本地变更
- **数据安全**：本地数据每24小时自动备份一次（保留最近7个备份）

## 6. 多设备一致性保障

| 维度 | 策略 |
|------|------|
| 单词库 | 版本号控制，大版本更新需全局替换 |
| 学习进度 | 增量合并，以最晚操作时间为准 |
| 统计数据 | 每日汇总合并，同一天取最大值 |
| 设置 | 每设备独立 + 可选云同步开关 |

## 7. 技术选型建议

| 组件 | 推荐技术 |
|------|---------|
| 前端框架 | Flutter（一套代码，iOS/Android/PC 全平台） |
| 本地存储(手机) | SQLite (sqflite) |
| 本地存储(PC) | JSON 文件 + 内存缓存 |
| HTTP 客户端 | Dio (Flutter) |
| WebDAV 库 | webdav_client (Dart) |
| 状态管理 | Riverpod / Bloc |
| 图表展示 | fl_chart (记忆曲线) |
| 后台同步 | WorkManager (Android) / BGTaskScheduler (iOS) |
*（内容由AI生成，仅供参考）*
