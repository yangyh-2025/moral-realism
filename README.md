# 道义现实主义 LLM 驱动社会模拟仿真系统
# Moral Realism LLM-Driven Agent-Based Modeling System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-orange.svg)](pyproject.toml)

## 项目简介 / Project Introduction

本项目是基于阎学通教授《道义、政治领导和国际秩序》理论构建的LLM驱动的智能体社会模拟仿真系统。

This project is an LLM-driven agent-based modeling system built based on Professor Yan Xuetong's theory from "Moral, Political Leadership, and International Order".

### 核心理论 / Core Theory

- **双变量逻辑 / Dual-Variable Logic**: 实力地位 + 政治领导类型 / Material Capability + Political Leadership Type
- **四类国际领导类型 / Four Types of International Leadership**:
  - 王道型 / Wangdao (Moral-Based Leadership)
  - 霸权型 / Hegemon (Interest-Based Leadership)
  - 强权型 / Qiangquan (Coercive Leadership)
  - 昏庸型 / Hunyong (Incompetent Leadership)

## 核心功能 / Core Features

- ✅ 四类国际领导类型智能体模拟 / Four types of international leadership agent simulation
- ✅ 多智能体互动系统 / Multi-agent interaction system
- ✅ 实时指标监测与可视化 / Real-time metrics monitoring and visualization
- ✅ 仿真报告生成 / Simulation report generation
- ✅ 检查点保存与恢复 / Checkpoint save and restore
- ✅ 性能监控与优化 / Performance monitoring and optimization
- ✅ 交互式Dashboard / Interactive Dashboard

## 安装说明 / Installation

### 环境要求 / Requirements

- Python 3.10+
- pip 或 poetry / pip or poetry

### 安装步骤 / Installation Steps

1. **克隆仓库 / Clone Repository**
```bash
git clone https://github.com/yangyh-2025/moral-realism-abm.git
cd moral-realism-abm
```

2. **创建虚拟环境 / Create Virtual Environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **安装依赖 / Install Dependencies**
```bash
pip install -e .
# Or with development dependencies
pip install -e ".[dev]"
```

4. **配置环境变量 / Configure Environment Variables**

创建 `.env` 文件并配置以下变量：
Create a `.env` file and configure the following variables:

```env
# LLM API Configuration / LLM API配置
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_MODEL=Qwen/Qwen2.5-72B-Instruct

# LLM Parameters / LLM参数
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
LLM_TIMEOUT=60

# Simulation Configuration / 仿真配置
MAX_ROUNDS=100
EVENT_PROBABILITY=0.1
CHECKPOINT_INTERVAL=10
```

## 使用指南 / Usage Guide

### 命令行运行 / Command Line

运行完整仿真：
Run complete simulation:

```bash
python -m src.main
```

运行特定配置的仿真：
Run simulation with specific configuration:

```bash
python -m src.main --config config/simulation_config.yaml
```

### Dashboard使用 / Dashboard Usage

启动交互式Dashboard：
Launch interactive dashboard:

```bash
python run_dashboard.py
```

Dashboard功能 / Dashboard Features:
- 实时仿真状态监控 / Real-time simulation status monitoring
- 智能体行为可视化 / Agent behavior visualization
- 指标趋势图表 / Metrics trend charts
- 交互式控制面板 / Interactive control panel

### 配置说明 / Configuration

仿真配置文件示例：
Example simulation configuration file (`config/simulation_config.yaml`):

```yaml
simulation:
  max_rounds: 100
  checkpoint_interval: 10
  event_probability: 0.1

agents:
  - id: "gp1"
    name: "Great Power 1"
    name_zh: "大国1"
    type: "great_power"
    leadership_type: "wangdao"
    capability:
      tier: "T1_GREAT_POWER"

  - id: "gp2"
    name: "Great Power 2"
    name_zh: "大国2"
    type: "great_power"
    leadership_type: "hegemon"
    capability:
      tier: "T1_GREAT_POWER"
```

## 项目结构 / Project Structure

```
moral-realism-abm/
├── src/                      # 源代码 / Source code
│   ├── core/                  # 核心模块 / Core modules
│   │   └── llm_engine.py     # LLM引擎 / LLM engine
│   ├── models/                # 数据模型 / Data models
│   │   ├── agent.py          # 智能体模型 / Agent models
│   │   ├── leadership_type.py # 领导类型 / Leadership types
│   │   └── capability.py     # 能力模型 / Capability models
│   ├── agents/                # 智能体实现 / Agent implementations
│   │   ├── great_power_agent.py
│   │   ├── small_state_agent.py
│   │   └── controller_agent.py
│   ├── environment/           # 环境模块 / Environment modules
│   │   ├── rule_environment.py
│   │   ├── dynamic_environment.py
│   │   └── static_environment.py
│   ├── interaction/           # 互动系统 / Interaction system
│   │   ├── interaction_manager.py
│   │   ├── behavior_selector.py
│   │   └── response_generator.py
│   ├── metrics/               # 指标系统 / Metrics system
│   │   ├── calculator.py
│   │   ├── storage.py
│   │   └── analyzer.py
│   ├── workflow/              # 工作流 / Workflow
│   │   ├── simulation_controller.py
│   │   ├── round_executor.py
│   │   ├── state_manager.py
│   │   ├── performance_monitor.py
│   │   └── workflow.py
│   ├── visualization/         # 可视化 / Visualization
│   │   ├── dashboard.py
│   │   ├── panels.py
│   │   └── report_generator.py
│   └── prompts/              # Prompt模板 / Prompt templates
│       ├── base_prompt.py
│       ├── leadership_prompts.py
│       ├── behavior_prompts.py
│       └── response_prompts.py
├── tests/                    # 测试文件 / Test files
│   ├── test_phase1.py        # Phase 1: Core models
│   ├── test_phase2.py        # Phase 2: Agents
│   ├── test_phase3.py        # Phase 3: Environment
│   ├── test_phase4.py        # Phase 4: Interactions
│   ├── test_phase5.py        # Phase 5: Metrics
│   ├── test_phase6.py        # Phase 6: Workflow
│   ├── test_phase7.py        # Phase 7: Visualization
│   └── test_phase9.py        # Phase 9: Integration
├── config/                   # 配置文件 / Configuration files
├── data/                     # 数据目录 / Data directory
├── run_dashboard.py          # Dashboard启动脚本 / Dashboard launcher
├── pyproject.toml           # 项目配置 / Project configuration
└── README.md                # 项目文档 / Project documentation
```

