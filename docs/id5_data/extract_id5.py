"""Extract ID5 (project_id=5) simulation data from SQLite database."""

import sqlite3
import json
from collections import defaultdict
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "abm_simulation.db"
OUT_DIR = Path(__file__).resolve().parent

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

PROJECT_ID = 5

# Agent ID -> name mapping
AGENT_NAMES = {
    92: "Germany", 93: "Russia", 94: "UK", 95: "France", 96: "Italy",
    97: "Austria-Hungary", 98: "Ottoman Empire", 99: "Bulgaria",
    100: "Spain", 101: "Belgium", 102: "Greece", 103: "Sweden",
    104: "Netherlands", 105: "Romania", 106: "Portugal", 107: "Denmark",
    108: "Switzerland", 109: "Serbia", 110: "Norway",
}

# ── 1. Agent config ──────────────────────────────────────────────────────────
cur.execute("""
    SELECT agent_id, agent_name, initial_total_power, current_total_power,
           power_level, leader_type, cinc_year, region, milex, milper,
           irst, pec, tpop, upop, country_code
    FROM agent_config
    WHERE project_id = ?
    ORDER BY agent_id
""", (PROJECT_ID,))
agents = []
for r in cur.fetchall():
    agents.append({
        "agent_id": r["agent_id"],
        "agent_name": r["agent_name"],
        "initial_total_power": r["initial_total_power"],
        "current_total_power": r["current_total_power"],
        "power_level": r["power_level"],
        "leader_type": r["leader_type"],
        "cinc_year": r["cinc_year"],
        "region": r["region"],
        "milex": r["milex"],
        "milper": r["milper"],
        "irst": r["irst"],
        "pec": r["pec"],
        "tpop": r["tpop"],
        "upop": r["upop"],
        "country_code": r["country_code"],
    })

with open(OUT_DIR / "agents.json", "w", encoding="utf-8") as f:
    json.dump(agents, f, ensure_ascii=False, indent=2)
print(f"agents.json: {len(agents)} agents")

# ── 2. Follower relations ───────────────────────────────────────────────────
cur.execute("""
    SELECT round_num, follower_agent_id, leader_agent_id
    FROM follower_relation
    WHERE project_id = ?
    ORDER BY round_num, follower_agent_id
""", (PROJECT_ID,))
follower_rows = cur.fetchall()
follower_relations = []
for r in follower_rows:
    entry = {
        "round_num": r["round_num"],
        "follower_agent_id": r["follower_agent_id"],
        "follower_name": AGENT_NAMES.get(r["follower_agent_id"], str(r["follower_agent_id"])),
        "leader_agent_id": r["leader_agent_id"],
        "leader_name": AGENT_NAMES.get(r["leader_agent_id"]) if r["leader_agent_id"] else None,
    }
    follower_relations.append(entry)

with open(OUT_DIR / "follower_relations.json", "w", encoding="utf-8") as f:
    json.dump(follower_relations, f, ensure_ascii=False, indent=2)
print(f"follower_relations.json: {len(follower_relations)} records")

# ── 3. Action records (grouped by round, then by agent) ─────────────────────
cur.execute("""
    SELECT round_num, source_agent_id AS initiator_agent_id,
           target_agent_id, action_id, action_name, action_category,
           action_stage, respect_sov, initiator_power_change,
           target_power_change, decision_detail, action_content
    FROM action_record
    WHERE project_id = ?
    ORDER BY round_num, source_agent_id, action_stage
""", (PROJECT_ID,))
action_rows = cur.fetchall()

