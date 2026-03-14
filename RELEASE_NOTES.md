# 版本 1.7.0 发布说明

**发布日期**: 2026-03-14
**版本**: 1.7.0
**分支**: phase3-agent-f

## 概述

道义现实主义仿真系统(DRS) v1.7.0 是一个完整的仿真平台，实现了从Prompt模板引擎到前端可视化的完整功能链路。本版本标志着系统的核心功能已经完备，可用于道义现实主义理论的研究和仿真实验。

---

## 主要更新

### 核心功能

#### 1. Prompt模板引擎
- ✅ 支持16种模板类型
- ✅ 变量注入和替换
- ✅ 模板缓存机制
- ✅ 版本控制支持

#### 2. 环境仿真引擎
- ✅ 周期性事件系统
- ✅ 优先级事件管理
- ✅ 影响传播链
- ✅ 时间步进控制

#### 3. 智能体决策系统
- ✅ 决策缓存机制
- ✅ 优先级决策系统
- ✅ 学习和记忆机制
- ✅ 多智能体协作

#### 4. 观测迭代层
- ✅ 指标计算引擎
- ✅ 因果追溯分析
- ✅ 实验管理功能
- ✅ 数据采集优化

#### 5. 后端API
- ✅ WebSocket实时通信
- ✅ 完整的CRUD操作
- ✅ 任务队列管理
- ✅ API认证与授权

#### 6. 前端应用
- ✅ React + TypeScript
- ✅ Redux状态管理
- ✅ 可视化组件库
- ✅ 响应式设计

### 性能优化

- 并发决策处理，提升多智能体场景下的计算效率
- 多级缓存机制，减少重复计算
- 数据库查询优化，使用索引和预编译语句
- 前端组件懒加载，减少初始加载时间
- WebSocket连接池管理，优化并发连接

### 安全加固

- API密钥认证机制
- 请求输入验证和过滤
- 请求速率限制，防止滥用
- CORS配置，控制跨域访问

### 用户体验

- 错误边界组件，提供友好的错误提示
- 性能监控工具，实时了解系统性能
- 国际化支持，中文/英文切换
- 响应式设计，支持移动端、平板、桌面和大屏

---

## 安装

### Docker 部署（推荐）

```bash
# 克隆仓库
git clone <repository-url>
cd drs-system

# 使用Docker Compose启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动安装

**后端环境**:
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
cp .env.example .env
# 编辑 .env 文件，设置数据库连接等配置

# 初始化数据库
python scripts/init_db.py

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端环境**:
```bash
# 安装依赖
cd frontend
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

---

## 配置说明

### 环境变量

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/drs

# API配置
API_KEY=your-secret-api-key
API_RATE_LIMIT=100

# WebSocket配置
WS_PORT=8001

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 前端配置
FRONTEND_URL=http://localhost:5173
```

---

## 已知问题

1. **WebSocket重连**: 当网络不稳定时，WebSocket连接可能断开，需要客户端配合实现自动重连机制。
2. **内存泄漏**: 长时间运行可能存在轻微的内存泄漏，建议定期重启服务。
3. **移动端图表**: 部分复杂图表在移动端设备上渲染性能可能不佳。

---

## 升级指南

从 v1.6.0 升级到 v1.7.0：

1. 备份数据库
2. 拉取最新代码：`git pull`
3. 运行数据库迁移脚本
4. 更新依赖：`pip install -r requirements.txt`
5. 重启服务

---

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 联系方式

- 项目主页: [GitHub Repository](https://github.com/yangyh-2025/drs-system)
- 问题反馈: [Issues](https://github.com/yangyh-2025/drs-system/issues)
- 邮箱: yangyuhang@163.com

---

## 致谢

感谢所有为道义现实主义仿真系统做出贡献的开发者和研究人员。

---

## 下一步计划

- [ ] 添加更多可视化组件类型
- [ ] 优化移动端体验
- [ ] 增加更多测试用例
- [ ] 实现数据导入导出功能
- [ ] 添加仿真结果对比功能
- [ ] 支持自定义模板上传
- [ ] 实现分布式仿真
