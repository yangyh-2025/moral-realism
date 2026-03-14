# 故障排除

本指南帮助您诊断和解决使用道义现实主义社会模拟仿真系统时可能遇到的问题。

## 目录

1. [安装问题](#安装问题)
2. [配置问题](#配置问题)
3. [运行时问题](#运行时问题)
4. [性能问题](#性能问题)
5. [网络问题](#网络问题)
6. [数据问题](#数据问题)
7. [前端问题](#前端问题)

---

## 安装问题

### Python 版本不兼容

**症状**:
```
ModuleNotFoundError: No module named 'typing_extensions'
```

**解决方案**:

1. 检查 Python 版本：
```bash
python --version
# 应该是 3.9 或更高版本
```

2. 如果版本过低，安装新版 Python：
- Windows: 从 [python.org](https://python.org) 下载
- macOS: 使用 Homebrew: `brew install python@3.11`
- Linux: 使用包管理器或 pyenv

### 依赖安装失败

**症状**:
```
ERROR: Could not find a version that satisfies the requirement
```

**解决方案**:

1. 升级 pip：
```bash
python -m pip install --upgrade pip
```

2. 使用镜像源（中国用户）：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. 手动安装问题包：
```bash
pip install --no-cache-dir package-name
```

### 虚拟环境问题

**症状**:
```
Command 'venv' not found
```

**解决方案**:

确保已安装 python3-venv：
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# 重新创建虚拟环境
python -m venv venv
```

---

## 配置问题

### API 密钥错误

**症状**:
```
Error: API key not found or invalid
```

**解决方案**:

1. 检查 `.env` 文件：
```bash
cat .env
```

2. 确认 API 密钥格式正确：
```bash
# .env 文件应该包含：
MORAL_REALISM_LLM_API_KEY=sk-your-actual-api-key
```

3. 验证 API 密钥在 SiliconFlow 平台有效

4. 如果使用配置文件，检查 `config/config.yaml`

### 配置文件语法错误

**症状**:
```
YAMLError: while parsing a flow mapping
```

**解决方案**:

1. 验证 YAML 语法：
```bash
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

2. 检查缩进（YAML 使用空格，不要用 Tab）

3. 使用在线 YAML 验证器

### 数据库路径错误

**症状**:
```
FileNotFoundError: database directory not found
```

**解决方案**:

1. 创建数据目录：
```bash
mkdir -p data
```

2. 检查配置中的路径：
```bash
# .env 文件
MORAL_REALISM_DATABASE_PATH=./data/database.db
```

3. 确保有写入权限

---

## 运行时问题

### 仿真无法启动

**症状**:
```
Error: Cannot start simulation
```

**诊断步骤**:

1. 检查后端是否运行：
```bash
curl http://localhost:8000/health
```

2. 检查仿真配置：
```bash
curl http://localhost:8000/api/simulation/list
```

3. 查看后端日志：
```bash
tail -f logs/app.log
```

**常见原因**:

- 智能体配置错误
- API 密钥无效
- 数据库未初始化

### 智能体决策失败

**症状**:
```
LLMError: Decision generation failed
```

**解决方案**:

1. 检查 API 配额：
```bash
curl -X POST https://api.siliconflow.cn/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-ai/DeepSeek-V3.2","messages":[{"role":"user","content":"test"}]}'
```

2. 增加 LLM 请求超时时间：
```yaml
# config.yaml
llm:
  timeout: 60  # 增加到 60 秒
```

3. 启用重试机制：
```yaml
llm:
  retry_attempts: 5
  retry_delay: 2
```

### 仿真卡住/无响应

**症状**:
仿真长时间处于运行状态，但没有进度更新

**解决方案**:

1. 检查 CPU 和内存使用：
```bash
top  # Linux/macOS
taskmgr  # Windows
```

2. 查看后端进程状态：
```bash
ps aux | grep python
```

3. 重启后端服务：
```bash
# 停止进程
pkill -f "backend.main"

# 重新启动
python -m backend.main
```

### WebSocket 连接失败

**症状**:
前端无法连接到 WebSocket

**解决方案**:

1. 检查 WebSocket 端点：
```javascript
// 浏览器控制台
const ws = new WebSocket('ws://localhost:8000/api/ws/test');
ws.onopen = () => console.log('连接成功');
ws.onerror = (err) => console.error('连接失败:', err);
```

2. 检查防火墙设置

3. 确认 CORS 配置正确：
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 性能问题

### 响应速度慢

**症状**:
API 请求响应时间过长（> 5 秒）

**解决方案**:

1. 使用多个 API 密钥并行请求：
```yaml
llm:
  api_keys:
    - key1
    - key2
    - key3
```

2. 减少每次请求的 token 数：
```yaml
llm:
  max_tokens: 2048  # 降低 token 数
```

3. 启用缓存：
```yaml
cache:
  enabled: true
  max_size: 1000
```

### 内存占用过高

**症状**:
系统内存使用持续增长

**解决方案**:

1. 减少仿真轮次：
```yaml
simulation:
  total_rounds: 50  # 从 100 减少到 50
```

2. 启用自动保存：
```yaml
storage:
  auto_save_interval: 5
  clear_memory_after_save: true
```

3. 定期重启服务

### CPU 使用率 100%

**症状**:
CPU 占用持续 100%

**解决方案**:

1. 限制并发请求数：
```yaml
performance:
  max_concurrent_requests: 5  # 降低并发数
```

2. 使用异步模式：
```bash
uvicorn backend.main:app --workers 2
```

3. 优化智能体数量

---

## 网络问题

### API 请求超时

**症状**:
```
TimeoutError: Request timeout
```

**解决方案**:

1. 检查网络连接：
```bash
ping api.siliconflow.cn
```

2. 增加超时设置：
```yaml
llm:
  timeout: 120  # 增加到 2 分钟
```

3. 使用代理（如果需要）：
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### CORS 错误

**症状**:
浏览器控制台显示 CORS 错误

**解决方案**:

检查并更新 CORS 配置：
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 数据问题

### 数据库锁定

**症状**:
```
DatabaseError: database is locked
```

**解决方案**:

1. 检查是否有其他进程占用数据库：
```bash
lsof data/database.db  # Linux/macOS
```

2. 使用 WAL 模式：
```bash
sqlite3 data/database.db "PRAGMA journal_mode=WAL;"
```

3. 重启服务

### 数据损坏

**症状**:
```
DatabaseError: database disk image is malformed
```

**解决方案**:

1. 尝试恢复数据库：
```bash
sqlite3 data/database.db ".recover" | sqlite3 recovered.db
```

2. 使用备份恢复：
```bash
cp backups/latest_backup.db data/database.db
```

3. 重新初始化数据库（会丢失数据）

---

## 前端问题

### 前端构建失败

**症状**:
```
npm run build fails with errors
```

**解决方案**:

1. 清理依赖并重新安装：
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

2. 检查 Node.js 版本：
```bash
node --version  # 应该是 16+
```

3. 检查 TypeScript 错误：
```bash
npm run type-check
```

### 组件渲染错误

**症状**:
白屏或 React 错误边界显示

**解决方案**:

1. 查看浏览器控制台错误

2. 检查 API 返回数据格式

3. 验证前端环境变量：
```bash
cat frontend/.env
```

### WebSocket 断开重连

**症状**:
WebSocket 连接频繁断开

**解决方案**:

实现自动重连机制：
```javascript
function connectWebSocket(simulationId) {
  const ws = new WebSocket(`ws://localhost:8000/api/ws/${simulationId}`);

  ws.onclose = () => {
    console.log('连接关闭，5秒后重连...');
    setTimeout(() => connectWebSocket(simulationId), 5000);
  };

  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error);
  };

  return ws;
}
```

---

## 日志分析

### 查看实时日志

```bash
# 查看所有日志
tail -f logs/app.log

# 只看错误日志
tail -f logs/app.log | grep ERROR

# 只看特定模块日志
tail -f logs/app.log | grep "simulation"
```

### 日志级别配置

```yaml
# config.yaml
logging:
  level: DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## 获取帮助

如果以上解决方案无法解决问题：

1. **收集诊断信息**:
```bash
# 系统信息
uname -a
python --version
node --version

# 应用状态
curl http://localhost:8000/health
curl http://localhost:8000/api/simulation/list
```

2. **查看完整日志**:
```bash
cat logs/app.log | tail -100
```

3. **提交问题报告**:
   - 包含系统信息
   - 附上错误日志
   - 描述复现步骤
   - 说明预期行为 vs 实际行为

---

*最后更新: 2026-03-14*