actions_grouped = defaultdict(lambda: defaultdict(list))
for r in action_rows:
    rn = r["round_num"]
    aid = r["initiator_agent_id"]
    actions_grouped[rn][aid].append({
        "target_agent_id": r["target_agent_id"],
        "target_name": AGENT_NAMES.get(r["target_agent_id"], str(r["target_agent_id"])) if r["target_agent_id"] else None,
        "action_id": r["action_id"],
        "action_name": r["action_name"],
        "action_category": r["action_category"],
        "action_stage": r["action_stage"],
        "respect_sov": bool(r["respect_sov"]) if r["respect_sov"] is not None else None,
        "initiator_power_change": r["initiator_power_change"],
        "target_power_change": r["target_power_change"],
        "decision_detail": r["decision_detail"],
        "action_content": r["action_content"],
    })

# Convert to sorted structure
actions_output = {}
for rn in sorted(actions_grouped.keys()):
    actions_output[rn] = {}
    for aid in sorted(actions_grouped[rn].keys()):
        label = f"{aid}_{AGENT_NAMES.get(aid, 'unknown')}"
        actions_output[rn][label] = actions_grouped[rn][aid]

with open(OUT_DIR / "actions.json", "w", encoding="utf-8") as f:
    json.dump(actions_output, f, ensure_ascii=False, indent=2)
print(f"actions.json: {len(action_rows)} total actions across {len(actions_output)} rounds")

# ── 4. Round info ───────────────────────────────────────────────────────────
cur.execute("""
    SELECT round_num, order_type, respect_sov_ratio AS sovereignty_ratio,
           has_leader, leader_agent_id, total_action_count,
           respect_sov_action_count, leader_follower_ratio
    FROM simulation_round
    WHERE project_id = ?
    ORDER BY round_num
""", (PROJECT_ID,))
rounds = []
for r in cur.fetchall():
    rounds.append({
        "round_num": r["round_num"],
        "order_type": r["order_type"],
        "sovereignty_ratio": r["sovereignty_ratio"],
        "has_leader": r["has_leader"],
        "leader_agent_id": r["leader_agent_id"],
        "leader_name": AGENT_NAMES.get(r["leader_agent_id"]) if r["leader_agent_id"] else None,
        "total_action_count": r["total_action_count"],
        "respect_sov_action_count": r["respect_sov_action_count"],
        "leader_follower_ratio": r["leader_follower_ratio"],
    })

with open(OUT_DIR / "rounds_info.json", "w", encoding="utf-8") as f:
    json.dump(rounds, f, ensure_ascii=False, indent=2)
print(f"rounds_info.json: {len(rounds)} rounds")

# ── 5. Summary ──────────────────────────────────────────────────────────────
# Per-agent action counts
per_agent_actions = defaultdict(int)
for r in action_rows:
    per_agent_actions[r["initiator_agent_id"]] += 1

per_agent_counts = {}
for aid in sorted(per_agent_actions.keys()):
    label = f"{aid}_{AGENT_NAMES.get(aid, 'unknown')}"
    per_agent_counts[label] = per_agent_actions[aid]

# Per-round follower counts (how many agents chose a leader)
per_round_followers = defaultdict(int)
per_round_leader = {}
for r in follower_rows:
    if r["leader_agent_id"] is not None:
        per_round_followers[r["round_num"]] += 1

per_round_follower_counts = {}
for rn in sorted(set(r["round_num"] for r in follower_rows)):
    per_round_follower_counts[rn] = per_round_followers[rn]

summary = {
    "project_id": PROJECT_ID,
    "total_rounds": len(rounds),
    "total_actions": len(action_rows),
    "total_agents": len(agents),
    "total_follower_records": len(follower_relations),
    "per_agent_action_counts": per_agent_counts,
    "per_round_follower_counts": per_round_follower_counts,
    "round_order_types": {r["round_num"]: r["order_type"] for r in rounds},
    "leaders_by_round": {
        r["round_num"]: {
            "leader_agent_id": r["leader_agent_id"],
            "leader_name": r["leader_name"],
            "has_leader": r["has_leader"],
        }
        for r in rounds
    },
}

with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"summary.json written")

conn.close()
print("\nDone. All files saved to:", OUT_DIR)
