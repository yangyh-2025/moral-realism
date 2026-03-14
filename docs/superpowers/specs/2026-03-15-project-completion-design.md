# 项目补全设计文档

> **创建日期**: 2026-03-15
> **版本**: v1.0
> **状态**: 已批准

---

## 概述

本文档定义了ABM仿真系统项目补全的设计方案，聚焦于完善前端页面、API、测试和文档等真正需要补全的部分。

---

## 背景

项目核心功能（规则校验、Prompt引擎、工作流、后端API、WebSocket）已完成95%。主要缺失内容：

1. 前端页面：事件管理、系统设置
2. 后端API：系统设置路由
3. 测试覆盖：需要提高到80%+
4. 文档完善：API文档、用户手册

---

## 设计方案

### 1. 系统设置API

#### 1.1 文件结构
- `backend/api/settings.py` - 新的路由模块
- `data/settings.json` - 持久化存储文件

#### 1.2 数据模型

```python
class SimulationConfig(BaseModel):
    default_total_rounds: int = 100
    round_interval: float = 1.0
    checkpoint_interval: int = 10

class LLMConfig(BaseModel):
    api_key: str = ""
    model_name: str = "deepseek-chat"
    max_tokens: int = 4096
    temperature: float = 0.7

class SystemConfig(BaseModel):
    realtime_notifications: bool = True
    performance_monitoring: bool = True
    log_level: str = "info"

class Settings(BaseModel):
    simulation: SimulationConfig
    llm: LLMConfig
    system: SystemConfig
```

#### 1.3 API接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/settings` | 获取所有设置 |
| PUT | `/api/settings` | 更新设置 |
| POST | `/api/settings/reset` | 重置为默认值 |
| GET | `/api/settings/{section}` | 获取特定部分配置 |

#### 1.4 持久化机制

- 使用JSON文件存储在 `data/settings.json`
- 首次访问时创建默认配置
- 每次更新后立即写入文件
- 使用文件锁防止并发写入冲突

---

### 2. 系统设置页面

#### 2.1 文件结构
- `frontend/src/pages/SystemSettings.tsx` - 主页面

#### 2.2 Redux集成

创建 `frontend/src/store/slices/settingsSlice.ts`：
```typescript
interface SettingsState {
  settings: Settings;
  isLoading: boolean;
  error: string | null;
}

Actions: fetchSettings, updateSettings, resetSettings
```

#### 2.3 UI布局

**三个主要卡片组**：

1. **仿真参数**
   - 默认仿真轮数 (10-1000)
   - 轮次间隔 (0.1-10秒)
   - 检查点间隔 (1-100轮)

2. **LLM配置**
   - API密钥 (密码输入)
   - 模型名称 (下拉选择)
   - 最大Token数 (1024-8192)
   - 温度参数 (0-2)

3. **系统配置**
   - 启用实时通知 (开关)
   - 启用性能监控 (开关)
   - 日志级别 (下拉选择)

#### 2.4 数据流

```
用户修改表单 → 本地状态更新 → 点击保存
                              ↓
                    dispatch(updateSettings(formData))
                              ↓
                    API调用 PUT /api/settings
                              ↓
                    成功：显示Toast + 更新Redux
                    失败：显示错误Toast
```

---

### 3. 事件管理页面

#### 3.1 文件结构
- `frontend/src/pages/EventManagement.tsx` - 主页面
- `frontend/src/components/events/EventForm.tsx` - 表单组件
- `frontend/src/components/events/EventList.tsx` - 列表组件

#### 3.2 功能特性

**列表展示**：
- 事件名称、类型、描述
- 受影响智能体
- 触发轮次/时间
- 激活状态
- 操作按钮（编辑、删除、激活/停用）

**表单功能**：
- 创建新事件
- 编辑现有事件
- 事件类型选择
- 受影响智能体多选
- 事件效果参数配置

**统计卡片**：
- 总事件数
- 活跃事件数
- 即将发生的事件数

#### 3.3 使用现有Redux

