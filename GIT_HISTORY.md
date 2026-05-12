# Git 提交历史详细记录

> 本文档记录本仓库（Moral Realism ABM）自创建以来的全部 30 次 Git 提交，按时间顺序排列，详细说明每次提交的改动内容、动机及涉及的关键文件。

## 项目概览

| 主题 | 时间范围 | 系统 | 提交数 |
| ---- | -------- | ---- | ------ |
| 道德现实主义 ABM (Moral Realism ABM) | 2026-04-12 → 2026-05-12 | 基于智能体的国际秩序仿真系统 | 30 |

**技术栈**: FastAPI + SQLAlchemy + Vue3 + Vite + Element Plus + ECharts + Tailwind CSS + Pinia + LLM (OpenAI SDK)

---

## 提交详情

### #1 `cf631a26` Initial commit

- **作者**: yangyh-2025 <yangyh-2025@users.noreply.github.com>
- **时间**: 2026-04-12 16:58:06 +0800
- **变更**: 5 files changed, 749 insertions(+)
- **说明**: 仓库重新初始化，准备搭建 Moral Realism ABM 系统。

---

### #2 `0f3d1e1e` Moral Realism ABM - Complete system refactoring

- **作者**: yangyh-2025
- **时间**: 2026-04-12 22:17:47 +0800
- **变更**: 68 files changed, 10466 insertions(+)
- **核心成果**: 整套国际秩序 Agent-Based Modeling 系统的奠基性提交。
- **架构组成**:
  - **后端**: FastAPI + SQLAlchemy，分层架构（api / core / models / services / config）
  - **前端**: Vue3 + Vite，提供交互式可视化界面
  - **核心引擎**: 采用克莱因(Klein)国力综合方程作为国力计算标准
  - **LLM 驱动**: 通过 OpenAI SDK 支持智能决策
  - **存储**: SQLite 本地数据库
- **关键模块**:
  - `app/core/`：`action_manager.py`、`agent_base.py`、`decision_engine.py`、`klein_equation.py`、`power_update.py`、`interaction_engine.py`、`order_determination.py`、`prompt_templates.py`
  - `app/api/`：`action_config`、`preset_scene`、`simulation`、`statistics`、`system`、`router`
  - `app/models/`：`action_config`、`action_record`、`agent_config`、`agent_power_history`、`follower_relation`、`preset_scene`、`simulation_project`

---

### #3 `88a61572` Add .gitignore to protect sensitive project state

- **作者**: yangyh-2025
- **时间**: 2026-04-13 08:45:54 +0800
- **变更**: 4 files changed, 139 insertions(+), 14 deletions(-)
- **说明**: 完善 `.gitignore`，排除虚拟环境、缓存、OMC 会话状态（`.omc/state/`、`.omc/sessions/`）、数据库文件、日志、环境变量、IDE 与 OS 产物。
- **协作者**: Claude Opus 4.6

---

### #4 `64e2704d` Ignore .omc/project-memory.json for privacy

- **作者**: yangyh-2025
- **时间**: 2026-04-13 08:53:18 +0800
- **变更**: 1 file changed, 1 insertion(+)
- **说明**: `.omc/project-memory.json` 含个人/项目隐私内容，加入 ignore 名单。

---

### #5 `bec00766` 代码重构：移除冗余代码，优化项目结构

- **作者**: yangyh-2025
- **时间**: 2026-04-13 12:42:36 +0800
- **变更**: 35 files changed, 4323 insertions(+), 1207 deletions(-)
- **改动要点**:
  - 重构核心模块：`action_manager`、`agent_base`、`interaction_engine`、`prompt_templates`
  - 简化 API 层逻辑，统一数据处理
  - 整合数据库配置与初始化逻辑
  - 清理前端未使用代码与调试输出
  - 移除根目录废弃文件 `main.py`、`run.py`、`start.bat`
  - 新增 `system_service.py`
  - 添加学术文档对比分析文档

---

### #6 `5d960c52` 重构：简化核心模块代码结构，更新gitignore配置

- **作者**: yangyh-2025
- **时间**: 2026-04-13 15:15:26 +0800
- **变更**: 11 files changed, 67 insertions(+), 124 deletions(-)
- **改动要点**:
  - 简化 `app/config/database.py` 与 `app/core/` 模块
  - 更新 `.gitignore` 忽略 `.claude/`、`.omc/`
  - 优化代码可读性与维护性

