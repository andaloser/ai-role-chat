# AI 角色对话 
基于 Streamlit 和 DeepSeek API 的 AI 角色扮演对话应用。支持自定义角色人设、多会话管理、流式对话、对话导出。

## 功能特性

**自定义角色** — 自由定义 AI 昵称和性格人设，打造专属对话伙伴
**多会话管理** — 创建、切换、重命名、清空、删除会话，支持导出聊天记录
**流式输出** — 基于 SSE 实时逐字显示 AI 回复
**本地持久化** — JSON 文件存储，无需外部数据库
**输入校验** — 消息长度限制、空消息拦截、API Key 前置检查

## 技术栈
| 组件 | 技术选型 | 说明 |
|------|---------|------|
| Web UI | Streamlit | 纯 Python，零前端代码 |
| AI 模型 | DeepSeek v4 | 通过 OpenAI 兼容 SDK 调用 |
| 数据存储 | 本地 JSON | 轻量零依赖，适合单机应用 |
| 测试 | pytest | 14 个单元测试，覆盖所有 CRUD 操作 |

##  项目结构

```
ai-role-chat/
├── main.py              # Streamlit UI 入口，仅负责页面渲染
├── config.py            # 配置常量集中管理（API、提示词、限制等）
├── session_manager.py   # 会话持久化逻辑层（纯函数，可脱离 UI 测试）
├── requirements.txt     # 依赖锁定
├── tests/
│   └── test_session_manager.py  # 会话管理单元测试
└── sessions/            # 会话数据目录（gitignore）
```

### 架构设计要点

- **UI 与逻辑分离**：`session_manager.py` 为纯函数模块，不依赖 Streamlit，可独立测试。`main.py` 仅负责 UI 渲染和状态管理。
- **配置集中管理**：所有硬编码项（API 端点、模型名、提示词模板、长度限制）统一在 `config.py` 中维护。
- **防御性编程**：API Key 前置校验、精确的异常捕获（非裸 `except Exception`）、日志记录所有错误操作。

### 环境要求

- Python 3.9+
- [DeepSeek API Key](https://platform.deepseek.com/)

### 安装

```bash
git clone https://github.com/andaloser/ai-role-chat.git
cd ai-role-chat
pip install -r requirements.txt
```

### 配置

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-api-key"

# macOS / Linux
export DEEPSEEK_API_KEY="your-api-key"
```

### 运行

```bash
streamlit run main.py
```
浏览器访问 `http://localhost:8501` 即可开始对话。

## 测试

```bash
python -m pytest tests/ -v
```

##  使用说明

| 操作 | 位置 | 说明 |
|------|------|------|
| 设置角色 | 侧边栏 → 角色信息 | 修改昵称和性格，即时生效 |
| 新建会话 | 侧边栏 → 新建会话 | 保存当前对话后创建空白会话 |
| 重命名会话 | 侧边栏 → 会话名称 | 为当前会话起一个有意义的名字 |
| 加载历史 | 侧边栏 → 会话历史 | 点击会话名切换，当前会话高亮 |
| 删除会话 | 侧边栏 → ❌ | 删除后会创建新的空白会话 |
| 清空对话 | 侧边栏 → 清空对话 | 保留会话，仅清除消息 |
| 导出记录 | 侧边栏 → 导出记录 | 下载当前会话为 JSON 文件 |
| 发送消息 | 底部输入框 | 回车发送 |
