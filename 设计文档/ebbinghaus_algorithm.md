---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 4c863aa1cbdbc6d8f2f9a928a9496dfd_2a55047b769711f1a7da5254006c9bbf
    ReservedCode1: aw9QCAeac/XBAg52UiQBkz8s6v7W8S8hhvOwpdomtHt6p1Imw7ZzZrAdIHkWIS4dgWAINck4nUadwH+rmPIXKoDNT2AEvwnXT683gvJCm6VtZAsIt3eqWQkGBJHKYLYs4N8QbNgR7xzbTw3qML8y+q9whD7y6gOJQaXrRId1GNtH5ntoyFnQIvV0jiA=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 4c863aa1cbdbc6d8f2f9a928a9496dfd_2a55047b769711f1a7da5254006c9bbf
    ReservedCode2: aw9QCAeac/XBAg52UiQBkz8s6v7W8S8hhvOwpdomtHt6p1Imw7ZzZrAdIHkWIS4dgWAINck4nUadwH+rmPIXKoDNT2AEvwnXT683gvJCm6VtZAsIt3eqWQkGBJHKYLYs4N8QbNgR7xzbTw3qML8y+q9whD7y6gOJQaXrRId1GNtH5ntoyFnQIvV0jiA=
---

# 艾宾浩斯记忆算法设计文档

## 1. 算法概述

本算法基于艾宾浩斯遗忘曲线理论，为单词背诵系统提供科学的复习调度机制。核心思想：在记忆即将衰减到临界点之前安排复习，以最少的重复次数达到长期记忆效果。

## 2. 遗忘曲线模型

### 2.1 经典艾宾浩斯遗忘曲线

| 时间间隔 | 记忆保持率 | 遗忘率 |
|---------|-----------|-------|
| 20分钟后 | 58.2% | 41.8% |
| 1小时后 | 44.2% | 55.8% |
| 8小时后 | 35.8% | 64.2% |
| 1天后 | 33.7% | 66.3% |
| 2天后 | 27.8% | 72.2% |
| 6天后 | 25.4% | 74.6% |
| 31天后 | 21.1% | 78.9% |

### 2.2 间隔重复效应

每次成功复习后，记忆保持率曲线的衰减速度都会变慢：

- **第1次复习后**：遗忘速度降低至原始的 60%
- **第2次复习后**：遗忘速度降低至原始的 40%
- **第3次复习后**：遗忘速度降低至原始的 25%
- **第4次复习后**：遗忘速度降低至原始的 15%
- **第5次复习后**：遗忘速度降低至原始的 10%
- **第6次及以上**：进入长期记忆区间，遗忘速度 < 5%

## 3. 复习节点设计

### 3.1 标准复习节点（11级）

| 节点编号 | 间隔时间 | 说明 |
|---------|---------|------|
| R0 | 5分钟 | 首次学习后快速强化，防止短时记忆消退 |
| R1 | 30分钟 | 短时记忆巩固 |
| R2 | 12小时 | 睡眠前/后复习，利用睡眠记忆巩固机制 |
| R3 | 1天 | 第一个关键遗忘点 |
| R4 | 2天 | 短期记忆→中期记忆过渡 |
| R5 | 4天 | 记忆巩固关键期 |
| R6 | 7天 | 周复习节点 |
| R7 | 15天 | 双周强化 |
| R8 | 30天 | 月度复习 |
| R9 | 60天 | 季度巩固 |
| R10 | 120天 | 长期记忆锚定 |

### 3.2 动态调整机制

根据用户的掌握程度反馈，动态调整下一复习间隔：

| 掌握程度 | 反馈 | 间隔调整 | 说明 |
|---------|------|---------|------|
| 熟悉 | 秒级正确回忆 | ×1.5 倍 | 扩大间隔，减少复习频次 |
| 模糊 | 回忆正确但耗时 > 3秒 | ×1.0 倍 | 维持原间隔 |
| 遗忘 | 无法回忆或回忆错误 | ×0.5 倍 | 缩短间隔，加强巩固 |

- **下限保护**：间隔不低于原始间隔的 0.5 倍
- **上限保护**：间隔不超过原始间隔的 3 倍
- **重置机制**：连续 3 次"遗忘"反馈后，该单词重置到 R0

## 4. 每日学习规划算法

### 4.1 新词学习量

```
每日新词量 N_new = min(N_target, N_max)
```

- `N_target`：用户设定目标（默认 30 词/天）
- `N_max`：系统根据当日复习负荷动态上限

### 4.2 当日复习负荷计算

```
当日复习量 = Σ(各节点待复习单词数)
负荷率 = 当日复习量 / 用户时间预算
```

- 若负荷率 > 1.2（即复习量超出时间预算 20%）：自动将次日新词量下调 30%
- 若负荷率 < 0.5（即复习量低于时间预算 50%）：提示用户可增加新词量

### 4.3 每日学习流程