---

### #7 `0ed2b2b4` 添加战略目标评估功能：支持LLM驱动的国家目标达成度评估

- **作者**: yangyh-2025
- **时间**: 2026-04-13 21:23:46 +0800
- **变更**: 11 files changed, 933 insertions(+), 57 deletions(-)
- **关键文件**:
  - `app/models/strategic_goal_evaluation.py`（新增数据模型）
  - `app/services/goal_evaluation_service.py`（新增服务）
  - `app/services/simulation_service.py`、`app/services/statistics_service.py`
  - 前端 `AcademicStatistics.vue`、`statistics.js`
- **说明**: 通过 LLM 评估每个国家对其战略目标的达成度，并将评估结果纳入统计面板。

---

### #8 `668af9cf` 功能增强：完善仿真控制系统和用户界面

- **作者**: yangyh-2025
- **时间**: 2026-04-19 21:04:10 +0800
- **变更**: 62 files changed, 5904 insertions(+), 623 deletions(-)
- **改动要点**:
  - 新增日志配置系统 `app/config/logging_config.py` 与 `.env.example`
  - 仿真控制台全面重构：单步执行、暂停/继续、实时状态监控
  - 三列布局：控制面板、日志面板、详情面板
  - 实时轮次详情：追随关系、决策信息、秩序类型
  - 新增测试与工具脚本：`create_missing_rounds.py`、`test_round_api.py`
  - 前端增加状态自动轮询、实时日志展示

---

### #9 `ffc55d43` 功能增强：集成仿真日志管理器和LLM调用追踪

- **作者**: yangyh-2025
- **时间**: 2026-04-20 19:03:48 +0800
- **变更**: 13 files changed, 847 insertions(+), 82 deletions(-)
- **改动要点**:
  - 新增 `app/services/simulation_log_manager.py`，记录 LLM 调用日志
  - `decision_engine` 集成日志管理器
  - 修复 `ActionStageEnum` 导入路径
  - 完善仿真服务与决策验证逻辑
  - 添加 `check_db.py`、`test_api*.py` 等测试工具

---

### #10 `76d44085` 前端优化：改进图表布局和显示效果

- **作者**: yangyh-2025
- **时间**: 2026-04-20 21:53:57 +0800
- **变更**: 2 files changed, 48 insertions(+), 33 deletions(-)
- **改动要点**（针对 `frontend/src/views/SimulationResults.vue`、`AcademicStatistics.vue`）：
  - 每个图表独占一行，避免拥挤
  - 移除 ECharts 内部标题，解决与 el-card 标题重叠
  - 调整图表容器高度（400→600px、大型 500→700px）
  - 优化图例配置（饼图横向、置顶或置底）
  - 调整 grid 边距为图例预留空间
  - 移除容器最大宽度限制（1600px→100%）
  - Tab 切换监听确保图表尺寸正确刷新

---

### #11 `19b487fe` 功能增强：修复智能体关系图谱显示问题

- **作者**: yangyh-2025
- **时间**: 2026-04-20 22:21:37 +0800
- **变更**: 4 files changed, 212 insertions(+), 1 deletion(-)
- **改动文件**: `app/api/statistics.py`、`app/services/statistics_service.py`、`frontend/src/api/statistics.js`、`frontend/src/views/SimulationResults.vue`
- **改动要点**:
  - 后端添加智能体关系图谱数据聚合方法与 API 端点
  - 前端添加关系数据加载与图表更新逻辑
  - 完善图谱可视化（节点分类、连线样式、交互效果）

---

### #12 `e468bbde` 修复：修正智能体关系图谱节点显示值和图表轮次排序

- **作者**: yangyh-2025
- **时间**: 2026-04-21 10:18:06 +0800
- **变更**: 3 files changed, 13 insertions(+), 5 deletions(-)
- **改动要点**:
  - `statistics_service.py`：节点值从 `initial_power` 改为 `initial_total_power`
  - `AcademicStatistics.vue`、`SimulationResults.vue`：修复轮次为数值排序，为 X 轴增加类型与标签

---

### #13 `4862b141` 功能增强：新增国家战略关系属性系统

