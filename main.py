import streamlit as st
import logging
from openai import OpenAI

import config
import session_manager

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _save_current_session() -> None:
    """将当前 session_state 保存到磁盘"""
    if not st.session_state.current_session:
        return
    try:
        session_manager.save_session({
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "display_name": st.session_state.display_name,
            "messages": st.session_state.messages,
        })
    except OSError as e:
        st.error(f"保存会话失败：{e}")


def _load_session_to_state(session_name: str) -> None:
    """将指定会话数据加载到 session_state"""
    data = session_manager.load_session_data(session_name)
    if data is None:
        st.warning(f"会话 '{session_name}' 不存在！")
        return
    st.session_state.messages = data.get("messages", [])
    st.session_state.nick_name = data.get("nick_name", config.DEFAULT_NICK_NAME)
    st.session_state.nature = data.get("nature", config.DEFAULT_NATURE)
    st.session_state.display_name = data.get("display_name", "")
    st.session_state.current_session = session_name


def _delete_session_ui(session_name: str) -> None:
    """删除会话并更新 UI 状态"""
    try:
        if st.session_state.current_session == session_name:
            st.session_state.messages = []
            st.session_state.current_session = session_manager.generate_session_name()
        session_manager.delete_session_file(session_name)
        st.rerun()
    except OSError as e:
        st.error(f"删除会话失败：{e}")


# 页面配置项
st.set_page_config(
    page_title="AI角色对话",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

st.title("AI角色对话")

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 初始化昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = config.DEFAULT_NICK_NAME
# 初始化性格设定
if "nature" not in st.session_state:
    st.session_state.nature = config.DEFAULT_NATURE

# 会话标识（每个用户会话只生成一次标识，页面刷新不变）
if "current_session" not in st.session_state:
    st.session_state.current_session = session_manager.generate_session_name()

# 会话显示名称
if "display_name" not in st.session_state:
    st.session_state.display_name = ""


# 展示聊天信息
st.text(f"会话名称: {st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# API Key 前置校验
if not config.DEEPSEEK_API_KEY:
    st.error("请设置环境变量 DEEPSEEK_API_KEY，可在 https://platform.deepseek.com/ 获取")
    st.stop()

# 创建 API 客户端（模块级单例，避免重复初始化）
client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
)

# 左侧的侧边栏 - with: streamlit中上下文管理器
with st.sidebar:
    # 会话信息
    st.subheader("AI控制面板")

    # 新建会话
    if st.button("新建会话", width="stretch", icon="📝"):
        _save_current_session()
        st.session_state.messages = []
        st.session_state.current_session = session_manager.generate_session_name()
        st.session_state.display_name = ""
        _save_current_session()
        st.rerun()

    # 会话重命名
    display_name = st.text_input(
        "会话名称", placeholder="为当前会话命名（可选）",
        value=st.session_state.display_name,
        key="display_name_input",
    )
    if display_name != st.session_state.display_name:
        st.session_state.display_name = display_name
        _save_current_session()

    # 清空 & 导出 按钮
    col_clear, col_export = st.columns(2)
    with col_clear:
        if st.button("清空对话", width="stretch", icon="🗑️"):
            st.session_state.messages = []
            _save_current_session()
            st.rerun()
    with col_export:
        export_data = session_manager.export_session(st.session_state.current_session)
        if export_data:
            st.download_button(
                "导出记录", data=export_data,
                file_name=f"{st.session_state.current_session}.json",
                mime="application/json",
                width="stretch",
                icon="📥",
            )
        else:
            st.button("导出记录", width="stretch", icon="📥", disabled=True)

    st.subheader("角色信息")
    # 昵称输入框
    nick_name = st.text_input(
        "昵称", placeholder="请输入昵称",
        value=st.session_state.nick_name,
        max_chars=config.MAX_NICKNAME_LENGTH,
    )
    if nick_name:
        st.session_state.nick_name = nick_name

    # 性格输入框
    nature = st.text_area(
        "角色设定", placeholder="请输入角色设定",
        value=st.session_state.nature,
        max_chars=config.MAX_NATURE_LENGTH,
    )
    if nature:
        st.session_state.nature = nature

    # 会话历史列表展示模块
    st.text("会话历史")

    # 加载所有已保存的会话列表
    session_list = session_manager.load_session_list()

    # 遍历每个会话，为其创建一行操作区域
    for session in session_list:
        # 获取会话显示名：优先显示自定义名，否则显示时间戳
        session_data = session_manager.load_session_data(session)
        session_label = (
            session_data.get("display_name") if session_data and session_data.get("display_name")
            else session
        )

        col1, col2 = st.columns([4, 1])

        # 左侧列：加载/切换会话
        with col1:
            if st.button(session_label, width="stretch", icon="📄", key=f"load_{session}",
                         type="primary" if session == st.session_state.current_session else "secondary",
                         help=f"会话 ID: {session}"):
                _load_session_to_state(session)
                st.rerun()

        # 右侧列：删除会话
        with col2:
            if st.button("", width="stretch", icon="❌", key=f"delete_{session}"):
                _delete_session_ui(session)

# 系统提示词（从配置加载模板）
system_prompt = config.SYSTEM_PROMPT_TEMPLATE

# 消息输入框
prompt = st.chat_input("请输入你的问题")

if prompt:
    # 输入校验
    if not prompt.strip():
        st.warning("消息不能为空")
        st.stop()
    if len(prompt) > config.MAX_MESSAGE_LENGTH:
        st.warning(f"消息长度不能超过 {config.MAX_MESSAGE_LENGTH} 字符")
        st.stop()

    st.chat_message("user").write(prompt)
    logging.info("用户输入: %s", prompt[:50])
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": system_prompt.format(
                nick_name=st.session_state.nick_name,
                nature=st.session_state.nature,
            )},
            *st.session_state.messages,
        ],
        stream=True,
        reasoning_effort=config.API_REASONING_EFFORT,
        extra_body={"thinking": {"type": "disabled"}},
    )

    # 流式输出 AI 回复
    response_message = st.empty()

    full_response = ""

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存会话信息
    _save_current_session()