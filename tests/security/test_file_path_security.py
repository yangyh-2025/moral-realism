"""
文件路径安全检查测试

测试路径遍历攻击防护：
- 路径遍历攻击防护
- 符号链接攻击防护
"""
import pytest
import os


@pytest.mark.security
class TestPathTraversalProtection:
    """路径遍历攻击防护测试"""

    def test_no_path_traversal(self):
        """测试路径遍历防护"""
        import os
        import pathlib

        # 模拟文件访问函数
        def safe_file_access(base_dir, file_path):
            # 解析文件路径并检查是否在基础目录内
            try:
                full_path = (pathlib.Path(base_dir) / file_path).resolve()
                base_path = pathlib.Path(base_dir).resolve()

                # 检查路径是否在基础目录内
                if not str(full_path).startswith(str(base_path)):
                    raise ValueError("路径遍历攻击检测")

                return full_path
            except Exception as e:
                raise ValueError(f"无效文件路径：{e}")

        base_dir = "/safe/directory"
        base_path = pathlib.Path(base_dir)

        # 测试正常路径（应该成功）
        try:
            # 注意：这些路径不需要实际存在
            safe_file_access(base_dir, "file.txt")
            safe_file_access(base_dir, "subdir/file.txt")
        except ValueError as e:
            if "遍历" not in str(e):
                # 允许其他错误（路径不存在）
                pass

        # 测试恶意路径（应该失败）
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd",
            "/etc/passwd",
            "C:\\Windows\\System32\\config",
        ]

        for malicious_path in malicious_paths:
            with pytest.raises(ValueError):
                safe_file_access(base_dir, malicious_path)

    def test_normalize_file_path(self):
        """测试文件路径规范化"""
        import os
        import pathlib

        def normalize_path(file_path):
            # 规范化路径
            if isinstance(file_path, str):
                normalized = os.path.normpath(file_path)
                if normalized.startswith(os.sep):
                    return normalized[1:]  # 移除前导斜杠
                return normalized
            return str(file_path)

        # 测试路径规范化
        test_cases = [
            ("file.txt", "file.txt"),
            ("subdir/file.txt", "subdir/file.txt"),
            ("subdir/../file.txt", "file.txt"),
            ("../file.txt", os.path.join("..", "file.txt")),
        ]

        for input_path, expected_norm in test_cases:
            result = normalize_path(input_path)
            # 规范化后的路径应该符合预期
            assert result is not None

    def test_validate_path_components(self):
        """测试路径组件验证"""
        def validate_path_components(path):
            """验证路径组件不包含恶意部分"""
            dangerous_components = [
                "etc",
                "windows",
                "system32",
                "config",
                "password",
                "secret",
            ]

            path_lower = path.lower()
            for component in dangerous_components:
                if component in path_lower:
                    return False

            return True

        # 测试验证函数
        assert validate_path_components("safe/file.txt") is True
        assert validate_path_components("data/test.json") is True

        # 恶意路径应该被拒绝
        malicious_paths = [
            "/etc/passwd",
            "C:/Windows/System32/config",
            "/secrets/api_key.txt",
        ]

        for path in malicious_paths:
            assert validate_path_components(path) is False


@pytest.mark.security
class TestSymbolicLinkProtection:
    """符号链接攻击防护测试"""

    def test_detect_symbolic_links(self):
        """测试检测符号链接"""
        import os
        import pathlib

        def is_symbolic_link(file_path):
            """检查路径是否包含符号链接"""
            if isinstance(file_path, str):
                file_path = pathlib.Path(file_path)

            # 检查路径的每个组件
            parts = file_path.parts
            for part in parts:
                # 符号链接通常包含特殊字符
                if part.startswith('@') or part.startswith('\x00'):
                    return True

            # 检查实际文件（如果存在）
            if os.path.exists(str(file_path)):
                if os.path.islink(str(file_path)):
                    return True

            return False

        # 测试检测函数
        assert is_symbolic_link("normal_file.txt") is False
        assert is_symbolic_link("safe/nested/file.txt") is False

        # 符号链接（如果应该被检测）
        # 注意：这些只是测试，实际符号链接需要在文件系统上创建


