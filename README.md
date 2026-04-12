# Moral Realism ABM

大语言模型驱动的国际关系主体基建模（ABM）研究平台。基于阎学通道义现实主义理论，利用 LLM Agent 仿真国际秩序演变趋势。

## 项目结构

```
├── app/                    # 后端（FastAPI + SQLAlchemy）
│   ├── api/                # REST API 端点
│   ├── core/               # 仿真核心引擎
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑层
│   ├── config/             # 数据库与日志配置
│   └── scripts/            # 数据维护脚本
├── frontend/               # 前端（Vue3 + Vite + ECharts）
│   └── src/
│       ├── views/          # 页面组件
│       ├── components/     # 共享组件
│       ├── api/            # API 客户端
│       ├── store/          # Pinia 状态管理
│       └── composables/    # 组合式函数
├── cinc/                   # CINC v6.0 国力数据库
├── data/
│   ├── history/            # 三个历史场景地面真值
│   ├── experiment_data.json    # 全部实验轮次级数据
│   └── organized_data.json     # 聚合整理实验数据
├── start.py                # 一键启动脚本
└── requirements.txt        # Python 依赖
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

### 安装与启动

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. 安装后端依赖
pip install -r requirements.txt

# 4. 安装前端依赖
cd frontend && npm install && cd ..

# 5. 配置 LLM API
cp .env.example .env
# 编辑 .env 填入你的 LLM Provider 信息

# 6. 一键启动
python start.py
```

浏览器访问 `http://localhost:8000`；交互式 API 文档位于 `http://localhost:8000/docs`。

### 使用流程

1. **选择预设场景** — 从一战前（1913）、二战前（1938）、冷战后（1946）三个历史场景中选择，或自行创建自定义场景
2. **配置智能体** — 按需调整各国初始属性、领导类型与战略关系
3. **启动仿真** — 支持自动运行、单步调试、暂停/继续
4. **分析结果** — 在统一分析页查看追随格局、秩序类型、主权尊重、战略目标达成度等多维度可视化

## 核心机制

- **国力模型**：基于 CINC (Composite Index of National Capability) v6.0，使用 1816–2016 年 217 国历史数据
- **决策引擎**：20 项标准互动行为集，LLM 驱动各国生成主动/响应行为
- **秩序判定**：根据主权尊重比例与领导追随结构，自动判定每轮国际秩序类型
- **战略关系**：五级关系模型（盟友/伙伴/无外交/冲突/战争），影响决策约束
- **追随机制**：LLM 基于综合国力、历史互动、战略关系做出追随决策

## 数据

| 文件 | 说明 |
|------|------|
| `data/history/scene*_prewar_*.json` | 三个历史场景的地面真值（各国逐轮追随目标） |
| `data/experiment_data.json` | 24 个实验场景完整轮次级数据 |
| `data/organized_data.json` | 按场景聚合的秩序类型与追随格局数据 |
| `cinc/NMC-60-*/` | COW NMC v6.0 CINC 数据库（CSV/DTA/TXT） |

## 引用

如在本研究中使用了本系统或数据，请引用：

```bibtex
@software{yang2026moralabm,
  author = {Yang, Yuhang},
  title = {Moral Realism ABM: LLM-Driven Agent-Based Model of International Order},
  year = {2026},
  url = {https://github.com/yangyh-2025/moral-realism}
}
```

## 许可

GNU General Public License v3.0 — 详见 [LICENSE](LICENSE)。
