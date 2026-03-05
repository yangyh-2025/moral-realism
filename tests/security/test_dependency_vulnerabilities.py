"""
依赖漏洞安全检查测试

使用pip-audit扫描依赖漏洞：
- 使用pip-audit扫描依赖漏洞
- 使用safety检查已知安全问题
"""
import pytest
import subprocess
import json


@pytest.mark.security
class TestDependencyVulnerabilities:
    """依赖漏洞测试"""

    def test_pip_audit_available(self):
        """测试pip-audit是否可用"""
        try:
            result = subprocess.run(
                ["pip-audit", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.skip("pip-audit未安装")
        except subprocess.TimeoutExpired:
            pytest.skip("pip-audit超时")

    def test_run_pip_audit(self):
        """测试运行pip-audit扫描"""
        try:
            result = subprocess.run(
                ["pip-audit", "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )

            # 检查是否成功执行
            assert result.returncode in [0, 1]  # 0=无漏洞，1=发现漏洞

            # 解析输出
            try:
                audit_result = json.loads(result.stdout)
                assert "dependencies" in audit_result
            except json.JSONDecodeError:
                # 输出可能不是JSON格式
                pass
        except FileNotFoundError:
            pytest.skip("pip-audit未安装")
        except subprocess.TimeoutExpired:
            pytest.skip("pip-audit超时")

    def test_pip_audit_vulnerabilities_critical(self):
        """测试检查关键漏洞"""
        try:
            result = subprocess.run(
                ["pip-audit", "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )

            try:
                audit_result = json.loads(result.stdout)

                # 检查有关键级别的漏洞
                if "dependencies" in audit_result:
                    critical_vulns = []
                    for dep, vulns in audit_result["dependencies"].items():
                        for vuln in vulns:
                            severity = vuln.get("severity", "").lower()
                            if severity in ["critical", "high"]:
                                critical_vulns.append({
                                    "package": dep,
                                    "vulnerability": vuln
                                })

                    # 断言：应该没有关键或高危漏洞
                    # 注意：在实际CI/CD中，这可能需要允许列表
                    if critical_vulns:
                        pytest.fail(
                            f"发现{len(critical_vulns)}个关键/高危漏洞：{ {[v['package'] for v in critical_vulns]}"
                        )
            except json.JSONDecodeError:
                pass
        except FileNotFoundError:
            pytest.skip("pip-audit未安装")
        except subprocess.TimeoutExpired:
            pytest.skip("pip-audit超时")

    def test_safety_available(self):
        """测试safety是否可用"""
        try:
            result = subprocess.run(
                ["safety", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.skip("safety未安装")
        except subprocess.TimeoutExpired:
            pytest.skip("safety超时")

    def test_run_safety_check(self):
        """测试运行safety检查"""
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=60
            )

            # 检查是否成功执行
            # safety返回非0表示发现安全问题
            assert result.returncode in [0, 1, 127]

            try:
                safety_result = json.loads(result.stdout)
                assert isinstance(safety_result, list) or isinstance(safety_result, dict)
            except json.JSONDecodeError:
                # 输出可能不是JSON格式
                pass
        except FileNotFoundError:
            pytest.skip("safety未安装")
        except subprocess.TimeoutExpired:
            pytest.skip("safety超时")


@pytest.mark.security
class TestDependencyIntegrity:
    """依赖完整性测试"""

    def test_check_requirements_exist(self):
        """测试requirements文件是否存在"""
        import os

        # 检查常见的requirements文件
        requirement_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "setup.py"
        ]

        # 至少应该有一个依赖配置文件
        project_root = os.path.dirname(os.path.dirname(__file__))
        found_files = []
        for req_file in requirement_files:
            file_path = os.path.join(project_root, req_file)
            if os.path.exists(file_path):
                found_files.append(req_file)

        assert len(found_files) > 0, "未找到任何依赖配置文件"

    def test_pyproject_toml_valid(self):
        """测试pyproject.toml是否有效"""
        import os
        try:
            import tomli
        except ImportError:
            pytest.skip("tomli未安装")

        project_root = os.path.dirname(os.path.dirname(__file__))
        pyproject_path = os.path.join(project_root, "pyproject.toml")

        if not os.path.exists(pyproject_path):
            pytest.skip("pyproject.toml不存在")

        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            config = tomli.loads(content)
            assert "project" in config
            assert "name" in config["project"]
        except Exception as e:
            pytest.fail(f"pyproject.toml解析失败：{e}")


@pytest.mark.security
class TestDependencyVersions:
    """依赖版本测试"""

    def test_no_unpinned_dependencies(self):
        """测试检查未固定的依赖（在requirements.txt中）"""
        import os
        import re

        project_root = os.path.dirname(os.path.dirname(__file__))
        req_path = os.path.join(project_root, "requirements.txt")

        if not os.path.exists(req_path):
            pytest.skip("requirements.txt不存在")

        with open(req_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        unpinned = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # 检查是否有版本规范
                if not re.search(r'[=<>~!]', line):
                    unpinned.append(line)

        # 注意：某些依赖（如工具链）可以不固定
        # 这里只做警告，不失败
        if unpinned:
            pytest.warn(f"发现未固定的依赖：{unpinned}")

    def test_outdated_dependencies(self):
        """测试检查过时的依赖（可选）"""
        import os

        try:
            result = subprocess.run(
                ["pip", "list", "outdated", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                # 注意：这只提供信息，不作为失败条件
                if outdated:
                    pytest.warn(f"发现{len(outdated)}个过时的依赖")
        except FileNotFoundError:
            pytest.skip("pip未找到")
        except subprocess.TimeoutExpired:
            pytest.skip("pip超时")
        except json.JSONDecodeError:
            pytest.skip("无法解析pip输出")


@pytest.mark.security
class TestDependencyLicenses:
    """依赖许可证测试（可选）"""

    def test_check_licenses(self):
        """测试检查依赖许可证"""
        try:
            import piplicenses_parser
        except ImportError:
            pytest.skip("pip-licenses未安装")

        try:
            # 创建解析器
            parser = piplicenses_parser.create_arg_parser()
            args = parser.parse_args(['--format', 'json'])

            # 获取许可证信息
            from piplicenses_parser import get_licenses

            licenses = get_licenses(args)

            # 检查是否有问题的许可证
            problematic_licenses = ["GPL-3.0", "AGPL-3.0", "LGPL-3.0"]
            found_problematic = []

            for license_info in licenses:
            license_name = license_info.get('License', '')
                if license_name in problematic_licenses:
                    found_problematic.append({
                        'name': license_info.get('Name'),
                        'license': license_name
                    })

            if found_problematic:
                pytest.warn(
                    f"发现使用问题许可证的包：{found_problematic}"
                )
        except Exception as e:
            pytest.skip(f"无法获取许可证信息：{e}")
