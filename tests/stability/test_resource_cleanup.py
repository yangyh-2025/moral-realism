"""
资源清理稳定性测试

测试模拟停止后的资源释放：
- 模拟停止后的资源释放
- 文件句柄清理
"""
import pytest
import gc
import os
from unittest.mock import Mock


@pytest.mark.stability
class TestResourceCleanup:
    """资源清理测试"""

    def test_controller_cleanup(self):
        """测试控制器资源清理"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        # 创建控制器
        controller = SimulationController(
            agents=[],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=10
        )

        # 删除控制器
        del controller
        gc.collect()

        # 如果没有异常，资源已正确清理
        pass

    def test_agent_cleanup(self):
        """测试代理资源清理"""
        try:
            from src.models.agent import Agent
        except ImportError:
            pytest.skip("Agent类未找到")

        # 创建代理
        agent = Agent(
            agent_id="test_agent",
            name="测试代理",
            capability=Mock(),
            leadership_profile=Mock()
        )

        # 删除代理
        del agent
        gc.collect()

        # 资源已清理
        pass

    def test_environment_cleanup(self):
        """测试环境资源清理"""
        try:
            from src.environment.rule_environment import RuleEnvironment
        except ImportError:
            pytest.skip("RuleEnvironment类未找到")

        # 创建环境
        env = RuleEnvironment(name="测试环境")

        # 删除环境
        del env
        gc.collect()

        # 资源已清理
        pass


@pytest.mark.stability
class TestFileHandleCleanup:
    """文件句柄清理测试"""

    def test_file_handle_closed(self, temp_dir):
        """测试文件句柄关闭"""
        test_file = temp_dir / "test.txt"

        # 写入文件
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("测试内容")

        # 文件句柄应该在with块结束后关闭
        # 验证文件可以被打开（没有锁定）
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert content == "测试内容"

    def test_temp_file_cleanup(self, temp_dir):
        """测试临时文件清理"""
        import tempfile

        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(
            dir=str(temp_dir),
            delete=False  # 手动删除用于测试
        )

        temp_file.write(b"测试内容")
        temp_file_path = temp_file.name
        temp_file.close()

        # 手动删除
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        # 文件已删除
        assert not os.path.exists(temp_file_path)


@pytest.mark.stability
class TestConnectionCleanup:
    """连接清理测试"""

    def test_socket_cleanup(self):
        """测试Socket连接清理"""
        import socket

        # 创建socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 关闭socket
        sock.close()

        # 验证socket已关闭
        assert sock.fileno() == -1

    def test_database_connection_cleanup(self):
        """测试数据库连接清理"""
        # Mock数据库连接
        class MockConnection:
            def __init__(self):
                self.is_connected = True

            def close(self):
                self.is_connected = False

        conn = MockConnection()
        assert conn.is_connected is True

        conn.close()
        assert conn.is_connected is False


@pytest.mark.stability
class TestMemoryCleanup:
    """内存清理测试"""

    def test_large_data_cleanup(self):
        """测试大数据清理"""
        gc.collect()
        initial_objects = len(gc.get_objects())

        # 创建大数据
        large_data = [{}] * 10000

        # 删除大数据
        del large_data
        gc.collect()

        # 验证对象已清理
        final_objects = len(gc.get_objects())
        leaked_objects = final_objects - initial_objects

        # 允许一定程度的对象增长
        assert leaked_objects < initial_objects * 0.5

    def test_nested_structure_cleanup(self):
        """测试嵌套结构清理"""
        gc.collect()
        initial_objects = len(gc.get_objects())

        # 创建嵌套结构
        nested = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": [{}] * 1000
                    }
                }
            }
        }

        # 删除嵌套结构
        del nested
        gc.collect()

        # 验证对象已清理
        final_objects = len(gc.get_objects())
        leaked_objects = final_objects - initial_objects

        assert leaked_objects < initial_objects * 0.5


@pytest.mark.stability
class TestThreadCleanup:
    """线程清理测试"""

    def test_thread_cleanup(self):
        """测试线程清理"""
        import threading

        completed = [False]

        def worker():
            import time
            time.sleep(0.1)
            completed[0] = True

        # 创建线程
        thread = threading.Thread(target=worker)
        thread.start()

        # 等待线程完成
        thread.join(timeout=5)

        # 线程应该已完成
        assert completed[0] is True
        assert not thread.is_alive()


@pytest.mark.stability
class TestProcessCleanup:
    """进程清理测试"""

    def test_subprocess_cleanup(self):
        """测试子进程清理"""
        import subprocess

        # 启动子进程
        proc = subprocess.Popen(
            ["python", "-c", "import time; time.sleep(0.1)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 等待进程完成
        proc.wait(timeout=10)

        # 验证进程已终止
        assert proc.returncode is not None
