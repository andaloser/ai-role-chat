import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json


# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 保存会话信息
def save_session():
    if not st.session_state.current_session:
        return

    session_data = {
        "nick_name": st.session_state.nick_name,
        "nature": st.session_state.nature,
        "current_session": st.session_state.current_session,
        "messages": st.session_state.messages
    }

    # 如果 sessions 目录不存在，则创建
    if not os.path.exists("sessions"):
        os.mkdir("sessions")
    # 保存会话信息
    with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)


# 加载会话列表信息
def load_sessions():
    session_list = []
    # session文件夹下的目录
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    return session_list


# 加载指定的会话信息
def load_session(session_name):
    try:
        # 检查会话文件是否存在
        if os.path.exists(f"sessions/{session_name}.json"):
            # 读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                # 将会话数据恢复到 session_state 中
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败！")


# 删除会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            if st.session_state.current_session == session_name:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
            os.remove(f"sessions/{session_name}.json")
            st.rerun()
        else:
            st.warning("会话不存在！")

    except Exception:
        st.error("删除会话失败！")


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
    st.session_state.nick_name = "路人甲"
# 初始化性格设定
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的姑娘"

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()
# 检查 st.session_state 中是否不存在 "current_session" 这个键
# 如果不存在，就将当前时间格式化为 年-月-日_时-分-秒 的字符串，存入 session_state
# 这样每个用户会话只会生成一次标识，页面刷新也不会改变


# 展示聊天信息
st.text(f"会话名称: {st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # else:
    #     st.chat_message("assistant").write(message["content"])

# 创建客户端（放在外面只初始化一次）
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# 左侧的侧边栏 - with: streamlit中上下文管理器
with st.sidebar:
    # 会话信息
    st.subheader("AI控制面板")

    # 新建会话
    # st.button这个按钮会重新从头执行一遍代码渲染页面后才执行里面的指令，这时页面已经渲染完成了。再清除聊天信息不显示在页面
    if st.button("新建会话", width="stretch", icon="📝"):
        # 1.保存当前会话信息
        save_session()

        # 2.创建新会话
        if st.session_state.messages:  # 如果聊天消息非空，就创建新的对话
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()  # 重新运行代码

    st.subheader("角色信息")
    # 昵称输入框
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    # 性格输入框
    nature = st.text_area("角色设定", placeholder="请输入角色设定", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

    # 会话历史列表展示模块
    st.text("会话历史")

    # 加载所有已保存的会话列表
    # load_sessions() 返回会话名称的列表
    session_list = load_sessions()

    # 遍历每个会话，为其创建一行操作区域
    for session in session_list:
        # 将当前行分为两列：左侧占4份宽度（显示会话名），右侧占1份宽度（删除按钮）
        # 比例 [4, 1] 意味着左侧按钮较宽，右侧删除按钮较窄
        col1, col2 = st.columns([4, 1])

        # ---------- 左侧列：加载/切换会话 ----------
        with col1:
            # 创建加载按钮，点击后可加载对应会话的聊天记录
            # - session: 按钮上显示的文本（即会话名称）
            # - width="stretch": 按钮宽度自适应填满列宽
            # - icon="📄": 按钮左侧显示文档图标，增强可视化识别
            # - key=f"load_{session}": 唯一标识符，Streamlit 要求每个交互组件必须有唯一 key
            #   使用 "load_" 前缀区分加载类按钮，避免与其他组件 key 冲突
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}",
                         type="primary" if session == st.session_state.current_session else "secondary"):
                # 加载指定的会话信息
                load_session(session)
                st.rerun()

        # ---------- 右侧列：删除会话 ----------
        with col2:
            # 创建删除按钮，点击后删除对应会话
            # - "": 按钮文本为空，仅通过图标识别，保持界面简洁
            # - width="stretch": 按钮宽度自适应填满列宽
            # - icon="❌": 红色叉号图标，直观表示删除操作
            # - key=f"delete_{session}": 唯一标识符，"delete_" 前缀与加载按钮区分
            if st.button("", width="stretch", icon="❌", key=f"delete_{session}"):
                delete_session(session)

# 系统提示词
system_prompt = """
代入昵称%s：
规则：
    1. 每次只回1条消息
    2. 禁止任何场景或状态描述性文字
    3. 匹配用户的语言
    4. 回复简短，像微信聊天一样
    7. 回复的内容，要充分体现性格特征
    角色设定%s
你必须严格遵守上述规则来回复用户。
"""

# 消息输入框
prompt = st.chat_input("请输入你的问题")

if prompt:  # 只在用户输入后才执行
    # 显示用户消息
    st.chat_message("user").write(prompt)
    print("调用AI大模型，提示词：", prompt)
    # 保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用AI大模型（移到 if 块内部）
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages,
            # {"role": "user", "content": prompt},
        ],
        stream=True,
        reasoning_effort="low",
        extra_body={"thinking": {"type": "disabled"}}
    )

    # 输出大模型返回的结果（非流式输出的解析方式）
    # print("<---------- 大模型返回的结果：", response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 输出大模型返回的结果（流式输出的解析方式）
    response_message = st.empty()  # 创建一个空的组件，用于展示大模型返回的结果

    full_response = ""

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存会话信息
    save_session()