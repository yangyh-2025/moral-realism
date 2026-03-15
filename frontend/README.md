# 前端开发指南

## 技术栈

- React 18
- TypeScript 5
- Redux Toolkit
- Vite 5
- Tailwind CSS 3
- Plotly.js

## 开发环境设置

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

## 项目结构

```
frontend/src/
├── components/     # React组件
│   ├── charts/     # 图表组件
│   └── ui/         # UI组件库
├── pages/         # 页面组件
├── services/      # API服务
├── store/        # Redux状态管理
├── types/        # TypeScript类型定义
├── utils/        # 工具函数
├── App.tsx       # 主应用
└── main.tsx       # 入口文件
```

## 开发规范

### 组件命名

- 使用PascalCase命名组件文件
- 导出默认组件

### 状态管理

- 使用Redux Toolkit
- 每个功能模块创建一个slice

### 样式规范

- 使用Tailwind CSS类
- 遵循BEM命名约定（自定义CSS）

## API调用示例

```typescript
import { simulationAPI } from '../services/simulation';

// 启动仿真
const response = await simulationAPI.start({
  total_rounds: 100,
  round_duration: 6,
  random_event_prob: 0.1
});

// 获取状态
const state = await simulationAPI.getState();
```

---

*文档生成时间: 2026-03-15*
