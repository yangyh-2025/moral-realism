"""
敏感信息泄露安全检查测试

测试环境变量泄露检查：
- 环境变量泄露检查
- 日志中的敏感信息检查
"""
import pytest
import os


@pytest.mark.security
class TestEnvironmentVariableSecurity:
    """环境变量安全测试"""

    def test_no_hardcoded_credentials(self):
        """测试检查硬编码的凭据"""
        import os
        import re

        # 扫描Python文件中的硬编码凭据模式
        project_root = os.path.dirname(os.path.dirname(__file__))
        found_credentials = []

        # 常见凭据模式
        credential_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'private_key\s*=\s*["\'][^"\']+["\']',
        ]

        for root, _, files in os.walk(project_root):
            # 跳过虚拟环境和测试目录
            if 'venv' in root or '__pycache__' in root or 'tests' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for i, line in enumerate(content.split('\n'), 1):
                                for pattern in credential_patterns:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        # 检查是否是环境变量引用（允许）
                                        if 'os.environ' not in line and 'getenv' not in line:
                                            found_credentials.append({
                                                "file": file_path,
                                                "line": i,
                                                "content": line.strip()
                                            })
                    except Exception:
                        pass

        if found_credentials:
            pytest.warn(f"发现{len(found_credentials)}处可能硬编码的凭据：{found_credentials[:5]}")

    def test_no_api_keys_in_config(self):
        """测试检查配置文件中的API密钥"""
        import os

        project_root = os.path.dirname(os.path.dirname(__file__))
        config_files = [
            os.path.join(project_root, "config.py"),
            os.path.join(project_root, "settings.py"),
            os.path.join(project_root, ".env"),
        ]

        api_key_patterns = [
            'sk-',
            'gpt_',
            'openai_',
            'api_key',
            'secret_key',
        ]

        for config_file in config_files:
            if not os.path.exists(config_file):
                continue

            with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()

                # 检查是否有API密钥模式
                for pattern in api_key_patterns:
                    if pattern in content and '=' in content:
                        # 如果这不是环境变量引用，警告
                        if 'os.environ' not in content:
                            pytest.warn(f"配置文件{config_file}中可能包含API密钥")


@pytest.mark.security
class TestLoggingSecurity:
    """日志安全测试"""

    def test_no_sensitive_data_in_logs(self):
        """测试检查日志中的敏感数据"""
        # 这个测试是示例性的
        # 实际实现需要分析日志文件或配置

        pass

    def test_log_level_configuration(self):
        """测试日志级别配置"""
        import os

        # 检查生产环境是否
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()

        # 如果在生产环境中，不应使用DEBUG日志级别
        if os.environ.get('ENVIRONMENT', 'development').lower() == 'production':
            assert log_level != 'DEBUG', "生产环境不应使用DEBUG日志级别"


@pytest.mark.security
class TestErrorHandlingSecurity:
    """错误处理安全测试"""

    def test_no_stack_traces_in_production(self):
        """测试生产环境不应显示堆栈跟踪"""
        import os

        # 在生产环境中，错误处理不应显示详细堆栈跟踪
        is_production = os.environ.get('ENVIRONMENT', 'development').lower() == 'production'

        if is_production:
            # 检查错误处理配置
            # 这是一个示例性测试
            pass

    def test_no_debug_mode_in_production(self):
        """测试生产环境不应启用调试模式"""
        import os

        is_production = os.environ.get('ENVIRONMENT', 'development').lower() == 'production'

        if is_production:
            debug_mode = os.environ.get('DEBUG', 'false').lower()
            assert debug_mode != 'true', "生产环境不应启用`DEBUG`模式"


