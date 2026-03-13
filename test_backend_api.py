"""
后端API简单测试脚本

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""

def test_api_structure():
    """测试API结构是否正确"""
    print("Testing backend API structure...")

    # 测试1: 检查main.py是否创建
    try:
        with open("backend/main.py", "r", encoding="utf-8") as f:
            content = f.read()
            assert "FastAPI" in content
            print("  [OK] backend/main.py created successfully")
    except Exception as e:
        print(f"  [FAIL] backend/main.py test failed: {e}")
        return False

    # 测试2: 检查simulation.py
    try:
        with open("backend/api/simulation.py", "r", encoding="utf-8") as f:
            content = f.read()
            assert '@router.post("/start")' in content
            assert '@router.post("/pause")' in content
            assert '@router.post("/resume")' in content
            assert '@router.post("/stop")' in content
            assert '@router.get("/state")' in content
            print("  [OK] backend/api/simulation.py created successfully")
    except Exception as e:
        print(f"  [FAIL] backend/api/simulation.py test failed: {e}")
        return False

    # 测试3: 检查agents.py
    try:
        with open("backend/api/agents.py", "r", encoding="utf-8") as f:
            content = f.read()
            assert '@router.get("")' in content
            assert '@router.post("")' in content
            assert '@router.get("/{agent_id}")' in content
            assert '@router.put("/{agent_id}")' in content
            assert '@router.delete("/{agent_id}")' in content
            print("  [OK] backend/api/agents.py created successfully")
    except Exception as e:
        print(f"  [FAIL] backend/api/agents.py test failed: {e}")
        return False

    # 测试4: 检查events.py
    try:
        with open("backend/api/events.py", "r", encoding="utf-8") as f:
            content = f.read()
            assert '@router.get("")' in content
            assert '@router.post("")' in content
            print("  [OK] backend/api/events.py created successfully")
    except Exception as e:
        print(f"  [FAIL] backend/api/events.py test failed: {e}")
        return False

    # 测试5: 检查data.py
    try:
        with open("backend/api/data.py", "r", encoding="utf-8") as f:
            content = f.read()
            assert '@router.get("/agents")' in content
            print("  [OK] backend/api/data.py created successfully")
    except Exception as e:
        print(f"  [FAIL] backend/api/data.py test failed: {e}")
        return False

    # 测试6: 检查export.py
    try:
        with open("backend/api/export.py", "r", encoding="utf-8") as f:
            content = f.read()
            assert '@router.post("/export")' in content
            print("  [OK] backend/api/export.py created successfully")
    except Exception as e:
        print(f"  [FAIL] backend/api/export.py test failed: {e}")
        return False

    print("\n[SUCCESS] All API structure tests passed!")
    return True

def test_git_info():
    """测试Git信息是否正确"""
    print("\nChecking Git information...")

    # 检查所有文件中的Git用户信息
    files_to_check = [
        "backend/main.py",
        "backend/api/simulation.py",
        "backend/api/agents.py",
        "backend/api/events.py",
        "backend/api/data.py",
        "backend/api/export.py"
    ]

    for filepath in files_to_check:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                assert "yangyh-2025" in content
                assert "yangyuhang2667@163.com" in content
                print(f"  [OK] {filepath} contains correct Git user info")
        except Exception as e:
            print(f"  [FAIL] {filepath} Git info check failed: {e}")
            return False

    print("\n[SUCCESS] All Git info checks passed!")
    return True

if __name__ == "__main__":
    success = test_api_structure()
    if success:
        success = test_git_info()

    if success:
        print("\n" + "="*50)
        print("[SUCCESS] Agent E - Backend API implementation completed!")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("[FAIL] Tests failed, please check error messages")
        print("="*50)
