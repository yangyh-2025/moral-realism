"""
重构验证测试脚本

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import sys
import os

# 确保能导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase1():
    """阶段一验证：根目录冗余目录已删除"""
    print("=" * 50)
    print("阶段一验证：根目录冗余目录删除")
    print("=" * 50)

    api_exists = os.path.exists("api")
    services_exists = os.path.exists("services")
    utils_exists = os.path.exists("utils")

    print(f"api/ 目录存在: {api_exists}")
    print(f"services/ 目录存在: {services_exists}")
    print(f"utils/ 目录存在: {utils_exists}")

    phase1_passed = not (api_exists or services_exists or utils_exists)
    print(f"\n阶段一验证结果: {'✅ 通过' if phase1_passed else '❌ 失败'}")
    return phase1_passed


def test_phase2():
    """阶段二验证：后端架构优化"""
    print("\n" + "=" * 50)
    print("阶段二验证：后端架构优化")
    print("=" * 50)

    passed = []

    # 1. 检查新文件是否存在
    print("\n1. 检查新文件创建...")
    model_exists = os.path.exists("backend/models/export.py")
    service_exists = os.path.exists("backend/services/export_service.py")
    print(f"   backend/models/export.py 存在: {model_exists}")
    print(f"   backend/services/export_service.py 存在: {service_exists}")
    passed.append(model_exists and service_exists)

    # 2. 测试模型导入
    print("\n2. 测试模型导入...")
    try:
        from backend.models.export import ExportFormat, ExportFilters, ExportResult, ExportRequest
        print("   ExportFormat, ExportFilters, ExportResult, ExportRequest 导入成功 ✅")
        passed.append(True)
    except Exception as e:
        print(f"   模型导入失败: {e} ❌")
        passed.append(False)

    # 3. 测试服务导入
    print("\n3. 测试服务导入...")
    try:
        from backend.services.export_service import ExportService
        print("   ExportService 导入成功 ✅")
        passed.append(True)
    except Exception as e:
        print(f"   服务导入失败: {e} ❌")
        passed.append(False)

    # 4. 测试ExportService功能
    print("\n4. 测试ExportService功能...")
    try:
        import asyncio
        from backend.services.export_service import ExportService
        from backend.models.export import ExportFormat, ExportFilters

        service = ExportService()
        result = asyncio.run(service.export_simulation_data(
            simulation_id="test_001",
            format=ExportFormat.JSON,
            filters=ExportFilters()
        ))

        if result.success:
            print(f"   导出功能测试成功 ✅")
            print(f"   结果: {result.message}")
            passed.append(True)
        else:
            print(f"   导出失败: {result.message} ❌")
            passed.append(False)
    except Exception as e:
        print(f"   导出功能测试失败: {e} ❌")
        passed.append(False)

    # 5. 测试路由导入
    print("\n5. 测试路由导入...")
    try:
        from backend.api.export import router
        print("   export router 导入成功 ✅")
        print(f"   路由数量: {len(router.routes)}")
        passed.append(True)
    except Exception as e:
        print(f"   路由导入失败: {e} ❌")
        passed.append(False)

    # 6. 测试main.py导入
    print("\n6. 测试main.py导入...")
    try:
        from backend.main import app
        print("   backend.main.app 导入成功 ✅")
        passed.append(True)
    except Exception as e:
        print(f"   main.py导入失败: {e} ❌")
        passed.append(False)

    phase2_passed = all(passed)
    print(f"\n阶段二验证结果: {'✅ 通过' if phase2_passed else '❌ 失败'}")
    print(f"通过项: {sum(passed)}/{len(passed)}")
    return phase2_passed


def test_code_refactoring():
    """测试代码重构结果"""
    print("\n" + "=" * 50)
    print("代码重构结果统计")
    print("=" * 50)

    def count_lines(filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        return 0

    files = {
        "backend/api/export.py": "导出路由（应简化）",
        "backend/services/export_service.py": "导出服务（新）",
        "backend/models/export.py": "导出模型（新）"
    }

    for filepath, desc in files.items():
        lines = count_lines(filepath)
        print(f"{desc}: {lines} 行")


def main():
    """主测试函数"""
    print("项目重构验证测试")
    print("=" * 50)

    phase1 = test_phase1()
    phase2 = test_phase2()
    test_code_refactoring()

    print("\n" + "=" * 50)
    print("总体验证结果")
    print("=" * 50)
    print(f"阶段一（清理冗余目录）: {'✅ 通过' if phase1 else '❌ 失败'}")
    print(f"阶段二（后端架构优化）: {'✅ 通过' if phase2 else '❌ 失败'}")

    if phase1 and phase2:
        print("\n🎉 所有验证通过！重构成功！")
        return 0
    else:
        print("\n部分验证失败，请检查上述错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
