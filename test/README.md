# 冒烟测试套件

覆盖 moral-ABM 项目的全部后端 API 端点与全部前端页面/按钮。

## 文件结构

```
test/
├── conftest.py             共享 fixtures（httpx Client + 临时项目 + 临时智能体）
├── pytest.ini              pytest 配置
├── test_backend_smoke.py   53 条后端测试（涵盖 8 个 router + 根路径）
├── test_frontend_smoke.py  21 条前端测试（涵盖 7 个页面）
└── README.md
```

## 前置条件

1. **后端**已启动并监听 `127.0.0.1:8000`
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

2. **前端 dev 服务**已启动并监听 `127.0.0.1:3000`
   ```bash
   cd frontend && npm run dev
   ```

3. Python 依赖（已在仓库 venv 内）：`pytest`、`httpx`、`playwright`、`pytest-asyncio`
   - 浏览器：执行过 `python -m playwright install chromium` 一次即可。

如需改 URL：

```bash
set ABM_TEST_BASE_URL=http://127.0.0.1:8000
set ABM_TEST_FRONTEND_URL=http://127.0.0.1:3000
```

## 一键运行

```bash
python -m pytest test/ -v
```

输出格式：

```
test_backend_smoke.py::TestRoot::test_health PASSED
...
====== 74 passed in 42.30s ======
```

仅跑后端：

```bash
python -m pytest test/test_backend_smoke.py -v
```

仅跑前端：

```bash
python -m pytest test/test_frontend_smoke.py -v
```

仅跑某一个 Test 类：

```bash
python -m pytest test/test_backend_smoke.py::TestSimulationControl -v
```

## 后端覆盖（53 用例）

| 测试类 | 端点前缀 | 用例数 |
|--------|---------|-------|
| TestRoot                  | /, /health, /docs, /openapi.json   | 4 |
| TestPresetScene           | /api/v1/preset-scene/...           | 4 |
| TestActionConfig          | /api/v1/action-config/...          | 3 |
| TestCinc                  | /api/v1/cinc/...                   | 7 |
| TestSystemConfig          | /api/v1/system/config              | 2 |
| TestProject               | /api/v1/simulation/project*        | 5 |
| TestAgent                 | /api/v1/simulation/project/{id}/agent* | 5 |
| TestStrategicRelationship | /api/v1/strategic-relationships/...| 5 |
| TestSimulationControl     | /api/v1/simulation/{id}/start...   | 3 |
| TestRoundDetail           | /api/v1/simulation/{id}/round/...  | 2 |
| TestStatistics            | /api/v1/simulation/{id}/stats/...  | 8 |
| TestAnalysis              | /api/v1/analysis/{id}/...          | 5 |

仿真控制测试**只验证状态切换**——不会真的跑 LLM 决策轮次（避免长时间等待与 token 消耗）。

## 前端覆盖（21 用例）

| 测试类 | 路由 | 验证内容 |
|--------|------|---------|
| TestHome                | /          | 欢迎卡 + 预置场景列表 + 详情对话框 + 跳转配置/行为集 |
| TestBehaviorSet         | /behavior  | 20 项行为渲染 + 刷新按钮 |
| TestSystemConfig        | /system    | 表单加载 + 保存按钮 + 重置按钮 |
| TestSimulationConfig    | /config    | 表单加载 + 添加/重置智能体 + 创建项目校验 |
| TestSimulationConsole   | /console   | 控制按钮齐全 + 清空日志 (需要 ?projectId=) |
| TestSimulationResults   | /results   | 5 大图表区域 |
| TestAcademicStatistics  | /statistics| 4 个 Tab 切换 |

每个用例自动捕获浏览器 `pageerror`，发生 JS 异常立即失败。

## 临时数据策略

`smoke_project` fixture 会按 session 创建一个名为 `smoke_test_<时间戳>` 的项目，
session 结束时自动 DELETE。`smoke_project_with_agents` 在其上加 3 个智能体（USA/CHN/FRA 的 2016 年 CINC 数据）并初始化战略关系。

测试不会污染现有项目数据；如果中途中断，残留的 `smoke_test_*` 项目可以通过前端"项目列表"手动删除。

## 已知限制

1. **不跑真实仿真轮次**：`step_simulation` 调 LLM 才能跑真。冒烟阶段只验证 HTTP 调用链通畅；如需端到端，把 `@pytest.mark.slow` 标记的用例打开（目前未标，需要自行添加）。
2. **依赖 CINC 数据库**：测试 fixture 用 USA(ccode=2)/CHN(ccode=710)/FRA(ccode=220)，年份 2016。如果 `data/cinc.csv` 改了年份或去掉这几个国家，需调 `conftest.py` 中的 `agent_payloads`。
3. **前端 `/console` 必须带 `?projectId=`**：组件内置无项目跳转逻辑。
