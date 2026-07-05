---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 4c863aa1cbdbc6d8f2f9a928a9496dfd_6fe0fa84781d11f1b3d35254007bceed
    ReservedCode1: 536BjIw7jL2cFgCTJsf8PrjbgwFaHtCzIWEUmiVoDNrBsrBn7KueYC8dn4bmN2vVM2M7gq7qCGx5WJI0D/rdr8AZl8M12Ck8rigulsAdQG9j/ApqxPMmI6tMfRVwioDvsFqsFvW9k4zyOCp168vdaraCqbgLC5mUHGSdUGxaY8uwI20AHbXmtNZwkhA=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 4c863aa1cbdbc6d8f2f9a928a9496dfd_6fe0fa84781d11f1b3d35254007bceed
    ReservedCode2: 536BjIw7jL2cFgCTJsf8PrjbgwFaHtCzIWEUmiVoDNrBsrBn7KueYC8dn4bmN2vVM2M7gq7qCGx5WJI0D/rdr8AZl8M12Ck8rigulsAdQG9j/ApqxPMmI6tMfRVwioDvsFqsFvW9k4zyOCp168vdaraCqbgLC5mUHGSdUGxaY8uwI20AHbXmtNZwkhA=
---

# 新能源行业英语单词学习工具包

## 快速开始

双击 `spaced_repetition_app.html` 即可使用，无需安装任何软件。

浏览器要求：Chrome / Edge / Firefox 最新版。

## 文件说明

### 主程序
| 文件 | 说明 |
|------|------|
| `spaced_repetition_app.html` | 完整的背单词应用（5571词），含学习/拼写测试/随身听/统计/多账户 |

### 词库导出（导入到其他 App）
| 文件 | 说明 |
|------|------|
| `词库导出/anki_import.csv` | Anki 导入格式 |
| `词库导出/momo_import.txt` | 墨墨背单词导入格式 |
| `词库导出/word_bank.xlsx` | Excel 格式词库 |
| `词库导出/words_database.json` | 完整 JSON 词库（含例句/音标/分类） |
| `词库导出/study_tracker.xlsx` | 学习打卡记录表 |

### 分类词库（按领域）
| 文件 | 领域 |
|------|------|
| `分类词库/wind_energy.txt` | 风电 |
| `分类词库/energy_storage.txt` | 储能 |
| `分类词库/new_energy.txt` | 新能源综合 |
| `分类词库/sales_oral.txt` | 销售口语 |
| `分类词库/product_manager.txt` | 产品经理 |
| `分类词库/business_meeting.txt` | 商务会议 |

### 设计文档
- `设计文档/ebbinghaus_algorithm.md`：艾宾浩斯记忆算法说明
- `设计文档/study_plan.md`：学习计划建议
- `设计文档/sync_solution.md`：多设备同步方案

## 分发方式

- **直接发送**：将整个 `NewEnergyVocab` 文件夹压缩为 zip，对方解压后双击 HTML 即可使用
- **局域网共享**：在本机运行 `python -m http.server 8080`，手机/其他电脑浏览器访问 `http://你的IP:8080/spaced_repetition_app.html`

## 注意事项

- 主应用依赖 Chart.js CDN（图表组件），需联网加载；其余功能完全离线可用
- 学习进度存储在浏览器本地（localStorage），更换浏览器需重新注册
- 多设备账号同步需自行部署后端（见 `设计文档/sync_solution.md`）
*（内容由AI生成，仅供参考）*
