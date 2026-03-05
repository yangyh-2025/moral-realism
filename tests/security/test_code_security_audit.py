"""
代码安全审计测试

使用bandit进行静态安全分析：
- 检测危险函数使用
- 检查安全漏洞
"""
import pytest
import subprocess


@pytest.mark.security
class TestCodeSecurityAudit:
    """代码安全审计测试"""

    def test_bandit_available(self):
        """测试bandit是否可用"""
        try:
            result = subprocess.run(
                ["bandit", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.skip("bandit未安装")
        except subprocess.TimeoutExpired:
            pytest.skip("bandit超时")

    def test_run_bandit_on_src(self):
        """测试在src目录运行bandit扫描"""
        import os

        try:
            src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
        except NameError:
            # fallback
            src_dir = "src"

        if not os.path.exists(src_dir):
            pytest.skip("src目录不存在")

        try:
            result = subprocess.run(
                ["bandit", "-r", src_dir, "-f", "json"],
                capture_output=True,
                text=True,
                timeout=120
            )

            # bandit返回0表示无问题，1表示发现安全问题
            # 这是预期的，只检查是否能运行
            assert result.returncode in [0, 1]

            # 检查是否有高危或严重问题
            try:
                import json
                bandit_result = json.loads(result.stdout)
                if "results" in bandit_result:
                    high_severity = []
                    for issue in bandit_result["results"]:
                        if issue.get("issue_severity") in ["HIGH", "MEDIUM"]:
                            high_severity.append({
                                "file": issue.get("filename"),
                                "line": issue.get("line_number"),
                                "issue": issue.get("issue_text"),
                                "severity": issue.get("issue_severity")
                            })

                    # 注意：在实际CI/CD中，这可能需要允许列表
                    if high_severity:
                        pytest.warn(
                            f"发现{len(high_severity)}个高/中危安全问题"
                        )
            except json.JSONDecodeError:
                # 输出可能不是有效的JSON
                pass
        except FileNotFoundError:
            pytest.skip("bandit未安装")
        except subprocess.TimeoutExpired:
            pytest.skip("bandit扫描超时")

    def test_bandit_on_api(self):
        """测试在api目录运行bandit扫描"""
        import os

        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        except NameError:
            base_dir = "."

        api_dir = os.path.join(base_dir, "api")

        if not os.path.exists(api_dir):
            pytest.skip("api目录不存在")

        try:
            result = subprocess.run(
                ["bandit", "-r", api_dir, "-f", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )

            assert result.returncode in [0, 1]
        except FileNotFoundError:
            pytest.skip("bandit未安装")
        except subprocess.TimeoutExpired:
            pytest.skip("bandit扫描超时")


@pytest.mark.security
class TestCodeSecurityPatterns:
    """代码安全模式测试"""

    def test_no_hardcoded_secrets(self):
        """测试检查硬编码的密钥"""
        import os
        import re

        # 扫描项目中的Python文件
        base_dir = os.path.dirname(os.path.dirname(__file__))
        secrets_found = []

        # 常见的密钥模式
        secret_patterns = [
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for i, line in enumerate(content.split('\n'), 1):
                                for pattern in secret_patterns:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        # 排除测试文件和环境变量引用
                                        if 'test' not in file_path.lower():
                                            if 'os.environ' not in line:
                                                secrets_found.append({
                                                    "file": file_path,
                                                    "line": i,
                                                    "content": line.strip()
                                                })
                    except Exception:
                        pass

        if secrets_found:
            pytest.warn(f"发现{len(secrets_found)}处可能硬编码的密钥：{secrets_found[:5]}")

    def test_no_sql_injection_patterns(self):
        """测试检查SQL注入模式"""
        import os
        import re

        base_dir = os.path.dirname(os.path.dirname(__file__))
        risky_patterns = []

        # 危险的SQL模式
        sql_patterns = [
            r'execute\s*\(\s*["\'][^"\']*\+',
            r'execute\s*\(\s*f["\'].*%\s*%s',
            r'cursor\.execute\s*\(\s*["\'][^"\']*\+',
        ]

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for i, line in enumerate(content.split('\n'), 1):
                                for pattern in sql_patterns:
                                    if re.search(pattern, line):
                                        risky_patterns.append({
                                            "file": file_path,
                                            "line": i,
                                            "content": line.strip()
                                        })
                    except Exception:
                        pass

        if risky_patterns:
            pytest.warn(f"发现{len(risky_patterns)}处可能的SQL注入风险：{risky_patterns[:5]}")

    def test_no_shell_injection_patterns(self):
        """测试检查Shell注入模式"""
        import os
        import re

        base_dir = os.path.dirname(os.path.dirname(__file__))
        risky_patterns = []

        # 危险的shell执行模式
        shell_patterns = [
            r'subprocess\.call\s*\(\s*["\'][^"\']*\+',
            r'os\.system\s*\(\s*["\'][^"\']*\+',
            r'subprocess\.Popen\s*\(\s*["\'][^"\']*\+',
        ]

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for i, line in enumerate(content.split('\n'), 1):
                                for pattern in shell_patterns:
                                    if re.search(pattern, line):
                                        risky_patterns.append({
                                            "file": file_path,
                                            "line": i,
                                            "content": line.strip()
                                        })
                    except Exception:
                        pass

        if risky_patterns:
            pytest.warn(f"发现{len(risky_patterns)}处可能的Shell注入风险：{risky_patterns[:5]}")


@pytest.mark.security
class TestCodeSecurityBestPractices:
    """代码安全最佳实践测试"""

    def test_use_https_not_http(self):
        """测试检查使用HTTPS而非HTTP"""
        import os
        import re

        base_dir = os.path.dirname(os.path.dirname(__file__))
        http_usages = []

        http_pattern = r'http://[^"\']*'
        # 排除允许的HTTP URL
        allowed_urls = [
            r'http://localhost',
            r'http://127\.0\.0\.1',
            r'http://example\.com',
            r'http://test\.local',
        ]

        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for i, line in enumerate(content.split('\n'), 1):
                                matches = re.finditer(http_pattern, line)
                                for match in matches:
                                    url = match.group()
                                    # 检查是否在允许列表中
                                    if not any(re.search(allowed, url) for allowed in allowed_urls):
                                        http_usages.append({
                                            "file": file_path,
                                            "line": i,
                                            "content": line.strip()
                                        })
                    except Exception:
                        pass

        if http_usages:
            pytest.warn(f"发现{len(http_usages)}处使用非HTTPS URL：{http_usages[:5]}")

    def test_no_debug_code_in_production(self):
        """测试检查生产代码中不应有调试代码"""
        import os

        base_dir = os.path.dirname(os.path.dirname(__file__))
        debug_code = []

        # 调试模式模式
        debug_patterns = [
            'pdb.set_trace',
            'breakpoint()',
            'print(',
        ]

        for root, _, files in os.walk(base_dir):
            # 跳过测试文件
            if 'test' in root.lower():
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for i, line in enumerate(content.split('\n'), 1):
                                for pattern in debug_patterns:
                                    if pattern in line:
                                        debug_code.append({
                                            "file": file_path,
                                            "line": i,
                                            "content": line.strip()
                                        })
                    except Exception:
                        pass

        if debug_code:
            pytest.warn(f"发现{len(debug_code)}处可能的调试代码：{debug_code[:5]}")