- **作者**: yangyh-2025
- **时间**: 2026-04-22 14:45:30 +0800
- **变更**: 23 files changed, 777 insertions(+), 209 deletions(-)
- **核心功能**:
  - 新增 `app/models/strategic_relationship.py` 战略关系数据模型，支持五级关系（战争 / 冲突 / 无外交 / 伙伴 / 盟友）
  - 自动初始化大国/超级大国之间的战略关系
  - 决策引擎集成战略关系信息，LLM 决策时可查看各国关系
  - 提供 `app/api/strategic_relationship.py` 管理 API
- **后端变更**:
  - 新增 `StrategicRelationshipEnum` 服务
  - 更新 `AgentInfo` / `InfoPool` 支持战略关系
  - 仿真服务集成关系初始化与数据加载
- **前端变更**: 优化仿真结果展示，更新统计 API 数据结构

---

### #14 `19b2eed2` 功能增强：在智能体决策提示词中增加地理位置和战略关系因素考虑

- **作者**: yangyh-2025
- **时间**: 2026-04-22 15:23:15 +0800
- **变更**: 1 file changed, 9 insertions(+)
- **改动文件**: `app/core/prompt_templates.py`
- **改动要点**:
  - `CORE_RULES_TEMPLATE` 新增第 7 条规则：LLM 决策时必须考虑地理位置与战略关系
  - `OUTPUT_REQUIREMENTS_TEMPLATE` 新增第 6 条规则：成本收益分析包含地理与战略关系维度
  - 明确指示 LLM 在分析中显式说明这些因素对决策的影响
- **协作者**: Claude Opus 4.7

---

### #15 `15e1ca2a` 功能完善：对齐学术文档并完善战略关系系统

- **作者**: yangyh-2025
- **时间**: 2026-04-25 14:47:24 +0800
- **变更**: 29 files changed, 2826 insertions(+), 318 deletions(-)
- **核心改动**:
  - 增强智能体决策提示词模板，明确区分 system / user prompt
  - 完善战略关系系统，支持关系配对规则
  - 前端新增战略关系配置界面与可视化（`SimulationConfig.vue`、`SimulationConsole.vue`、`strategicRelationship.js`）
  - 添加多种测试脚本与工具文件（`check_relations.py`、`fix_vue1-6.py`、`recreate_preset_projects.py`、`test_set_relation.py`、`test_strategic_relationship.py` 等）
  - 导出 `openapi.json`

---

### #16 `6fd8496b` 功能增强：AI行为生成具体执行内容并修复数据访问问题

- **作者**: yangyh-2025
- **时间**: 2026-04-25 23:22:02 +0800
- **变更**: 8 files changed, 26 insertions(+), 15 deletions(-)
- **改动要点**:
  - 提示词模板新增 `action_content` 字段：AI 需生成 50-200 字的具体声明 / 协议内容
  - 统计服务过滤"未判定"类型轮次数据
  - 前端修复 API 响应数据访问路径
  - 行为记录模型 (`action_record.py`) 增加内容字段

---

### #17 `525bc7cf` CINC 国力系统全面替换克莱因方程 ⭐