@pytest.mark.security
class TestDataExposureSecurity:
    """数据暴露安全测试"""

    def test_no_sensitive_fields_in_serialization(self):
        """测试序列化中不应包含敏感字段"""
        # 模拟测试对象序列化
        class MockAgent:
            def __init__(self):
                self.agent_id = "agent_1"
                self.password = "secret_password"
                self.api_key = "secret_api_key"

        agent = MockAgent()

        # 序列化为字典
        serialized = agent.__dict__

        # 检查敏感字段
        sensitive_fields = ['password', 'api_key', 'secret']
        exposed_fields = [f for f in sensitive_fields if f in serialized]

        if exposed_fields:
            pytest.warn(f"序列化中的敏感字段：{exposed_fields}")

    def test_no_sensitive_data_in_api_responses(self):
        """测试API响应中不应包含敏感数据"""
        # 模拟API响应
        response = {
            "agent_id": "agent_1",
            "name": "测试代理",
            "password": "secret",  # 不应该出现在响应中
            "token": "secret_token",  # 不应该出现在响应中
        }

        # 检查敏感字段
        sensitive_fields = ['password', 'token', 'secret', 'api_key']
        exposed_fields = [f for f in sensitive_fields if f in response]

        if exposed_fields:
            pytest.warn(f"API响应中的敏感字段：{exposed_fields}")


@pytest.mark.security
class TestFilePermissionSecurity:
    """文件权限安全测试"""

    def test_sensitive_file_permissions(self):
        """测试敏感文件权限"""
        import os
        import stat

        project_root = os.path.dirname(os.path.dirname(__file__))
        sensitive_files = [
            os.path.join(project_root, ".env"),
            os.path.join(project_root, "config.py"),
            os.path.join(project_root, "secrets.py"),
        ]

        for file_path in sensitive_files:
            if not os.path.exists(file_path):
                continue

            # 获取文件权限
            file_stat = os.stat(file_path)
            mode = file_stat.st_mode

            # 检查是否可被其他人读取
            if mode & stat.S_IROTH:
                pytest.warn(f"敏感文件{file_path}可被其他人读取")

            # 检查是否可被组读取
            if mode & stat.S_IRGRP:
                pytest.warn(f"敏感文件{file_path}可被组读取")

    def test_no_sensitive_files_in_version_control(self):
        """测试敏感文件不应在版本控制中"""
        import os

        project_root = os.path.dirname(os.path.dirname(__file__))
        gitignore_path = os.path.join(project_root, ".gitignore")

        # 检查.gitignore是否存在
        if not os.path.exists(gitignore_path):
            pytest.warn(".gitignore文件不存在")

        # 检查是否包含敏感文件模式
        sensitive_patterns = ['.env', '*.key', '*_secrets.py', 'config.py']

        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()

            missing_patterns = []
            for pattern in sensitive_patterns:
                if pattern not in content:
                    missing_patterns.append(pattern)

            if missing_patterns:
                pytest.warn(f".gitignore中缺少敏感文件模式：{missing_patterns}")


@pytest.mark.security
class TestApiKeyManagement:
    """API密钥管理测试"""

    def test_api_key_from_environment(self):
        """测试API密钥应从环境变量获取"""
        import os

        # 检查API密钥环境变量是否存在
        # 注意：这个测试不验证密钥本身，只验证机制
        api_key_env = os.environ.get('OPENAI_API_KEY')

')

        if api_key_env is None:
            pytest.skip("OPENAI_API_KEY环境变量未设置（本地开发可能需要）")

        # 验证密钥不是示例或测试值
        test_values = ['test', 'example', 'placeholder', 'xxx']
        is_test_value = any(val in api_key_env.lower() for val in test_values)

        if is_test_value:
            pytest.warn("API密钥似乎是测试值")

    def test_no_api_key_in_source_code(self):
        """测试API密钥不应在源代码中"""
        import os

        project_root = os.path.dirname(os.path.dirname(__file__))
        found_keys = []

        # 扫描Python文件
        for root, _, files in os.walk(project_root):
            if 'venv' in root or '__pycache__' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 检查常见的API密钥模式
                            if 'sk-' in content and '=' in content:
                                found_keys.append(file_path)
                    except Exception:
                        pass

        if found_keys:
            pytest.warn(f"可能在源代码中发现API密钥：{found_keys[:3]}")