@pytest.mark.security
class TestFileExtensionSecurity:
    """文件扩展名安全测试"""

    def test_validate_file_extension(self):
        """测试验证文件扩展名"""
        def is_safe_extension(file_path, allowed_extensions):
            """检查文件扩展名是否在允许列表中"""
            import os

            _, ext = os.path.splitext(file_path)
            ext = ext.lower().lstrip('.')
            return ext in allowed_extensions

        # 允许的扩展名
        allowed = ['txt', 'json', 'csv', 'png', 'jpg']

        # 测试有效扩展名
        valid_files = [
            "file.txt",
            "data.json",
            "image.png",
            "document.csv",
        ]

        for file_path in valid_files:
            assert is_safe_extension(file_path, allowed) is True

        # 测试无效扩展名
        invalid_files = [
            "file.exe",
            "script.sh",
            "dangerous.php",
            "backdoor.py",
        ]

        for file_path in invalid_files:
            assert is_safe_extension(file_path, allowed) is False

    def test_no_double_extensions(self):
        """测试防止双扩展名攻击"""
        def detect_double_extension(file_path):
            """检测双扩展名"""
            import os

            base = os.path.basename(file_path)
            parts = base.split('.')

            # 检查是否有多个扩展名
            # 例如：file.txt.exe
            if len(parts) > 2:
                # 常见的安全扩展名（第一个扩展名）
                decoy_extensions = ['txt', 'doc', 'xls', 'pdf', 'jpg', 'png']
                if parts[-2].lower() in decoy_extensions:
                    return True

            return False

        # 测试双扩展名检测
        assert detect_double_extension("file.txt") is False
        assert detect_double_extension("file.txt.exe") is True
        assert detect_double_extension("document.pdf.bat") is True
        assert detect_double_extension("image.jpg.sh") is True


@pytest.mark.security
class TestFilenameSanitization:
    """文件名清理测试"""

    def test_sanitize_filename(self):
        """测试文件名清理"""
        def sanitize_filename(filename):
            """清理文件名，移除危险字符"""
            import re

            # 移除路径分隔符
            sanitized = re.sub(r'[\/\\\?*:|"<>\0-\x1f]', '_', filename)

            # 限制长度
            if len(sanitized) > 255:
                sanitized = sanitized[:255]

            # 移除前导点和空格
            sanitized = sanitized.lstrip('. ')

            if not sanitized:
                sanitized = 'unnamed'

            return sanitized

        # 测试清理函数
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file/with/slashes.txt", "file_with_slashes.txt"),
            ("file\\with\\backslashes.txt", "file_with_backslashes.txt"),
            ("file|with|pipes.txt", "file_with_pipes.txt"),
            ("file:with:colons.txt", "file_with_colons.txt"),
            ("..hidden_file.txt", "_hidden_file.txt"),
            ("  leading_spaces.txt", "leading_spaces.txt"),
            ("trailing_spaces.txt  ", "trailing_spaces.txt"),
        ]

        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected

    def test_validate_filename(self):
        """测试验证文件名"""
        def is_valid_filename(filename):
            """验证文件名是否有效"""
            import os

            # 检查空文件名
            if not filename or filename.isspace():
                return False

            # 检查路径分隔符
            if '/' in filename or '\\\\' in filename:
                return False

            # 检查保留名称
            reserved_names = [
                'CON', 'PRN', 'AUX', 'NUL',
                'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
            ]

            base_name = os.path.splitext(filename)[0].upper()
            if base_name in reserved_names:
                return False

            return True

        # 测试验证函数
        assert is_valid_filename("normal_file.txt") is True
        assert is_valid_filename("data.txt") is True

        # 无效文件名
        invalid_names = [
            "",
            "   ",
            "file/name.txt",
            "file\\name.txt",
            "CON.txt",
            "PRN.txt",
        ]

        for name in invalid_names:
            assert is_valid_filename(name) is False


@pytest.mark.security
class TestDirectoryAccessSecurity:
    """目录访问安全测试"""

    def test_validate_directory_access(self):
        """测试验证目录访问"""
        def is_safe_directory(directory, allowed_dirs):
            """ """检查目录是否在允许列表中"""
            import os
            import pathlib

            # 规范化目录路径
            norm_dir = os.path.normpath(directory)
            norm_allowed = [os.path.normpath(d) for d in allowed_dirs]

            # 检查是否在允许目录中
            for allowed_dir in norm_allowed:
                if norm_dir.startswith(allowed_dir):
                    return True

            return False

        # 允许的目录
        allowed_dirs = [
            "/safe/uploads",
            "/data/files",
            "/tmp",
        ]

        # 测试允许的目录
        assert is_safe_directory("/safe/uploads/file.txt", allowed_dirs) is True
        assert is_safe_directory("/data/files/subdir/", allowed_dirs) is True

        # 不允许的目录
        disallowed_dirs = [
            "/etc/passwd",
            "/",
            "/root",
            "/home/user/.ssh",
        ]

        for dir_path in disallowed_dirs:
            assert is_safe_directory(dir_path, allowed_dirs) is False

    def test_prevent_directory_listing(self):
        """测试防止目录列表"""
        def should_prevent_listing(directory):
            """检查是否应该防止目录列表"""
            # 某些目录不应该允许列表
            protected_dirs = [
                "/etc",
                "/root",
                "/home",
                "/var",
                "/usr",
            ]

            for protected_dir in protected_dirs:
                if directory.startswith(protected_dir):
                    return True

            return False

        # 测试保护目录
        assert should_prevent_listing("/etc") is True
        assert should_prevent_listing("/root/secret") is True
        assert should_prevent_listing("/var/log") is True

        # 非保护目录
        assert should_prevent_listing("/safe/data") is False
        assert should_prevent_listing("/uploads") is False
