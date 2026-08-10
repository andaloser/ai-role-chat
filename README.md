# AI 角色对话 🤖

基于 Streamlit 和 DeepSeek API 的 AI 角色对话应用，支持自定义角色设定和多会话管理。

## 功能

- 🎭 **自定义角色**：自由设定 AI 的昵称和性格，打造专属对话伙伴
- 💬 **多会话管理**：支持创建、切换、删除多个聊天会话
- 🔄 **会话持久化**：聊天记录自动保存到本地，下次打开仍可继续
- 🌊 **流式输出**：AI 回复实时逐字显示，体验更流畅

## 技术栈

- [Streamlit](https://streamlit.io/) - Web UI 框架
- [DeepSeek API](https://api.deepseek.com) - AI 大模型
- [OpenAI SDK](https://github.com/openai/openai-python) - API 调用

## 快速开始

### 1. 安装依赖

```bash
pip install streamlit openai
```

### 2. 设置 API Key

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="你的DeepSeek API Key"

# macOS / Linux
export DEEPSEEK_API_KEY="你的DeepSeek API Key"
```

> 在 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取 API Key。

### 3. 运行

```bash
streamlit run 1.py
```

浏览器会自动打开 `http://localhost:8501`，即可开始对话。

## 使用说明

- **侧边栏** → 设置 AI 昵称和角色性格（如"活泼开朗的姑娘"、"严谨的理工男"）
- **新建会话** → 保存当前对话并开启新聊天
- **会话历史** → 点击会话名切换，点击 ❌ 删除
- **底部输入框** → 输入消息开始对话
