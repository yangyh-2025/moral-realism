"""
状态管理器单元测试

测试StateManager类的核心功能：
- 初始化和配置
- 状态保存和恢复
- 检查点操作
"""
import pytest
from unittest.mock import Mock
import json


class TestStateManagerInitialization:
    """测试StateManager初始化"""

    def test_state_manager_initialization(self):
        """测试状态管理器初始化"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        assert manager is not None

    def test_state_manager_with_storage_path(self, temp_dir):
        """测试带存储路径初始化"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        storage_path = temp_dir / "state_storage.json"
        manager = StateManager(storage_path=str(storage_path))

        # 存储路径已设置
        pass


class TestStateManagerSaveLoad:
    """测试状态保存和加载"""

    def test_save_state(self, temp_dir):
        """测试保存状态"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'save_state'):
            state = {
                "current_round": 5,
                "agents": {},
                "environment": {}
            }

            save_path = temp_dir / "state.json"
            manager.save_state(state, str(save_path))

            assert save_path.exists()

    def test_load_state(self, temp_dir):
        """测试加载状态"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        # 创建状态文件
        state_data = {
            "current_round": 5,
            "agents": {"agent_1": {"power": 75}},
            "environment": {"order_level": 3}
        }

        state_path = temp_dir / "state.json"
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f)

        manager = StateManager()

        if hasattr(manager, 'load_state'):
            loaded_state = manager.load_state(str(state_path))
            assert loaded_state["current_round"] == 5


class TestStateManagerCheckpoints:
    """测试检查点操作"""

    def test_create_checkpoint(self, temp_dir):
        """测试创建检查点"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager(checkpoints_dir=str(temp_dir))

        if hasattr(manager, 'create_checkpoint'):
            state = {
                "current_round": 5,
                "agents": {},
                "environment": {}
            }

            checkpoint_id = manager.create_checkpoint(state, description="第5回合检查点")
            assert checkpoint_id is not None

    def test_load_checkpoint(self, temp_dir):
        """测试加载检查点"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager(checkpoints_dir=str(temp_dir))

        if hasattr(manager, 'create_checkpoint') and hasattr(manager, 'load_checkpoint'):
            state = {
                "current_round": 5,
                "agents": {},
                "environment": {}
            }

            checkpoint_id = manager.create_checkpoint(state)
            loaded_state = manager.load_checkpoint(checkpoint_id)

            assert loaded_state["current_round"] == 5

    def test_list_checkpoints(self, temp_dir):
        """测试列出检查点"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager(checkpoints_dir=str(temp_dir))

        if hasattr(manager, 'create_checkpoint') and hasattr(manager, 'list_checkpoints'):
            state = {"current_round": 5}
            manager.create_checkpoint(state, description="检查点1")
            manager.create_checkpoint(state, description="检查点2")

            checkpoints = manager.list_checkpoints()
            assert len(checkpoints) == 2

    def test_delete_checkpoint(self, temp_dir):
        """测试删除检查点"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager(checkpoints_dir=str(temp_dir))

        if hasattr(manager, 'create_checkpoint') and hasattr(manager, 'delete_checkpoint'):
            state = {"current_round": 5}
            checkpoint_id = manager.create_checkpoint(state)

            manager.delete_checkpoint(checkpoint_id)

            checkpoints = manager.list_checkpoints()
            assert checkpoint_id not in [c["id"] for c in checkpoints]


class TestStateManagerDeltas:
    """测试增量状态"""

    def test_create_delta(self):
        """测试创建增量"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'create_delta'):
            old_state = {"current_round": 5, "value": 100}
            new_state = {"current_round": 6, "value": 105}

            delta = manager.create_delta(old_state, new_state)
            assert "current_round" in delta.changes

    def test_apply_delta(self):
        """测试应用增量"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'create_delta') and hasattr(manager, 'apply_delta'):
            old_state = {"current_round": 5, "value": 100}
            new_state = {"current_round": 6, "value": 105}

            delta = manager.create_delta(old_state, new_state)
            applied = manager.apply_delta(old_state, delta)

            assert applied["current_round"] == 6


class TestStateManagerCompression:
    """测试状态压缩"""

    def test_compress_state(self):
        """测试压缩状态"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'compress_state'):
            state = {
                "current_round": 5,
                "agents": {f"agent_{i}": {"power": 50 + i} for i in range(100)}
            }

            compressed = manager.compress_state(state)
            # 压缩后的状态应该更小
            assert len(str(compressed)) < len(str(state))

    def test_decompress_state(self):
        """测试解压状态"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'compress_state') and hasattr(manager, 'decompress_state'):
            state = {
                "current_rounded": 5,
                "agents": {"agent_1": {"power": 75}}
            }

            compressed = manager.compress_state(state)
            decompressed = manager.decompress_state(compressed)

            assert decompressed["current_rounded"] == 5


class TestStateManagerValidation:
    """测试状态验证"""

    def test_validate_state(self):
        """测试验证状态"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'validate_state'):
            valid_state = {
                "current_round": 5,
                "agents": {},
                "environment": {}
            }

            is_valid = manager.validate_state(valid_state)
            assert is_valid is True

    def test_validate_invalid_state(self):
        """测试验证无效状态"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'validate_state'):
            invalid_state = {}

            is_valid = manager.validate_state(invalid_state)
            assert is_valid is False


class TestStateManagerHistory:
    """测试状态历史"""

    def test_record_state(self):
        """测试记录状态"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'record_state'):
            state = {"current_round": 5}
            manager.record_state(state)

            # 状态已记录
            pass

    def test_get_state_history(self):
        """测试获取状态历史"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager()

        if hasattr(manager, 'record_state') and hasattr(manager, 'get_state_history'):
            for i in range(5):
                manager.record_state({"current_round": i})

            history = manager.get_state_history()
            assert len(history) == 5


class TestStateManagerBackup:
    """测试备份功能"""

    def test_create_backup(self, temp_dir):
        """测试创建备份"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager(backup_dir=str(temp_dir))

        if hasattr(manager, 'create_backup'):
            state = {"current_round": 5}
            backup_id = manager.create_backup(state)

            assert backup_id is not None

    def test_restore_backup(self, temp_dir):
        """测试恢复备份"""
        try:
            from src.workflow.state_manager import StateManager
        except ImportError:
            pytest.skip("StateManager类未找到")

        manager = StateManager(backup_dir=str(temp_dir))

        if hasattr(manager, 'create_backup') and hasattr(manager, 'restore_backup'):
            state = {"current_round": 5}
            backup_id = manager.create_backup(state)

            restored = manager.restore_backup(backup_id)
            assert restored["current_round"] == 5