- **作者**: yangyh-2025
- **时间**: 2026-05-07 11:43:07 +0800
- **变更**: 70 files changed, 67145 insertions(+), 3172 deletions(-)
- **里程碑提交**: 将国力计算体系从克莱因综合国力方程全面替换为 CINC (Composite Index of National Capability)，引入 COW NMC v6.0 数据库（1816-2016 年，217 国）。
- **核心变更**:
  - **新增 CINC 核心模块**:
    - `app/core/cinc_data_loader.py`
    - `app/core/cinc_calculator.py`
    - `app/core/cinc_power_update.py`
  - **数据模型改造**: 移除克莱因 5 项指标 (c/e/m/s/w)，新增 CINC 6 项底层指标 (`milex`、`milper`、`irst`、`pec`、`tpop`、`upop`)
  - **国力计算机制**: 从绝对分值改为比例值 (0-1)，层级按仿真体系内相对排名动态判定
  - **国力更新机制**: 行为 → 底层指标变化 → 全局重算 CINC（含被动变化）→ 全局重算层级
  - **20 项标准行为** 新增 `primary_indicator` / `secondary_indicator` 字段，映射到 CINC 底层指标
  - **核心层全面适配**: `agent_base`、`action_manager`、`interaction_engine`、`order_determination`、`prompt_templates`、`decision_engine`、`decision_validation`
  - **服务层全面适配**: `agent_service`、`simulation_service`、`statistics_service`、`goal_evaluation`、`relationship_evolution`、`simulation_log_manager`
  - **预设场景重构**: 替换为基于真实 CINC 数据的三个历史场景：
    - 一战前欧洲（1913 年，19 国）
    - 二战前欧洲（1938 年,28 国）
    - 冷战前欧洲（1946 年，25 国）
  - **新增 CINC 数据查询 API**: `/cinc/countries`、`/years`、`/data`、`/by-year`
  - **前端全面适配**: `SimulationConfig.vue` 移除克莱因输入改为 CINC 国家选择器，所有国力显示改为 CINC 指数
  - **删除旧模块**: `klein_equation.py`、`power_update.py` 及临时测试脚本
  - **数据资产入库**: `cinc/NMC-60-abridged/`、`cinc/NMC-60-wsupplementary/` CSV/DTA/TXT 数据文件 + NMC 文档 PDF
  - 重建数据库 schema，清理代码中全部克莱因相关引用

---

### #18 `0bfd1ea3` 修复：CINC层级动态变化导致的leader_type硬校验失败问题

- **作者**: yangyh-2025
- **时间**: 2026-05-07 17:02:35 +0800
- **变更**: 2 files changed, 26 insertions(+), 12 deletions(-)
- **问题**:
  - CINC 层级基于体系内相对排名动态判定（前 10% 超级大国、10-30% 大国等）
  - 批量创建 agent 时每次新增都会触发 CINC 重算，前几个 agent 的层级会临时不准确
  - `agent_service.add_agent/update_agent` 中的 `leader_type` 硬校验在排名未稳定时误判，抛出 `ValueError → HTTP 500`
- **修复内容**:
  - `agent_service.add_agent`：去除硬校验，改为 `logger.warning`
  - `agent_service.update_agent`：同上修复
  - `agent_service.delete_agent`：增加 `_recalculate_all_cincs` 调用
  - 添加 `loguru.logger` 导入
  - `action_config.py`：响应模型 `ActionConfigResponse` 增加 `primary_indicator/secondary_indicator` 字段
- **验证**: 三个预设场景全部能正常创建；agent CRUD 后 CINC 自动重算且总和 = 1.0；行为配置 API 返回完整 CINC 指标映射字段。

---

### #19 `b62c69f7` 修复：前端LLM配置无法生效，仿真启动后无响应问题

- **作者**: yangyh-2025
- **时间**: 2026-05-07 17:30:40 +0800
- **变更**: 2 files changed, 158 insertions(+), 64 deletions(-)
- **问题**:
  - 前端"系统配置"页面修改 LLM 模型 / API key / API base 后，只更新内存字典
  - 既不持久化到数据库，也不通知 `LLMService` 刷新客户端
  - `LLMService` 单例只从 `.env` 与环境变量读取一次
  - 结果：用户配置变更全部无效，仿真启动后大量 LLM 调用失败
- **修复内容**:
  - `system_service.py`：
    - 改造 `SystemConfigService` 使配置持久化到 `system_config` 表
    - 启动时从数据库懒加载，覆盖环境变量默认值
    - `update_system_config` 更新内存后写库，并通过 `LLMConfig.update_config` 同步刷新 `LLMService` 单例
    - 新增 `sync_to_llm_service()` 供启动钩子主动同步
  - `main.py`：应用启动 `lifespan` 在 `init_default_data` 后调用 `sync_to_llm_service`

---

### #20 `7c820a3b` 修复：自定义项目创建时战略关系全部丢失变为无外交关系的bug