## 技术架构 / Technical Architecture

### 系统架构图 / System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Dashboard UI                         │
│          (Streamlit Visualization Layer)              │
└─────────────────────────┬─────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────┐
│              Workflow Orchestrator                    │
│              (SimulationController)                    │
└──┬───────────────┬───────────────┬──────────────────┘
   │               │               │
┌──▼───┐      ┌──▼───┐      ┌──▼────────────┐
│ Agents│      │Environment│   │   Metrics      │
│       │      │           │   │   System      │
│ Wangdao│      │ Rules     │   │ Calculator    │
│ Hegemon │      │ Dynamic   │   │ Storage       │
│ Qiangquan│     │ Static    │   │ Analyzer      │
│ Hunyong │      │           │   │               │
└───┬───┘      └─────┬─────┘      └───────┬───────┘
    │                │                   │
┌───▼────────────────▼───────────────────▼───────┐
│          LLM Decision Engine                    │
│          (OpenAI-Compatible API)                │
└─────────────────────────────────────────────────┘
```

### 核心组件 / Core Components

1. **智能体层 / Agent Layer**
   - GreatPowerAgent: 大国智能体 / Great power agent
   - SmallStateAgent: 小国智能体 / Small state agent
   - ControllerAgent: 控制智能体 / Controller agent

2. **环境层 / Environment Layer**
   - RuleEnvironment: 规则环境 / Rule-based environment
   - DynamicEnvironment: 动态环境 / Dynamic event environment
   - StaticEnvironment: 静态环境 / Static parameter environment

3. **互动层 / Interaction Layer**
   - InteractionManager: 互动管理器 / Interaction manager
   - BehaviorSelector: 行为选择器 / Behavior selector
   - ResponseGenerator: 响应生成器 / Response generator

4. **指标层 / Metrics Layer**
   - MetricsCalculator: 指标计算器 / Metrics calculator
   - DataStorage: 数据存储 / Data storage
   - MetricsAnalyzer: 指标分析器 / Metrics analyzer

5. **工作流层 / Workflow Layer**
   - SimulationController: 仿真控制器 / Simulation controller
   - StateManager: 状态管理器 / State manager
   - PerformanceMonitor: 性能监控器 / Performance monitor

## 开发指南 / Development Guide

### 代码规范 / Code Standards

- 使用Black进行代码格式化 / Use Black for code formatting
  ```bash
  black src/ tests/
  ```

- 使用mypy进行类型检查 / Use mypy for type checking
  ```bash
  mypy src/
  ```

### 测试运行 / Running Tests

运行所有测试：
Run all tests:

```bash
pytest tests/ -v
```

运行特定阶段的测试：
Run specific phase tests:

```bash
pytest tests/test_phase1.py -v
pytest tests/test_phase9.py -v
```

查看测试覆盖率：
View test coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

### 贡献指南 / Contributing

1. Fork 本仓库 / Fork this repository
2. 创建特性分支 / Create feature branch (`git checkout -b feature/AmazingFeature`)
3. 提交更改 / Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 / Push to branch (`git push origin feature/AmazingFeature`)
5. 创建Pull Request / Create Pull Request

### 发布说明 / Release Notes

**Version 0.3.0** (Current)
- 完整的9阶段开发 / Complete 9-phase development
- 完整的测试覆盖 / Complete test coverage
- 交互式Dashboard / Interactive dashboard
- 完善的文档 / Comprehensive documentation

## 许可证 / License

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 参考文献 / References

- 阎学通. 《道义、政治领导和国际秩序》. 北京大学出版社, 2016.
- Yan Xuetong. *Moral, Political Leadership, and International Order*. Peking University Press, 2016.

## 联系方式 / Contact

- **GitHub**: https://github.com/yangyh-2025/moral-realism-abm
- **Email**: yangyuhang2667@163.com

## 致谢 / Acknowledgments

感谢所有为本项目做出贡献的开发者和研究者。

Thanks to all developers and researchers who have contributed to this project.

---

**注意 / Note**: 本项目仅用于学术研究和教育目的。
**Note**: This project is for academic research and educational purposes only.
