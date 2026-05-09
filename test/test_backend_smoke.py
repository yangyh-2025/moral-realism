"""
后端冒烟测试 - 覆盖所有 API 端点

按功能分类的 TestClass 结构：
- TestRoot                   /, /health, /docs
- TestPresetScene            /api/v1/preset-scene/...
- TestActionConfig           /api/v1/action-config/...
- TestCinc                   /api/v1/cinc/...
- TestSystemConfig           /api/v1/system/config
- TestProject                /api/v1/simulation/project*
- TestAgent                  /api/v1/simulation/project/{pid}/agent*
- TestStrategicRelationship  /api/v1/strategic-relationships/...
- TestSimulationControl      /api/v1/simulation/{pid}/{start,step,pause,resume,stop,reset}
- TestRoundDetail            /api/v1/simulation/{pid}/round/{n}
- TestStatistics             /api/v1/simulation/{pid}/stats/...
- TestAnalysis               /api/v1/analysis/{pid}/...

依赖 conftest.py 中的 fixtures：
- client: 共享 httpx Client
- smoke_project: 自动创建/清理的测试项目
- smoke_project_with_agents: 带 3 个 agent + 初始化关系的项目
"""

from __future__ import annotations

import time

import httpx
import pytest


API = "/api/v1"


# ========================================================================
# Root / health
# ========================================================================
class TestRoot:
    def test_health(self, client: httpx.Client) -> None:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json().get("status") == "healthy"

    def test_root(self, client: httpx.Client) -> None:
        r = client.get("/")
        # 返回前端 index.html 或系统信息
        assert r.status_code == 200

    def test_openapi_docs(self, client: httpx.Client) -> None:
        r = client.get("/docs")
        assert r.status_code == 200

    def test_openapi_json(self, client: httpx.Client) -> None:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        data = r.json()
        assert "paths" in data