- **作者**: yangyh-2025
- **时间**: 2026-05-07 21:02:36 +0800
- **变更**: 1 file changed, 83 insertions(+), 49 deletions(-)
- **改动文件**: `frontend/src/views/SimulationConfig.vue`
- **问题**: 自定义配置页新增 agent 无 `agentId` 字段，关系矩阵以 `agentId` 作 key 时全为 `undefined`，所有关系都写到 `relationshipMatrix[undefined][undefined]`，提交时 `idMapping[parseInt('undefined')]=NaN`，最终用户配置完全丢失。
- **修复**:
  - 关系矩阵改用 `agents` 数组索引 (i, j) 作稳定 key
  - 模板 v-for 增加 `(targetAgent, targetIndex)`，`#default` 增加 `$index`
  - `getRelation` / `canSetRelation` / `setRelation` 改签名为 `(sourceIndex, targetIndex)`
  - `canSetRelation` 通过 `agents.value[idx]` 直接取 agent
  - `setRelation`：项目未创建时仅写本地 matrix；已创建时再用 agentId 同步后端
  - `loadRelationships`：后端 agentId-based 响应转换为 index-based
  - `saveRelations`：matrix index 反查 agentId 再调后端 API

---

### #21 `f7ed69bf` 修复：reset_simulation会清空用户配置的战略关系

- **作者**: yangyh-2025
- **时间**: 2026-05-07 21:17:35 +0800
- **变更**: 1 file changed, 5 insertions(+), 7 deletions(-)
- **改动文件**: `app/services/simulation_service.py`
- **问题**: `reset_simulation` 调用 `initialize_relationships(skip_existing=False)`，将所有战略关系强制重置为"无外交"，丢失用户配置/场景预设。
- **设计修正**:
  - 战略关系属于"项目配置"，非"运行数据"
  - `reset_simulation` 只应清除运行数据（行为记录 / 轮次 / 追随关系 / CINC 历史 / 当前 CINC）
  - 如需重置关系，由 `/strategic-relationships/{project_id}/initialize` 单独触发
- **修复**: 移除重置战略关系代码块，加注释说明设计意图。

---

### #22 `9874edf7` 性能优化：决策生成从串行改为并发执行

- **作者**: yangyh-2025
- **时间**: 2026-05-07 21:30:26 +0800
- **变更**: 1 file changed, 80 insertions(+), 72 deletions(-)
- **改动文件**: `app/services/simulation_service.py`
- **问题**: `_generate_decisions` 串行 LLM 调用，19 个 agent × 主动+响应 = 38 次调用，每次约 18 秒，单轮约 11 分钟，50 轮约 9 小时。
- **优化**:
  - 使用 `asyncio.Semaphore` 限制并发上限（系统配置 `simulation_concurrency`，1-20）
  - 每个 agent 决策提取为内部协程 `_decide_one_agent`
  - 异常隔离：单 agent 失败不影响其他
  - `asyncio.gather` 并发等待
- **预期效果**:
  - `concurrency=5`：单轮约 144s（10× 加速）
  - `concurrency=10`：单轮约 72s（15× 加速）

---

### #23 `2bec964c` 增强：仿真进度可视化日志，便于追踪运行状态

- **作者**: yangyh-2025
- **时间**: 2026-05-07 21:59:11 +0800
- **变更**: 1 file changed, 53 insertions(+), 24 deletions(-)
- **改动文件**: `app/services/simulation_service.py`
- **改进内容**:
  1. 轮次开始 / 结束加双横线框装饰区分每轮
  2. 决策阶段显示进度计数 `[ 7/19] ✓ R1 主动决策 | 强国甲(ID:77) → 表达合作意向->ID78; 协商/磋商->ID79`
  3. 阶段标记编号 `[阶段3/6]`、`[阶段4/6]`
  4. 轮次结束统计行为数、秩序类型与耗时
  5. 决策摘要：成功决策时显示前 3 个行为
- **日志路径**:
  - 控制台: uvicorn 启动终端的 stdout
  - 文件: `logs/abm_2026-MM-DD.log`（可 `tail -f`）
  - 错误专用: `logs/abm_error_2026-MM-DD.log`

---

### #24 `fa1d3b1d` 修复：agent-relations API 500错误（Pydantic类型校验失败）

- **作者**: yangyh-2025
- **时间**: 2026-05-07 22:11:31 +0800
- **变更**: 1 file changed, 3 insertions(+), 1 deletion(-)
- **改动文件**: `app/services/statistics_service.py`
- **根因**: `get_agent_relations` 计算 `symbolSize = max(20, min(80, cinc_val * 500))` 返回 float，但 `AgentRelationNode` 模型声明 `symbolSize: int`；Pydantic v2 严格模式下 float 无法自动转 int → 校验失败 → 500。
- **修复**: 在 `statistics_service.get_agent_relations` 中显式 `int()` 转换 `symbolSize`。
- **验证**: 所有 stats API 全部 HTTP 200。

