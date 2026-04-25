# 修复全量信息池历史行为记录缺失字段

## Context

用户发现全量信息池中没有包含所有国家过往决策的完整信息。经检查，`ActionRecord` 模型包含完整的决策字段（`initiator_power_change`, `target_power_change`, `decision_detail`），但 `_get_action_history()` 方法返回的数据字典中缺少这些字段。

这导致智能体在决策时无法获取历史的国力变化和决策详情信息。

## 实施计划

### 修改文件

**文件：** `app/services/simulation_service.py`

**位置：** 第 627-636 行，`_get_action_history()` 方法的返回列表

### 修改内容

在返回的字典中添加缺失的字段：

```python
return [
    {
        'round_num': r.round_num,
        'source_agent_id': r.source_agent_id,
        'target_agent_id': r.target_agent_id,
        'action_name': r.action_name,
        'action_category': r.action_category,
        'respect_sov': r.respect_sov,
        'initiator_power_change': r.initiator_power_change,  # 新增
        'target_power_change': r.target_power_change,          # 新增
        'decision_detail': r.decision_detail                   # 新增
    }
    for r in records
]
```

### 验证方式

1. 启动仿真项目并运行至少一轮
2. 检查 `InfoPool` 中 `history_action_records` 是否包含完整字段
3. 查看日志或调试输出确认数据完整性
