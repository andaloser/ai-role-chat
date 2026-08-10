"""会话持久化管理模块

提供会话数据的 CRUD 操作，所有函数均为纯函数，
不依赖 Streamlit session_state，可直接进行单元测试。
"""
import os
import json
import logging
from datetime import datetime

import config

logger = logging.getLogger(__name__)


def generate_session_name() -> str:
    """生成基于当前时间的唯一会话标识"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _get_session_path(session_name: str, sessions_dir: str = config.SESSIONS_DIR) -> str:
    """获取会话文件的完整路径"""
    return os.path.join(sessions_dir, f"{session_name}.json")


def _ensure_sessions_dir(sessions_dir: str = config.SESSIONS_DIR) -> None:
    """确保会话存储目录存在"""
    os.makedirs(sessions_dir, exist_ok=True)


def save_session(
    session_data: dict,
    sessions_dir: str = config.SESSIONS_DIR,
) -> None:
    """保存会话数据到 JSON 文件

    Args:
        session_data: 包含 nick_name, nature, current_session, messages 的字典
        sessions_dir: 会话存储目录，默认使用配置中的 SESSIONS_DIR
    """
    session_name = session_data.get("current_session")
    if not session_name:
        return

    try:
        _ensure_sessions_dir(sessions_dir)
        file_path = _get_session_path(session_name, sessions_dir)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error("保存会话失败 [%s]: %s", session_name, e)
        raise


def load_session_list(sessions_dir: str = config.SESSIONS_DIR) -> list[str]:
    """加载所有已保存的会话名称列表

    Args:
        sessions_dir: 会话存储目录

    Returns:
        按修改时间倒序排列的会话名称列表
    """
    session_list: list[str] = []
    if not os.path.exists(sessions_dir):
        return session_list

    try:
        # 获取所有 JSON 文件，按修改时间倒序排列
        files = [
            f for f in os.listdir(sessions_dir)
            if f.endswith(".json")
        ]
        files.sort(
            key=lambda f: os.path.getmtime(os.path.join(sessions_dir, f)),
            reverse=True,
        )
        session_list = [f[:-5] for f in files]
    except OSError as e:
        logger.error("读取会话目录失败: %s", e)

    return session_list


def load_session_data(
    session_name: str,
    sessions_dir: str = config.SESSIONS_DIR,
) -> dict | None:
    """加载指定会话的完整数据

    Args:
        session_name: 会话名称（不含 .json 后缀）
        sessions_dir: 会话存储目录

    Returns:
        会话数据字典，不存在时返回 None
    """
    try:
        file_path = _get_session_path(session_name, sessions_dir)
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.error("加载会话失败 [%s]: %s", session_name, e)
        return None


def delete_session_file(
    session_name: str,
    sessions_dir: str = config.SESSIONS_DIR,
) -> None:
    """删除指定会话的文件

    Args:
        session_name: 会话名称
        sessions_dir: 会话存储目录
    """
    try:
        file_path = _get_session_path(session_name, sessions_dir)
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        logger.error("删除会话文件失败 [%s]: %s", session_name, e)
        raise


def export_session(
    session_name: str,
    sessions_dir: str = config.SESSIONS_DIR,
) -> str | None:
    """导出会话数据为 JSON 字符串

    Args:
        session_name: 会话名称
        sessions_dir: 会话存储目录

    Returns:
        格式化的 JSON 字符串，会话不存在时返回 None
    """
    data = load_session_data(session_name, sessions_dir)
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, indent=2)