---

### #25 `ff9770e0` 优化LLM提示词设计：提升决策准确度、行为一致性与评估可信度

- **作者**: yangyh-2025
- **时间**: 2026-05-08 11:40:48 +0800
- **变更**: 7 files changed, 1167 insertions(+), 70 deletions(-)
- **核心改进**:
  1. 修复 Windows GBK 终端 Unicode 编码错误（✓→[OK]、→→-> 等）
  2. 决策提示词增加 CINC 指数通俗解释、6 项国力指标全称、实力层级判定标准
  3. 成本收益分析对齐实际国力变化值（行为列表标注确切数值，禁止 LLM 编造）
  4. 重试提示词增强：补充有效 `action_id/action_name/agent_id` 白名单
  5. JSON 示例类型修复：`action_id` 从字符串占位符改为真实整数
  6. LLM 温度参数从 0.7 降至 0.35，提升决策确定性
  7. 追随决策增加领导类型差异化规则（4 种类型不同追随偏好）
  8. 决策 User Prompt 增加自动生成的态势摘要（排名 / 盟友 / 对手 / 上一轮行为 / 国力趋势）
  9. 历史行为按关系对聚合展示（合作类 / 对抗类次数统计 + 最近 5 条详细记录）
  10. 战略目标评估增加 Few-shot 评分锚点（高 / 中 / 低分 3 个示例）
  11. 战略关系演变增加量化评估标准（升级 / 降级阈值、国力显著增长定义）
  12. 关系演变增加历史连续性约束（变化后稳定期、防关系回弹）
  13. 关系演变增加上一轮变化记录到 User Prompt
  14. 关系演变明确第三方影响机制（盟友传导效应的具体压力等级）
- **新增文档**: `docs/智能体提示词设计说明.md`（汇总 4 个智能体的提示词设计与仿真流程）

---

### #26 `8e9c5e50` 实现预设场景数据库初始化与多模块优化

- **作者**: yangyh-2025
- **时间**: 2026-05-09 11:47:39 +0800
- **变更**: 10 files changed, 259 insertions(+), 117 deletions(-)
- **后端改动**:
  - `database`: 实现 `_init_preset_scenes`，将 3 个 CINC 历史预设场景写入数据库
  - `scene_service`: 预设场景查询优先走数据库，无数据时回退硬编码兜底
  - `agent_base`: 移除 `leader_type` 空验证器简化逻辑
  - `decision_engine`: 修复 `_format_history_for_prompt` 支持全局聚合（agent_id=None），修复 retry 时的 NameError
  - `cinc_power_update`: 国力更新计算调整
  - `prompt_templates`: 进一步优化决策准确度
  - `action_record`: 行为记录模型微调
  - `simulation_service`: 国力变化率改用对数变化率，避免极小起点放大效应
- **前端**: `SimulationResults` 仿真结果展示优化
- **文档**: 同步更新 `docs/智能体提示词设计说明.md`

---

### #27 `2010ae25` 完善：对齐学术文档 + 新增后验分析 API + 修复仿真控制 bug + 新增冒烟测试套件

- **作者**: yangyh-2025
- **时间**: 2026-05-09 20:21:00 +0800
- **变更**: 28 files changed, 2429 insertions(+), 1602 deletions(-)
- **1. 对齐学术文档**:
  - 重构 `prompt_templates`，移除超出学术文档要求的额外约束，使用完整描述
  - 决策校验删除 Tier 3 合规校验（含已损坏的 `standard_action` 引用），仅保留 Tier 1 行为白名单 + Tier 2 基础格式校验
  - `decision_engine` 强化情境摘要、冲突升级轨迹、实力矩阵等上下文
  - `interaction_engine`、`agent_base`、`action_manager` 同步调整字段使用
  - `relationship_evolution_service`、`goal_evaluation_service` 沿同一路径调整为统一信息池接入
