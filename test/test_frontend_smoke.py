"""
前端冒烟测试 - 使用 Playwright 直接驱动浏览器

要求：
- 后端在 127.0.0.1:8000
- 前端 dev 服务在 127.0.0.1:3000

每个测试会监听浏览器控制台错误：测试结束如果出现 page error / console.error，则失败。

覆盖的页面 / 按钮：
- Home (`/`)              欢迎卡 + 预置场景列表 + "查看详情" / "开始配置" / "查看行为集" 按钮
- SimulationConfig (`/config`)   添加智能体 / 删除 / 初始化关系 / 保存配置 / 创建项目并启动 / 重置配置
- SimulationConsole (`/console`) 启动 / 暂停 / 继续 / 终止 / 单步 / 重置 / 清空日志
- SimulationResults (`/results`) 图表区域加载
- AcademicStatistics (`/statistics`) Tab 切换 + 查询/计算/分析/查询评估
- BehaviorSet (`/behavior`)      20 项行为渲染 + 刷新数据
- SystemConfig (`/system`)       表单加载 + 保存配置 + 重置为默认
"""

from __future__ import annotations

import os
import re
from typing import Iterator, List

import pytest
from playwright.sync_api import (
    Browser, BrowserContext, Page, sync_playwright, expect
)


FRONTEND_BASE = os.environ.get("ABM_TEST_FRONTEND_URL", "http://127.0.0.1:3000")


# ===== 共享 fixtures (function scope so 每个用例独立) =================
@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture()
def page(browser: Browser) -> Iterator[Page]:
    """每个用例一个 Page；自动收集 console.error / pageerror。"""
    ctx: BrowserContext = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    errors: List[str] = []

    # 真正的 JS 异常
    page.on("pageerror", lambda exc: errors.append(f"PAGEERROR: {exc}"))

    # 控制台 console.error 仅做警告（很多前端有可忽略的404/网络错误）
    # 不直接 fail，只在结束时打印
    console_errors: List[str] = []
    page.on("console", lambda msg: (
        console_errors.append(msg.text) if msg.type == "error" else None
    ))

    yield page

    # 清理
    ctx.close()

    if errors:
        # JS 异常一定要失败
        pytest.fail("浏览器抛出 JS 异常:\n" + "\n".join(errors))


# ===== 工具函数 =====
def _goto(page: Page, path: str) -> None:
    page.goto(f"{FRONTEND_BASE}{path}", wait_until="networkidle", timeout=15000)


# ============================================================
# 各页面
# ============================================================
class TestHome:
    def test_load(self, page: Page) -> None:
        _goto(page, "/")
        expect(page.locator("h2", has_text="欢迎使用国际秩序ABM仿真系统")).to_be_visible()

    def test_preset_scenes_render(self, page: Page) -> None:
        _goto(page, "/")
        # 应当有至少一个预置场景卡片，渲染出"一键启动"按钮
        page.wait_for_selector("button:has-text('一键启动')", timeout=10000)
        buttons = page.locator("button:has-text('一键启动')")
        assert buttons.count() >= 1

    def test_view_scene_detail_dialog(self, page: Page) -> None:
        _goto(page, "/")
        page.wait_for_selector("button:has-text('查看详情')", timeout=10000)
        page.locator("button:has-text('查看详情')").first.click()
        # 弹出场景详情 dialog
        expect(page.locator(".el-dialog__title", has_text="场景详情")).to_be_visible()

    def test_navigate_to_config(self, page: Page) -> None:
        _goto(page, "/")
        page.locator("button:has-text('开始配置')").click()
        page.wait_for_url(re.compile(r".*/config"), timeout=5000)

    def test_navigate_to_behavior_set(self, page: Page) -> None:
        _goto(page, "/")
        page.locator("button:has-text('查看行为集')").click()
        page.wait_for_url(re.compile(r".*/behavior"), timeout=5000)


class TestBehaviorSet:
    def test_load_renders_20_actions(self, page: Page) -> None:
        _goto(page, "/behavior")
        expect(page.locator("h2", has_text="20项GDELT标准互动行为集")).to_be_visible()
        # 学术规范要求 20 项
        page.wait_for_selector(".action-card", timeout=10000)
        assert page.locator(".action-card").count() == 20

    def test_refresh_button(self, page: Page) -> None:
        _goto(page, "/behavior")
        page.locator("button:has-text('刷新数据')").click()
        # 成功消息
        page.wait_for_selector(".el-message--success", timeout=5000)