已经存在 `eventsSlice.ts`，包含：
- 事件状态管理
- UserEvent类型
- EventConfig类型

---

### 4. 测试方案

#### 4.1 前端测试 (Vitest)

**系统设置页面测试**：
```typescript
describe('SystemSettings', () => {
  it('渲染所有设置卡片');
  it('表单验证正确工作');
  it('保存按钮调用API');
  it('错误状态正确显示');
});
```

**事件管理页面测试**：
```typescript
describe('EventManagement', () => {
  it('渲染事件列表');
  it('创建事件打开表单');
  it('删除事件确认提示');
  it('切换激活状态');
});
```

**API服务测试**：
```typescript
describe('API Services', () => {
  it('fetchSettings 返回正确数据');
  it('updateSettings 发送正确请求');
});
```

#### 4.2 后端测试 (pytest)

**设置API测试**：
```python
def test_get_settings()
def test_update_settings()
def test_reset_settings()
def test_file_persistence()
def test_concurrent_write_protection()
```

**事件API测试**：
```python
@pytest.mark.asyncio
async def test_create_event()
async def test_trigger_event()
async def test_event_validation()
```

#### 4.3 集成测试

```python
@pytest.mark.asyncio
async def test_settings_workflow():
    """测试完整的设置管理流程"""
    # 获取默认设置
    # 修改部分设置
    # 保存设置
    # 验证持久化
    # 重置设置
    pass
```

---

### 5. 文档更新

#### 5.1 API参考文档

在 `docs/api-reference.md` 中添加：

```markdown
## 系统设置 API

### 获取设置
GET /api/settings

### 更新设置
PUT /api/settings
Content-Type: application/json

{
  "simulation": {...},
  "llm": {...},
  "system": {...}
}
```

#### 5.2 用户手册

在 `docs/user-guide.md` 中添加章节：

```markdown
## 系统设置

通过系统设置页面可以配置：
- 仿真运行参数
- LLM模型设置
- 系统行为选项

## 事件管理

通过事件管理页面可以：
- 创建自定义事件
- 管理事件触发条件
- 查看事件历史
```

---

## 技术栈

### 后端
- FastAPI
- Pydantic (数据验证)
- aiofiles (异步文件操作)

### 前端
- React + TypeScript
- Redux Toolkit
- Tailwind CSS
- Vitest (测试)

---

## 实施顺序

1. **后端设置API** (优先)
   - 创建 `backend/api/settings.py`
   - 实现CRUD接口
   - 添加文件持久化
   - 注册路由

2. **前端设置页面**
   - 创建 `settingsSlice.ts`
   - 实现 `SystemSettings.tsx`
   - 集成API调用

3. **前端事件管理页面**
   - 实现 `EventManagement.tsx`
   - 创建子组件
   - 集成现有API

4. **测试补充**
   - 后端单元测试
   - 前端组件测试
   - 集成测试

5. **文档更新**
   - API文档补充
   - 用户手册完善

---

## 验收标准

### 功能验收
- [ ] 系统设置API所有接口可用
- [ ] 设置正确持久化到JSON文件
- [ ] 系统设置页面所有控件工作正常
- [ ] 事件管理页面完整功能可用
- [ ] 所有测试通过

### 性能验收
- [ ] 设置保存响应时间 < 500ms
- [ ] 事件列表加载 < 1s
- [ ] 测试覆盖率 > 80%

### 文档验收
- [ ] API文档完整
- [ ] 用户手册包含新功能说明
- [ ] 代码注释清晰

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| JSON文件并发写入 | 数据丢失 | 使用文件锁机制 |
| API密钥安全暴露 | 安全问题 | 密码输入框 + 不显示完整密钥 |
| 测试覆盖不足 | 质量问题 | 严格检查覆盖率指标 |
| 文档不一致 | 维护困难 | 文档与代码同步更新 |

---

## 后续优化

1. 考虑使用数据库替代JSON文件存储
2. 添加设置变更历史记录
3. 实现设置导入/导出功能
4. 添加事件模板库
5. 实现事件调度器可视化