```
1. [复习优先] 按 R0 → R1 → ... → R10 顺序，完成当日全部待复习单词
2. [新词学习] 完成复习后，学习 N_new 个新词
3. [首轮强化] 新学单词的 R0（5分钟后）自动安排
4. [生成明日计划] 根据当日反馈，计算明日各节点的复习列表
```

## 5. 复习调度 Python 伪代码

```python
import datetime
from collections import defaultdict

# 标准复习间隔（天）
STANDARD_INTERVALS = [
    5/1440,    # R0: 5分钟
    30/1440,   # R1: 30分钟
    0.5,       # R2: 12小时
    1,         # R3: 1天
    2,         # R4: 2天
    4,         # R5: 4天
    7,         # R6: 7天
    15,        # R7: 15天
    30,        # R8: 30天
    60,        # R9: 60天
    120,       # R10: 120天
]

def schedule_next_review(word, feedback, current_stage):
    """
    根据反馈动态调整复习间隔
    
    Args:
        word: 单词对象
        feedback: 'easy' | 'normal' | 'hard'
        current_stage: 当前复习阶段 (0-10)
    
    Returns:
        next_review_date: 下次复习日期
        new_stage: 新阶段
    """
    base_interval = STANDARD_INTERVALS[current_stage]
    
    if feedback == 'easy':
        interval_multiplier = 1.5
        new_stage = min(current_stage + 1, 10)
    elif feedback == 'normal':
        interval_multiplier = 1.0
        new_stage = min(current_stage + 1, 10)
    else:  # hard
        interval_multiplier = 0.5
        new_stage = max(current_stage - 1, 0)
    
    # 连续3次hard则重置
    if word['consecutive_hard_count'] >= 3:
        new_stage = 0
        interval_multiplier = 1.0
    
    interval = base_interval * interval_multiplier
    interval = max(base_interval * 0.5, min(base_interval * 3.0, interval))
    
    next_review = datetime.date.today() + datetime.timedelta(days=interval)
    return next_review, new_stage

def generate_daily_plan(word_db, date, new_words_per_day=30):
    """
    生成每日学习计划
    """
    plan = {
        'date': date,
        'reviews': [],      # 当日待复习单词
        'new_words': [],    # 当日新学单词
        'total_review_count': 0,
        'estimated_minutes': 0,
    }
    
    # 1. 收集当日所有待复习单词
    for word in word_db:
        if word['next_review_date'] == date:
            plan['reviews'].append(word)
    
    # 2. 计算复习时间
    total_reviews = len(plan['reviews'])
    review_time = total_reviews * 0.3  # 平均每词30秒复习
    
    # 3. 动态调整新词量
    available_time = 45  # 用户每日45分钟预算（分钟）
    time_for_new = available_time - review_time
    if time_for_new < 10:
        adjusted_new = max(5, new_words_per_day // 2)
    elif time_for_new > 60:
        adjusted_new = new_words_per_day
    else:
        adjusted_new = new_words_per_day
    
    # 4. 从词库取新词（按顺序或按分类）
    new_candidates = [w for w in word_db if w['stage'] == -1]  # 未学习
    plan['new_words'] = new_candidates[:adjusted_new]
    
    plan['total_review_count'] = total_reviews
    plan['estimated_minutes'] = round(total_reviews * 0.3 + adjusted_new * 1.0)
    
    return plan
```

## 6. 记忆保持率预测模型

基于间隔重复效应，预测第 N 次复习后的记忆保持率：

```
BaseRetention(t) = 1 - 0.56 * t^0.06          # 基础遗忘曲线（t为天数）
BoostedRetention(t, n) = 1 - (1 - BaseRetention(t)) * (0.6)^n  # n为完成复习次数
```

### 预测数据点

| 复习轮次 | 1天后 | 7天后 | 30天后 | 120天后 |
|---------|------|------|--------|---------|
| 学完（0次复习） | 33.7% | 25.4% | 21.1% | 18.0% |
| 第1次复习后 | 60.2% | 55.2% | 52.7% | 50.8% |
| 第2次复习后 | 76.1% | 73.1% | 71.6% | 70.5% |
| 第3次复习后 | 85.7% | 83.9% | 83.0% | 82.3% |
| 第4次复习后 | 91.4% | 90.3% | 89.8% | 89.4% |
| 第5次复习后 | 94.9% | 94.2% | 93.9% | 93.6% |
| 第6次复习后（长期） | 97.0% | 96.5% | 96.3% | 96.1% |

## 7. 关键设计决策

1. **复习优先于新学**：每日先完成所有待复习任务，再学新词，确保已学单词不遗忘
2. **动态新词量**：根据当日复习负荷自动调整，避免用户负担过重
3. **三次重置机制**：连续3次"遗忘"反馈后自动重置，避免陷入无效重复
4. **12小时节点**：利用睡眠记忆巩固效应，在睡前和次日早晨安排快速回顾
5. **弹性时间窗口**：每个复习节点允许 ±20% 的时间窗口误差，容错实际生活中的时间偏差
*（内容由AI生成，仅供参考）*
