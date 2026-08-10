"""会话管理模块单元测试

测试 session_manager.py 的所有 CRUD 操作。
所有测试不依赖 Streamlit、网络或 API Key。
"""
import json
import os
import tempfile
import time

import pytest

import session_manager


# ---- 共享 fixtures ----

@pytest.fixture
def sessions_dir() -> str:
    """创建临时目录用于测试"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_data() -> dict:
    """示例会话数据"""
    return {
        "nick_name": "测试角色",
        "nature": "测试性格",
        "display_name": "测试会话",
        "current_session": "test-session-001",
        "messages": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好呀！"},
        ],
    }


# ---- 测试类 ----

class TestGenerateSessionName:
    """会话名称生成测试"""

    def test_name_is_non_empty_string(self):
        name = session_manager.generate_session_name()
        assert isinstance(name, str)
        assert len(name) > 0

    def test_name_matches_datetime_format(self):
        name = session_manager.generate_session_name()
        # 格式: YYYY-MM-DD_HH-MM-SS
        parts = name.split("_")
        assert len(parts) == 2
        date_part, time_part = parts
        assert len(date_part.split("-")) == 3
        assert len(time_part.split("-")) == 3

    def test_names_differ_after_delay(self):
        """间隔超过1秒后生成的两个名称应不同（时间戳精度为秒级）"""
        name1 = session_manager.generate_session_name()
        time.sleep(1.1)
        name2 = session_manager.generate_session_name()
        assert name1 != name2


class TestSessionCRUD:
    """会话 CRUD 操作测试"""

    def test_save_and_load_roundtrip(self, sessions_dir, sample_data):
        """保存后再加载应返回一致数据"""
        session_manager.save_session(sample_data, sessions_dir)
        loaded = session_manager.load_session_data("test-session-001", sessions_dir)

        assert loaded is not None
        assert loaded["nick_name"] == "测试角色"
        assert loaded["nature"] == "测试性格"
        assert loaded["display_name"] == "测试会话"
        assert len(loaded["messages"]) == 2

    def test_load_nonexistent_session(self, sessions_dir):
        """加载不存在的会话应返回 None"""
        result = session_manager.load_session_data("nonexistent", sessions_dir)
        assert result is None

    def test_delete_session(self, sessions_dir, sample_data):
        """删除会话后文件应不存在"""
        session_manager.save_session(sample_data, sessions_dir)
        session_manager.delete_session_file("test-session-001", sessions_dir)

        file_path = os.path.join(sessions_dir, "test-session-001.json")
        assert not os.path.exists(file_path)

    def test_delete_nonexistent_does_not_raise(self, sessions_dir):
        """删除不存在的会话不应抛异常"""
        session_manager.delete_session_file("nonexistent", sessions_dir)

    def test_load_session_list(self, sessions_dir):
        """应正确列出所有会话名"""
        # 创建多个会话
        for i in range(3):
            session_manager.save_session({
                "current_session": f"session-{i}",
                "messages": [],
            }, sessions_dir)

        session_list = session_manager.load_session_list(sessions_dir)
        assert len(session_list) == 3
        for i in range(3):
            assert f"session-{i}" in session_list

    def test_load_session_list_empty_dir(self, sessions_dir):
        """空目录应返回空列表"""
        session_list = session_manager.load_session_list(sessions_dir)
        assert session_list == []

    def test_save_session_without_name_does_nothing(self, sessions_dir):
        """没有 current_session 时应安全跳过"""
        session_manager.save_session({"messages": []}, sessions_dir)
        # 不应创建任何文件
        assert len(os.listdir(sessions_dir)) == 0

    def test_export_session(self, sessions_dir, sample_data):
        """导出应返回格式化的 JSON 字符串"""
        session_manager.save_session(sample_data, sessions_dir)
        exported = session_manager.export_session("test-session-001", sessions_dir)

        assert exported is not None
        assert isinstance(exported, str)
        # 应为有效 JSON
        parsed = json.loads(exported)
        assert parsed["nick_name"] == "测试角色"

    def test_export_nonexistent_returns_none(self, sessions_dir):
        """导出不存在的会话应返回 None"""
        exported = session_manager.export_session("nonexistent", sessions_dir)
        assert exported is None


class TestSessionEncoding:
    """会话数据编码测试"""

    def test_unicode_nickname(self, sessions_dir):
        """包含 emoji 和特殊字符的昵称应正确保存和加载"""
        data = {
            "current_session": "unicode-test",
            "nick_name": "🌟小明",
            "nature": "温柔体贴的小姐姐👧",
            "messages": [{"role": "user", "content": "Hello 🌍"}],
        }
        session_manager.save_session(data, sessions_dir)
        loaded = session_manager.load_session_data("unicode-test", sessions_dir)

        assert loaded["nick_name"] == "🌟小明"
        assert loaded["messages"][0]["content"] == "Hello 🌍"

    def test_special_characters_in_nickname(self, sessions_dir):
        """包含 %s 等格式化字符的昵称不应出错"""
        data = {
            "current_session": "special-chars",
            "nick_name": "%s测试%d",
            "nature": "测试",
            "messages": [],
        }
        session_manager.save_session(data, sessions_dir)
        loaded = session_manager.load_session_data("special-chars", sessions_dir)
        assert loaded["nick_name"] == "%s测试%d"