- **2. 新增后验分析 API**（`/api/v1/analysis/{project_id}/...`）:
  - `behavior`：行为模式分析
  - `power`：国力动态变化
  - `order`：国际秩序演变
  - `leader`：领导类型与行为关联
  - `report`：综合报告
  - 在 `router.py` 中挂载
- **3. 修复仿真控制接口 500 错误**:
  - `step_simulation` 改为 `log_manager` 可选，未传则按 `project_id` 自建
  - `resume_simulation` 重启后台任务时显式创建 `log_manager`，避免 TypeError → 500
- **4. 新增前后端冒烟测试套件 `test/`**:
  - `test_backend_smoke.py`：53 用例，覆盖 8 个 router 全部端点
  - `test_frontend_smoke.py`：21 用例（Playwright 驱动 Chromium），覆盖 7 个页面与关键按钮交互
  - `conftest.py`：会话级 fixtures 自动建/删测试项目与智能体
  - `README.md`：运行步骤、依赖与覆盖矩阵
- **5. 文档与杂项**:
  - 删除过时的 3 份 docs：修改计划、学术文档对比、技术方案
  - 更新 `docs/智能体提示词设计说明.md`、`SimulationResults.vue`
  - `.gitignore` 增加 `data/` 排除运行时 SQLite 与备份

---

### #28 `89ce2a1a` 增强追随决策提示词：注入战略关系总览与候选人评估，优化LLM日志与前端可视化

- **作者**: yangyh-2025
- **时间**: 2026-05-10 12:47:25 +0800
- **变更**: 9 files changed, 583 insertions(+), 71 deletions(-)
- **改动要点**:
  - 新增 `build_personal_relations_summary`：为每个 agent 构建自我视角的战略关系分组总览
  - 新增 `build_candidates_evaluation`：按 voter 视角预先核对候选人的关系警示与双向互动统计
  - 更新追随决策通用规则与提示词模板，强化"先核对战略关系再决策"约束
  - `simulation_service`：参与决策和投票决策中注入个人关系总览和候选人评估
  - 战略关系格式化：从平铺改为按类型聚合（`[战争:135,136][盟友:134]`），超过 5 国中立关系折叠
  - LLM 日志 API 扩展为汇总 4 类日志（interaction / following / goal_evaluation / relationship_evolution）
  - `action_content` 校验：长度限制调整为 50-300 字，空内容明确报错
  - 前端 `SimulationConsole`：LLM 响应按类别打标，支持按响应形态智能渲染
  - 修复 `relationship_evolution_service` 中多余的 `await`
  - 更新测试 README 与提示词设计文档

---

### #29 `9abf6827` 新增历史任务页面与LLM调用日志系统，重构项目列表API，优化仿真控制

- **作者**: yangyh-2025
- **时间**: 2026-05-12 14:45:42 +0800
- **变更**: 30 files changed, 2189 insertions(+), 228 deletions(-)
- **后端改动**:
  - 新增 LLM 调用日志模块: `llm_call_log` 模型 + `/llm-calls` API + 历史日志回填脚本 (`app/scripts/backfill_llm_logs.py`)
  - 项目列表 API 重构为分页 / 筛选 / 排序，支持 `keyword/scene_source/status` 多维查询
  - `SimulationProject` 模型新增 `started_at/completed_at/duration_seconds` 字段
  - 项目导出 ZIP 打包功能（配置 / 智能体 / 历史回合 / 动作记录等）
  - 仿真控制新增 `_stop_flags` 快速终止机制，多个停止点检查保证响应性
  - 完善 `goal_evaluation` / `relationship_evolution` / `statistics` 等服务计算逻辑
  - `prompt_templates` 与 `decision_engine` 文案与行为对齐学术文档
- **前端改动**:
  - 新增 `SimulationHistory.vue` "历史任务"页面：筛选 / 分页 / 排序 / 状态分类标签；表格首列展示项目唯一 ID（短码 + 悬停完整 + 点击复制）；内置导出 ZIP / 查看 LLM 日志 / 删除等操作
  - 新增 `LLMCallLog.vue` "LLM 调用记录"页面：按类型 / 轮次 / agent 多维检索调用记录
  - 路由新增 `/history` 与 `/llm-calls`，顶部导航增加"历史任务"入口
  - `SimulationConsole` / `SimulationResults` / `SystemConfig` 配合后端字段与流程更新