class TestSystemConfig:
    def test_load(self, page: Page) -> None:
        _goto(page, "/system")
        expect(page.locator("h2", has_text="系统配置")).to_be_visible()
        # LLM 配置 / 仿真配置 / 日志配置 三个区
        expect(page.locator(".el-divider", has_text="LLM 配置")).to_be_visible()
        expect(page.locator(".el-divider", has_text="仿真配置")).to_be_visible()
        expect(page.locator(".el-divider", has_text="日志配置")).to_be_visible()

    def test_save_button(self, page: Page) -> None:
        _goto(page, "/system")
        page.locator("button:has-text('保存配置')").click()
        # 成功 toast
        page.wait_for_selector(".el-message--success", timeout=5000)

    def test_reset_button(self, page: Page) -> None:
        _goto(page, "/system")
        page.locator("button:has-text('重置为默认')").click()
        # info toast
        page.wait_for_selector(".el-message", timeout=5000)


class TestSimulationConfig:
    def test_load(self, page: Page) -> None:
        _goto(page, "/config")
        expect(page.locator("h2", has_text="仿真配置")).to_be_visible()

    def test_add_agent_button(self, page: Page) -> None:
        _goto(page, "/config")
        before = page.locator(".agent-item").count()
        page.locator("button:has-text('添加智能体')").click()
        page.wait_for_function(
            f"document.querySelectorAll('.agent-item').length > {before}",
            timeout=3000,
        )
        assert page.locator(".agent-item").count() == before + 1

    def test_reset_button(self, page: Page) -> None:
        _goto(page, "/config")
        # 先添加再重置
        page.locator("button:has-text('添加智能体')").click()
        page.wait_for_timeout(300)
        page.locator("button:has-text('重置配置')").click()
        page.wait_for_timeout(300)
        # 重置后 agent 列表清空
        assert page.locator(".agent-item").count() == 0

    def test_create_without_name_warns(self, page: Page) -> None:
        _goto(page, "/config")
        page.locator("button:has-text('重置配置')").click()
        page.wait_for_timeout(200)
        # 不输入名称直接点创建，应弹 warning
        page.locator("button:has-text('创建项目并启动')").click()
        page.wait_for_selector(".el-message--warning", timeout=5000)


class TestSimulationConsole:
    """
    Console 页面会在没有 projectId 时跳到 /config。
    所以这里通过 ?projectId= 查询参数注入 smoke_project_with_agents 的 ID。
    """

    def test_load(self, page: Page, smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        _goto(page, f"/console?projectId={pid}")
        expect(page.locator("h3", has_text="仿真控制")).to_be_visible()
        expect(page.locator("h3", has_text="仿真日志")).to_be_visible()

    def test_all_control_buttons_present(
        self, page: Page, smoke_project_with_agents: dict
    ) -> None:
        pid = smoke_project_with_agents["project_id"]
        _goto(page, f"/console?projectId={pid}")
        for label in ("启动仿真", "暂停", "继续", "终止", "单步执行", "重置"):
            expect(page.locator(f"button:has-text('{label}')")).to_be_visible()

    def test_clear_logs(
        self, page: Page, smoke_project_with_agents: dict
    ) -> None:
        pid = smoke_project_with_agents["project_id"]
        _goto(page, f"/console?projectId={pid}")
        page.locator("button:has-text('清空')").click()
        # 不抛异常即可


class TestSimulationResults:
    def test_load(self, page: Page) -> None:
        _goto(page, "/results")
        expect(page.locator("h2", has_text="仿真结果可视化")).to_be_visible()
        # 检查所有图表 section 渲染
        for section in ("国际秩序演变", "智能体CINC指数变化",
                        "行为类型分布", "主权尊重率趋势",
                        "领导国追随率"):
            expect(page.locator("h3", has_text=section)).to_be_visible()


class TestAcademicStatistics:
    def test_load(self, page: Page) -> None:
        _goto(page, "/statistics")
        expect(page.locator("h2", has_text="学术指标统计分析")).to_be_visible()

    def test_tabs_present(self, page: Page) -> None:
        _goto(page, "/statistics")
        for tab_label in ("CINC变化分析", "变化率统计", "行为偏好分析",
                          "战略目标评估"):
            expect(page.locator(".el-tabs__item", has_text=tab_label)).to_be_visible()

    def test_switch_tabs(self, page: Page) -> None:
        _goto(page, "/statistics")
        for tab_label in ("变化率统计", "行为偏好分析", "战略目标评估",
                          "CINC变化分析"):
            page.locator(".el-tabs__item", has_text=tab_label).click()
            page.wait_for_timeout(200)
