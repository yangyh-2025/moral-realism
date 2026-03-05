#!/usr/bin/env python3
"""
测试运行脚本

提供命令行界面运行不同类型的测试，生成测试报告，支持并行执行。

使用方法：
    python tests/test_runner.py --help
    python tests/test_runner.py unit
    python tests/test_runner.py integration
    python tests/test_runner.py security
    python tests/test_runner.py performance
    python tests/test_runner.py all
    python tests/test_runner.py all --parallel --cov-report=html
"""
import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"


class TestRunner:
    """测试运行器类"""

    def __init__(self, verbose: bool = False, parallel: bool = False):
        """
        初始化测试运行器

        Args:
            verbose: 是否显示详细输出
            parallel: 是否使用并行执行
        """
        self.verbose = verbose
        self.parallel = parallel

    def _build_pytest_command(self, test_path: str, extra_args: List[str] = None) -> List[str]:
        """
        构建pytest命令

        Args:
            test_path: 测试路径
            extra_args: 额外的pytest参数

        Returns:
            List[str]: pytest命令列表
        """
        cmd = ["python", "-m", "pytest"]

        if self.parallel:
            cmd.extend(["-n", "auto"])  # 自动检测CPU核心数

        if self.verbose:
            cmd.append("-v")

        cmd.append(test_path)

        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def _run_command(self, cmd: List[str]) -> int:
        """
        运行命令并返回退出代码

        Args:
            cmd: 命令列表

        Returns:
            int: 退出代码
        """
        print(f"运行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode

    def run_unit_tests(self, extra_args: Optional[List[str]] = None) -> int:
        """
        运行单元测试

        Args:
            extra_args: 额外的pytest参数

        Returns:
            int: 退出代码
        """
        print("\n" + "="*60)
        print("运行单元测试")
        print("="*60)

        test_path = str(TESTS_DIR / "unit")
        cmd = self._build_pytest_command(test_path, extra_args)

        return self._run_command(cmd)

    def run_integration_tests(self, extra_args: Optional[List[str]] = None) -> int:
        """
        运行集成测试

        Args:
            extra_args: 额外的pytest参数

        Returns:
            int: 退出代码
        """
        print("\n" + "="*60)
        print("运行集成测试")
        print("="*60)

        test_path = str(TESTS_DIR / "integration")
        cmd = self._build_pytest_command(test_path, extra_args)

        return self._run_command(cmd)

    def run_security_tests(self, extra_args: Optional[List[str]] = None) -> int:
        """
        运行安全测试

        Args:
            extra_args: 额外的pytest参数

        Returns:
            int: 退出代码
        """
        print("\n" + "="*60)
        print("运行安全检查测试")
        print("="*60)

        test_path = str(TESTS_DIR / "security")
        cmd = self._build_pytest_command(test_path, extra_args)

        return self._run_command(cmd)

    def run_performance_tests(self, extra_args: Optional[List[str]] = None) -> int:
        """
        运行性能测试

        Args:
            extra_args: 额外的pytest参数

        Returns:
            int: 退出代码
        """
        print("\n" + "="*60)
        print("运行性能测试")
        print("="*60)

        test_path = str(TESTS_DIR / "performance")
        cmd = self._build_pytest_command(test_path, extra_args)

        return self._run_command(cmd)

    def run_stability_tests(self, extra_args: Optional[List[str]] = None) -> (int):
        """
        运行稳定性测试

        Args:
            extra_args: 额外的pytest参数

        Returns:
            int: 退出代码
        """
        print("\n" + "="*60)
        print("运行稳定性测试")
        print("="*60)

        test_path = str(TESTS_DIR / "stability")
        cmd = self._build_pytest_command(test_path, extra_args)

        return self._run_command(cmd)

    def run_all_tests(self, extra_args: Optional[List[str]] = None) -> int:
        """
        运行所有测试

        Args:
            extra_args: 额外的pytest参数

        Returns:
            int: 退出代码
        """
        print("\n" + "="*60)
        print("运行所有测试")
        print("="*60)

        test_path = str(TESTS_DIR)
        cmd = self._build_pytest_command(test_path, extra_args)

        return self._run_command(cmd)

    def run_security_scan(self) -> int:
        """
        运行安全扫描（bandit, safety, pip-audit）

        Returns:
            int: 退出代码（0表示所有检查通过）
        """
        print("\n" + "="*60)
        print("运行安全扫描")
        print("="*60)

        exit_code = 0

        # 运行bandit
        print("\n[1/3] 运行bandit安全审计...")
        bandit_cmd = ["python", "-m", "bandit", "-r", "src/", "api/"]
        result = subprocess.run(bandit_cmd, cwd=PROJECT_ROOT)
        if result.returncode != 0:
            print("警告: bandit发现潜在安全问题")
            exit_code = 1

        # 运行safety
        print("\n[2/3] 运行safety依赖检查...")
...[安全检查继续]..."""
        print("运行safety依赖检查...")
        safety_cmd = ["python", "-m", "safety", "check"]
        result = subprocess.run(safety_cmd, cwd=PROJECT_ROOT)
        if result.returncode not in [0, 127]:  # 0=无问题，127=未安装
            print("警告: safety发现潜在依赖问题")
            exit_code = 1

        # 运行pip-audit
        print("\n[3/3] 运行pip-audit漏洞扫描...")
        audit_cmd = ["python", "-m", "pip-audit", "--output-format", "summary"]
        result = subprocess.run(audit_cmd, cwd=PROJECT_ROOT)
        if result.returncode != 0:
            print("警告: pip-audit发现潜在漏洞")
            exit_code = 1

        return exit_code

    def generate_coverage_report(self) -> int:
        """
        生成覆盖率报告

        Returns:
            int: 退出代码
        """
        print("\n" + "="*60)
        print("生成覆盖率报告")
        print("="*60)

        extra_args = [
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term",
            "--cov-report=xml",
        ]

        return self.run_all_tests(extra_args)

    def run_benchmarks(self) -> int:
        """
        运行基准测试

        Returns:
            int: 退出代码
        """
        print("\n" + "="*60)
        print("运行基准测试")
        print("="*60)

        test_path = str(TESTS_DIR / "performance")
        cmd = self._build_pytest_command(test_path, ["--benchmark-only"])
        return self._run_command(cmd)


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description="道义现实主义ABM系统测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python tests/test_runner.py unit
  python tests/test_runner.py integration
  python tests/test_runner.py security
  python tests/test_runner.py performance
  python tests/test_runner.py all
  python tests/test_runner.py all --parallel --cov-report=html
  python tests/test_runner.py security-scan
  python tests/test_runner.py coverage
        """
    )

    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "security", "performance", "stability", "all", "security-scan", "coverage", "benchmark"],
        help="测试类型"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )

    parser.add_argument(
        "-p", "--parallel",
        action="store_true",
        help="使用并行执行（pytest-xdist）"
    )

    parser.add_argument(
        "--cov-report",
        choices=["term", "html", "xml", "none"],
        default="none",
        help="覆盖率报告格式"
    )

    parser.add_argument(
        "-m", "--marker",
        help="只运行带有指定标记的测试（例如：-m slow）"
    )

    parser.add_argument(
        "-k", "--keyword",
        help="只运行匹配关键词的测试"
    )

    parser.add_argument(
        "-x", "--stop-on-failure",
        action="store_true",
        help="第一个失败后停止"
    )

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()

    runner = TestRunner(verbose=args.verbose, parallel=args.parallel)

    # 构建额外的pytest参数
    extra_args = []
    if args.cov_report != "none":
        extra_args.append("--cov=src")
        if args.cov_report == "html":
            extra_args.extend(["--cov-report=html"])
        elif args.cov_report == "term":
            extra_args.extend(["--cov-report=term-missing"])
        elif args.cov_report == "xml":
            extra_args.extend(["--cov-report=xml"])

    if args.marker:
        extra_args.append(f"-m {args.marker}")

    if args.keyword:
        extra_args.append(f"-k {args.keyword}")

    if args.stop_on_failure:
        extra_args.append("-x")

    # 根据测试类型运行相应的测试
    exit_code = 0

    if args.test_type == "unit":
        exit_code = runner.run_unit_tests(extra_args)
    elif args.test_type == "integration":
        exit_code = runner.run_integration_tests(extra_args)
    elif args.test_type == "security":
        exit_code = runner.run_security_tests(extra_args)
    elif args.test_type == "performance":
        exit_code = runner.run_performance_tests(extra_args)
    elif args.test_type == "stability":
        exit_code = runner.run_stability_tests(extra_args)
    elif args.test_type == "all":
        exit_code = runner.run_all_tests(extra_args)
    elif args.test_type == "security-scan":
        exit_code = runner.run_security_scan()
    elif args.test_type == "coverage":
        exit_code = runner.generate_coverage_report()
    elif args.test_type == "benchmark":
        exit_code = runner.run_benchmarks()

    # 显示总结
    print("\n" + "="*60)
    if exit_code == 0:
        print("✓ 测试成功完成")
    else:
        print(f"✗ 测试失败，退出代码：{exit_code}")
    print("="*60)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