---

### #30 `ee58d345` feat: 新增智能体邻居关系模块，重构前端分析页面，增强仿真决策引擎

- **作者**: yangyh-2025
- **时间**: 2026-05-12 16:57:38 +0800
- **变更**: 71 files changed, 7390 insertions(+), 2041 deletions(-)
- **后端改动**:
  - 新增智能体邻居关系 API / 模型 / 服务：`agent_neighbor` 系列
  - 新增地理数据模块 `app/core/geography_data.py`
  - 增强 `scene_service`（+863 行）与决策引擎（+223 行）
  - 优化提示词模板、战略关系服务与目标评估服务
  - 新增 `app/scripts/cleanup_duplicate_relationships.py` 清理重复关系
  - 数据库配置扩展
- **前端改动（重大重构）**:
  - **统一分析页面**: 移除 `SimulationResults`、`AcademicStatistics`，统一为 `Analysis.vue` + `analysis/` 下的 Tab 组件（`BehaviorTab`、`CincTab`、`ExportTab`、`GoalEvalTab`、`GrowthRateTab`、`OverviewTab`）
  - **新增 Pinia store**: `store/chart.js`、`store/project.js`
  - **新增组合式函数**: `composables/useChartTheme.js`、`useProject.js`、`useSimulationStatus.js`、`useStats.js`
  - **新增组件库**:
    - 图表组件: `BarChart`、`BaseChart`、`LineChart`、`NetworkChart`、`PieChart`、`StackedAreaChart`、`chart-theme.js`
    - 布局组件: `AppShell`、`EmptyState`、`PageHeader`、`ProjectPicker`、`Sidebar`
    - 原子组件: `Card`、`DataTable`、`Metric`、`Section`、`Tag`
  - **接入 Tailwind CSS**: `tailwind.config.js`、`postcss.config.js`、`styles/tailwind.css`、`styles/tokens.css`、`styles/element-overrides.css`、`styles/global.css`
  - **路由重构**: 兼容旧路径重定向
  - **清理调试文件**: `debug.html`、`simple-test.html`、`test.html`、`test.vue` 等
- **测试改动**:
  - 增强前后端冒烟测试
  - 新增 E2E 集成测试 `test/test_e2e_integration.py`

---

## 演进总结

按照功能线索可以将整个项目的演进梳理为几条主线：

| 主线 | 关键提交 | 演进描述 |
| ---- | -------- | -------- |
| 系统奠基 | #2 | FastAPI + Vue3 + SQLAlchemy + LLM 完整分层架构 |
| 国力模型 | #2 → #17 | 克莱因方程 → CINC 综合国家能力指数（COW NMC v6.0 真实历史数据） |
| 仿真控制 | #8、#22、#23、#27、#29 | 单步/暂停/继续/重置/快停 + 串行 → 并发决策 + 进度可视化 |
| 战略关系 | #13、#14、#15、#20、#21、#28 | 五级关系模型 + 提示词集成 + 前端配置 + 持久化 + 候选评估 |
| 提示词设计 | #5、#7、#16、#25、#26、#27、#28 | 模板拆分 system/user + Few-shot 锚点 + 量化标准 + 关系总览 |
| LLM 调用追踪 | #9、#28、#29 | 日志管理器 → 4 类日志汇总 → `/llm-calls` API + 历史回填 |
| 数据后验分析 | #27、#30 | `/analysis/*` 五大维度 API + 前端 `Analysis.vue` 统一分析页 |
| 测试体系 | #27、#30 | 53 后端用例 + 21 前端用例（Playwright） + E2E 集成测试 |
| 前端体系 | #10、#11、#12、#30 | ECharts 优化 → Tailwind + 组件库 + Pinia + Composables 完整重构 |
| 历史与回归 | #18、#19、#20、#21、#24 | CINC 动态层级、LLM 配置持久化、关系矩阵 key 修复、Pydantic 校验等关键 bug fix |

---

## 文档生成说明

- **数据来源**: `git log --reverse` + `git show --name-only --stat`
- **统计口径**: 文件改动数与增删行数取自 `--shortstat`
- **生成时间**: 2026-05-12
- **当前 HEAD**: `ee58d345` (master)