# ========================================================================
# 预置场景
# ========================================================================
class TestPresetScene:
    def test_list(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/preset-scene/list")
        assert r.status_code == 200
        scenes = r.json()
        assert isinstance(scenes, list)
        # 系统至少应当有默认场景
        assert len(scenes) >= 1
        s = scenes[0]
        for k in ("scene_id", "scene_name", "scene_desc", "total_rounds",
                 "agent_config_json", "is_default"):
            assert k in s

    def test_get_by_id(self, client: httpx.Client) -> None:
        scenes = client.get(f"{API}/preset-scene/list").json()
        if not scenes:
            pytest.skip("无预置场景可测")
        scene_id = scenes[0]["scene_id"]
        r = client.get(f"{API}/preset-scene/{scene_id}")
        assert r.status_code == 200
        assert r.json()["scene_id"] == scene_id

    def test_get_not_found(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/preset-scene/999999")
        assert r.status_code == 404

    def test_create_project_from_scene(self, client: httpx.Client) -> None:
        scenes = client.get(f"{API}/preset-scene/list").json()
        if not scenes:
            pytest.skip("无预置场景可测")
        scene_id = scenes[0]["scene_id"]
        payload = {
            "scene_id": scene_id,
            "project_name": f"smoke_scene_{int(time.time())}",
            "project_desc": "from preset scene",
        }
        r = client.post(f"{API}/preset-scene/{scene_id}/create-project", json=payload)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "project_id" in body
        # 清理
        client.delete(f"{API}/simulation/project/{body['project_id']}")


# ========================================================================
# 行为配置
# ========================================================================
class TestActionConfig:
    def test_list(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/action-config/list")
        assert r.status_code == 200
        actions = r.json()
        # 学术模型规定 20 项标准行为
        assert len(actions) == 20
        for a in actions:
            for k in ("action_id", "action_name", "action_en_name",
                     "action_category", "respect_sov", "is_initiative",
                     "is_response"):
                assert k in a

    def test_get_by_id(self, client: httpx.Client) -> None:
        for aid in (1, 10, 20):
            r = client.get(f"{API}/action-config/{aid}")
            assert r.status_code == 200
            assert r.json()["action_id"] == aid

    def test_get_not_found(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/action-config/9999")
        assert r.status_code == 404


# ========================================================================
# CINC 数据
# ========================================================================
class TestCinc:
    def test_countries(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/cinc/countries")
        assert r.status_code == 200
        countries = r.json()
        assert isinstance(countries, list)
        assert len(countries) > 0

    def test_years(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/cinc/years")
        assert r.status_code == 200
        years = r.json()
        assert isinstance(years, list)
        assert all(isinstance(y, int) for y in years)

    def test_data_by_country_code(self, client: httpx.Client) -> None:
        # USA = 2
        r = client.get(f"{API}/cinc/data", params={"country_code": 2, "year": 2016})
        assert r.status_code == 200
        data = r.json()
        for k in ("ccode", "year", "milex", "milper", "irst",
                 "pec", "tpop", "upop", "cinc"):
            assert k in data

    def test_data_by_stateabb(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/cinc/data", params={"stateabb": "USA", "year": 2016})
        assert r.status_code == 200

    def test_data_missing_params(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/cinc/data", params={"year": 2016})
        assert r.status_code == 400

    def test_data_not_found(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/cinc/data",
                       params={"country_code": 99999, "year": 2016})
        assert r.status_code == 404

    def test_by_year(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/cinc/by-year/2016")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ========================================================================
# 系统配置
# ========================================================================
class TestSystemConfig:
    def test_get(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/system/config")
        assert r.status_code == 200
        cfg = r.json()
        for k in ("llmModelName", "llmTimeout", "llmMaxRetries",
                 "simulationConcurrency", "logLevel"):
            assert k in cfg

    def test_update(self, client: httpx.Client) -> None:
        # 先取当前配置
        before = client.get(f"{API}/system/config").json()
        original_concurrency = before["simulationConcurrency"]

        # 更新并发度
        new_value = 7 if original_concurrency != 7 else 8
        r = client.put(
            f"{API}/system/config", json={"simulationConcurrency": new_value}
        )
        assert r.status_code == 200, r.text
        assert r.json()["simulationConcurrency"] == new_value

        # 还原
        client.put(
            f"{API}/system/config",
            json={"simulationConcurrency": original_concurrency},
        )


# ========================================================================
# 项目 CRUD
# ========================================================================
class TestProject:
    def test_list(self, client: httpx.Client, smoke_project: dict) -> None:
        r = client.get(f"{API}/simulation/project/list")
        assert r.status_code == 200
        projects = r.json()
        ids = [p["project_id"] for p in projects]
        assert smoke_project["project_id"] in ids

    def test_get(self, client: httpx.Client, smoke_project: dict) -> None:
        pid = smoke_project["project_id"]
        r = client.get(f"{API}/simulation/project/{pid}")
        assert r.status_code == 200
        assert r.json()["project_id"] == pid

    def test_get_not_found(self, client: httpx.Client) -> None:
        r = client.get(f"{API}/simulation/project/999999")
        assert r.status_code == 404

    def test_update(self, client: httpx.Client, smoke_project: dict) -> None:
        pid = smoke_project["project_id"]
        new_desc = f"updated_{int(time.time())}"
        payload = {
            "project_name": smoke_project["project_name"],
            "project_desc": new_desc,
            "total_rounds": smoke_project["total_rounds"],
            "scene_source": smoke_project["scene_source"],
        }
        r = client.put(f"{API}/simulation/project/{pid}", json=payload)
        assert r.status_code == 200, r.text
        assert r.json()["project_desc"] == new_desc

    def test_create_and_delete(self, client: httpx.Client) -> None:
        payload = {
            "project_name": f"to_delete_{int(time.time())}",
            "total_rounds": 5,
            "scene_source": "自定义",
        }
        r = client.post(f"{API}/simulation/project", json=payload)
        assert r.status_code == 200, r.text
        pid = r.json()["project_id"]

        r = client.delete(f"{API}/simulation/project/{pid}")
        assert r.status_code == 200

        r = client.get(f"{API}/simulation/project/{pid}")
        assert r.status_code == 404


# ========================================================================
# 智能体 CRUD（依赖 smoke_project_with_agents）
# ========================================================================
class TestAgent:
    def test_list(self, client: httpx.Client,
                  smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/simulation/project/{pid}/agent/list")
        assert r.status_code == 200
        agents = r.json()
        assert len(agents) == 3
        for a in agents:
            for k in ("agent_id", "agent_name", "region",
                     "current_total_power", "power_level"):
                assert k in a

    def test_get_one(self, client: httpx.Client,
                     smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        aid = smoke_project_with_agents["agent_ids"][0]
        r = client.get(f"{API}/simulation/project/{pid}/agent/{aid}")
        assert r.status_code == 200
        assert r.json()["agent_id"] == aid

    def test_get_not_found(self, client: httpx.Client,
                           smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/simulation/project/{pid}/agent/999999")
        assert r.status_code == 404

    def test_update(self, client: httpx.Client,
                    smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        aid = smoke_project_with_agents["agent_ids"][0]
        agent = client.get(
            f"{API}/simulation/project/{pid}/agent/{aid}"
        ).json()

        new_name = f"updated_{int(time.time())}"
        payload = {
            "agent_name": new_name,
            "region": agent["region"],
            "milex": agent["milex"], "milper": agent["milper"],
            "irst": agent["irst"], "pec": agent["pec"],
            "tpop": agent["tpop"], "upop": agent["upop"],
            "country_code": agent.get("country_code"),
            "cinc_year": agent.get("cinc_year"),
            "leader_type": agent["leader_type"],
        }
        r = client.put(f"{API}/simulation/project/{pid}/agent/{aid}", json=payload)
        assert r.status_code == 200, r.text
        assert r.json()["agent_name"] == new_name

    def test_add_and_delete(self, client: httpx.Client,
                            smoke_project: dict) -> None:
        pid = smoke_project["project_id"]
        payload = {
            "agent_name": f"throwaway_{int(time.time())}",
            "region": "亚洲",
            "milex": 100.0, "milper": 100.0, "irst": 10.0,
            "pec": 1000.0, "tpop": 5000.0, "upop": 3000.0,
            "country_code": 740, "cinc_year": 2016,
            "leader_type": None,
        }
        r = client.post(f"{API}/simulation/project/{pid}/agent", json=payload)
        assert r.status_code == 200, r.text
        aid = r.json()["agent_id"]

        r = client.delete(f"{API}/simulation/project/{pid}/agent/{aid}")
        assert r.status_code == 200


# ========================================================================
# 战略关系
# ========================================================================
class TestStrategicRelationship:
    def test_get_all(self, client: httpx.Client,
                     smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/strategic-relationships/project/{pid}")
        assert r.status_code == 200
        body = r.json()
        # 初始化关系后应当返回非空映射
        assert isinstance(body, dict)
        assert len(body) > 0

    def test_get_for_specific_agent(self, client: httpx.Client,
                                    smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        aid = smoke_project_with_agents["agent_ids"][0]
        r = client.get(
            f"{API}/strategic-relationships/project/{pid}",
            params={"agent_id": aid},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["agent_id"] == aid
        assert "relationships" in body

    def test_set_relationship(self, client: httpx.Client,
                              smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        ids = smoke_project_with_agents["agent_ids"]
        # 超级大国(0) <-> 大国(1)，允许且属于学术约束允许的配对
        r = client.post(
            f"{API}/strategic-relationships/project/{pid}",
            json={"source_id": ids[0], "target_id": ids[1],
                  "relationship_type": "盟友关系"},
        )
        assert r.status_code == 200, r.text

    def test_initialize(self, client: httpx.Client,
                        smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.post(
            f"{API}/strategic-relationships/project/{pid}/initialize"
        )
        assert r.status_code == 200

    def test_get_changes(self, client: httpx.Client,
                         smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/strategic-relationships/project/{pid}/changes")
        assert r.status_code == 200
        assert "changes" in r.json()


# ========================================================================
# 仿真控制（不实际跑 LLM 轮）
# ========================================================================
class TestSimulationControl:
    """
    控制端点冒烟（start/step/pause/resume/stop/reset）。
    跑 1 步真实仿真会调 LLM——慢且可能失败。
    这里只验证 start 后的状态切换 + reset 恢复。
    """

    def test_reset_initial(self, client: httpx.Client,
                           smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.post(f"{API}/simulation/{pid}/reset")
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "未启动"

    def test_step_when_not_running(self, client: httpx.Client,
                                   smoke_project_with_agents: dict) -> None:
        """step 在未启动状态应返回业务级提示。"""
        pid = smoke_project_with_agents["project_id"]
        client.post(f"{API}/simulation/{pid}/reset")
        r = client.post(f"{API}/simulation/{pid}/step")
        assert r.status_code == 200, r.text
        body = r.json()
        # 服务端应返回带状态信息的 dict
        assert isinstance(body, dict)

    def test_pause_resume_stop_chain(self, client: httpx.Client,
                                     smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]

        # reset 到初始
        r = client.post(f"{API}/simulation/{pid}/reset")
        assert r.status_code == 200

        # start -> 后台开始跑
        r = client.post(f"{API}/simulation/{pid}/start")
        assert r.status_code == 200, r.text
        assert r.json()["status"] in ("运行中", "已完成")

        # 立即 pause
        r = client.post(f"{API}/simulation/{pid}/pause")
        assert r.status_code == 200
        assert r.json()["status"] == "暂停"

        # resume
        r = client.post(f"{API}/simulation/{pid}/resume")
        assert r.status_code == 200
        assert r.json()["status"] == "运行中"

        # stop
        r = client.post(f"{API}/simulation/{pid}/stop")
        assert r.status_code == 200
        assert r.json()["status"] == "已终止"

        # reset 还原
        r = client.post(f"{API}/simulation/{pid}/reset")
        assert r.status_code == 200


# ========================================================================
# 单轮详情 / LLM prompts
# ========================================================================
class TestRoundDetail:
    def test_round_detail_existing(self, client: httpx.Client) -> None:
        """对任一已有轮次拉取详情。优先用历史项目 2，若不存在则跳过。"""
        # 取项目列表，找一个有轮次数据的
        projects = client.get(f"{API}/simulation/project/list").json()
        valid = [p for p in projects if p.get("current_round", 0) >= 1]
        if not valid:
            pytest.skip("无已运行轮次的项目可测")
        pid = valid[0]["project_id"]
        r = client.get(f"{API}/simulation/{pid}/round/1")
        assert r.status_code == 200
        body = r.json()
        for k in ("round_num", "actions", "total_actions",
                 "respect_sov_actions", "follower_relations"):
            assert k in body

    def test_llm_prompts(self, client: httpx.Client) -> None:
        """LLM prompt 拉取——返回列表（可能为空）。"""
        projects = client.get(f"{API}/simulation/project/list").json()
        if not projects:
            pytest.skip("无项目可测")
        pid = projects[0]["project_id"]
        r = client.get(f"{API}/simulation/project/{pid}/round/1/llm-prompts")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ========================================================================
# 统计
# ========================================================================
class TestStatistics:
    """以测试项目为主，对带数据的历史项目仅做表面验证。"""

    def test_power_history(self, client: httpx.Client,
                           smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/simulation/{pid}/stats/power-history")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_power_growth_rate(self, client: httpx.Client,
                               smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/simulation/{pid}/stats/power-growth-rate")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_action_preference(self, client: httpx.Client,
                               smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/simulation/{pid}/stats/action-preference")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_order_evolution(self, client: httpx.Client,
                             smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/simulation/{pid}/stats/order-evolution")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_round_detail_stats_returns_404_for_missing(
        self, client: httpx.Client, smoke_project_with_agents: dict
    ) -> None:
        pid = smoke_project_with_agents["project_id"]
        # smoke project 没跑轮次，应当返回 404
        r = client.get(
            f"{API}/simulation/{pid}/stats/round-detail",
            params={"round_num": 999},
        )
        assert r.status_code == 404

    def test_goal_evaluations(self, client: httpx.Client,
                              smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/simulation/{pid}/stats/goal-evaluations")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_goal_evaluation_trend(self, client: httpx.Client,
                                   smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        aid = smoke_project_with_agents["agent_ids"][0]
        r = client.get(
            f"{API}/simulation/{pid}/stats/goal-evaluation-trend/{aid}"
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_agent_relations(self, client: httpx.Client,
                             smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/simulation/{pid}/stats/agent-relations")
        assert r.status_code == 200
        body = r.json()
        for k in ("nodes", "links", "round_num"):
            assert k in body


# ========================================================================
# 后验分析
# ========================================================================
class TestAnalysis:
    def test_behavior(self, client: httpx.Client,
                      smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/analysis/{pid}/behavior")
        assert r.status_code == 200
        assert isinstance(r.json(), dict)

    def test_power(self, client: httpx.Client,
                   smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/analysis/{pid}/power")
        assert r.status_code == 200
        assert isinstance(r.json(), dict)

    def test_order(self, client: httpx.Client,
                   smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/analysis/{pid}/order")
        assert r.status_code == 200
        assert isinstance(r.json(), dict)

    def test_leader(self, client: httpx.Client,
                    smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/analysis/{pid}/leader")
        assert r.status_code == 200
        assert isinstance(r.json(), dict)

    def test_full_report(self, client: httpx.Client,
                         smoke_project_with_agents: dict) -> None:
        pid = smoke_project_with_agents["project_id"]
        r = client.get(f"{API}/analysis/{pid}/report")
        assert r.status_code == 200
        assert isinstance(r.json(), dict)
