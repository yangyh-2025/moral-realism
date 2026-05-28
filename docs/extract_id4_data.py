# -*- coding: utf-8 -*-
"""Extract ID4 simulation data from database to JSON files."""
import sqlite3
import json
import os

db_path = r"C:/Users/yangy/myfile/PAPER/moral-ABM/python/data/abm_simulation.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

output_dir = r"C:/Users/yangy/myfile/PAPER/moral-ABM/python/docs/id4_data"
os.makedirs(output_dir, exist_ok=True)

def fix_encoding(s):
    """Fix mojibake encoding."""
    if s is None:
        return None
    if isinstance(s, str):
        try:
            return s.encode('latin1').decode('utf-8')
        except:
            return s
    return s

# 1. Project info
cursor.execute("SELECT project_id, project_name, scene_source, total_rounds, current_round, status, respect_sov_threshold, leader_threshold FROM simulation_project WHERE project_id = 4")
row = cursor.fetchone()
project_info = {
    "project_id": row[0],
    "project_name": fix_encoding(row[1]),
    "scene_source": fix_encoding(row[2]),
    "total_rounds": row[3],
    "current_round": row[4],
    "status": fix_encoding(row[5]),
    "respect_sov_threshold": row[6],
    "leader_threshold": row[7]
}

with open(os.path.join(output_dir, "project_info.json"), "w", encoding="utf-8") as f:
    json.dump(project_info, f, ensure_ascii=False, indent=2)

# 2. Agents
cursor.execute("SELECT agent_id, agent_name, country_code, initial_total_power, current_total_power, power_level, leader_type FROM agent_config WHERE project_id = 4 ORDER BY initial_total_power DESC")
agents = []
for row in cursor.fetchall():
    agents.append({
        "agent_id": row[0],
        "agent_name": fix_encoding(row[1]),
        "country_code": row[2],
        "initial_total_power": row[3],
        "current_total_power": row[4],
        "power_level": fix_encoding(row[5]),
        "leader_type": fix_encoding(row[6])
    })

with open(os.path.join(output_dir, "agents.json"), "w", encoding="utf-8") as f:
    json.dump(agents, f, ensure_ascii=False, indent=2)

# 3. Actions summary
cursor.execute("SELECT action_name, action_category, respect_sov, COUNT(*) as cnt FROM action_record WHERE project_id = 4 GROUP BY action_name ORDER BY cnt DESC")
actions = []
for row in cursor.fetchall():
    actions.append({
        "action_name": fix_encoding(row[0]),
        "action_category": fix_encoding(row[1]),
        "respect_sov": bool(row[2]),
        "count": row[3]
    })

with open(os.path.join(output_dir, "actions_summary.json"), "w", encoding="utf-8") as f:
    json.dump(actions, f, ensure_ascii=False, indent=2)

# 4. Total actions
cursor.execute("SELECT COUNT(*) FROM action_record WHERE project_id = 4")
total_actions = cursor.fetchone()[0]

# 5. Actions by category
cursor.execute("SELECT action_category, respect_sov, COUNT(*) FROM action_record WHERE project_id = 4 GROUP BY action_category, respect_sov")
actions_by_cat = []
for row in cursor.fetchall():
    actions_by_cat.append({
        "category": fix_encoding(row[0]),
        "respect_sov": bool(row[1]),
        "count": row[2]
    })

with open(os.path.join(output_dir, "actions_by_category.json"), "w", encoding="utf-8") as f:
    json.dump(actions_by_cat, f, ensure_ascii=False, indent=2)

# 6. Power history
cursor.execute("SELECT agent_id, round_num, round_start_power, round_end_power, round_change_value, round_change_rate FROM agent_power_history WHERE project_id = 4 ORDER BY agent_id, round_num")
power_history = []
for row in cursor.fetchall():
    power_history.append({
        "agent_id": row[0],
        "round_num": row[1],
        "round_start_power": row[2],
        "round_end_power": row[3],
        "round_change_value": row[4],
        "round_change_rate": row[5]
    })

with open(os.path.join(output_dir, "power_history.json"), "w", encoding="utf-8") as f:
    json.dump(power_history, f, ensure_ascii=False, indent=2)

# 7. Follower relations
cursor.execute("SELECT round_num, follower_agent_id, leader_agent_id FROM follower_relation WHERE project_id = 4 ORDER BY round_num")
followers = []
for row in cursor.fetchall():
    followers.append({
        "round_num": row[0],
        "follower_agent_id": row[1],
        "leader_agent_id": row[2]
    })

with open(os.path.join(output_dir, "follower_relations.json"), "w", encoding="utf-8") as f:
    json.dump(followers, f, ensure_ascii=False, indent=2)

# 8. Sovereignty rate by round
cursor.execute("""
    SELECT round_num,
           SUM(CASE WHEN respect_sov = 1 THEN 1 ELSE 0 END) as respect_count,
           COUNT(*) as total_count
    FROM action_record
    WHERE project_id = 4
    GROUP BY round_num
    ORDER BY round_num
""")
sov_by_round = []
for row in cursor.fetchall():
    sov_by_round.append({
        "round_num": row[0],
        "respect_count": row[1],
        "total_count": row[2],
        "respect_rate": round(row[1] / row[2], 4) if row[2] > 0 else 0
    })

with open(os.path.join(output_dir, "sovereignty_by_round.json"), "w", encoding="utf-8") as f:
    json.dump(sov_by_round, f, ensure_ascii=False, indent=2)

# 9. Actions by top agents (Germany=73, Russia=74, UK=75)
cursor.execute("""
    SELECT source_agent_id, target_agent_id, action_name, action_category, respect_sov, COUNT(*) as cnt
    FROM action_record
    WHERE project_id = 4 AND source_agent_id IN (73, 74, 75)
    GROUP BY source_agent_id, target_agent_id, action_name
    ORDER BY source_agent_id, cnt DESC
""")
agent_actions = []
for row in cursor.fetchall():
    agent_actions.append({
        "source_agent_id": row[0],
        "target_agent_id": row[1],
        "action_name": fix_encoding(row[2]),
        "action_category": fix_encoding(row[3]),
        "respect_sov": bool(row[4]),
        "count": row[5]
    })

with open(os.path.join(output_dir, "top_agent_actions.json"), "w", encoding="utf-8") as f:
    json.dump(agent_actions, f, ensure_ascii=False, indent=2)

# 10. Germany-Russia interactions by round
cursor.execute("""
    SELECT round_num, source_agent_id, target_agent_id, action_name, COUNT(*) as cnt
    FROM action_record
    WHERE project_id = 4
      AND ((source_agent_id = 73 AND target_agent_id = 74) OR (source_agent_id = 74 AND target_agent_id = 73))
    GROUP BY round_num, source_agent_id, action_name
    ORDER BY round_num, source_agent_id
""")
ger_rus = []
for row in cursor.fetchall():
    ger_rus.append({
        "round_num": row[0],
        "source_agent_id": row[1],
        "target_agent_id": row[2],
        "action_name": fix_encoding(row[3]),
        "count": row[4]
    })

with open(os.path.join(output_dir, "germany_russia_interactions.json"), "w", encoding="utf-8") as f:
    json.dump(ger_rus, f, ensure_ascii=False, indent=2)

# 11. Order changes
cursor.execute("SELECT round_num, order_type, respect_sov_ratio, has_leader, leader_agent_id, leader_follower_ratio FROM simulation_round WHERE project_id = 4 ORDER BY round_num")
rounds_info = []
for row in cursor.fetchall():
    rounds_info.append({
        "round_num": row[0],
        "order_type": fix_encoding(row[1]),
        "respect_sov_ratio": row[2],
        "has_leader": row[3],
        "leader_agent_id": row[4],
        "leader_follower_ratio": row[5]
    })

with open(os.path.join(output_dir, "rounds_info.json"), "w", encoding="utf-8") as f:
    json.dump(rounds_info, f, ensure_ascii=False, indent=2)

# 12. Leader summary by round
cursor.execute("""
    SELECT round_num, leader_agent_id, COUNT(*) as follower_count
    FROM follower_relation
    WHERE project_id = 4
    GROUP BY round_num, leader_agent_id
    ORDER BY round_num, follower_count DESC
""")
leader_summary = []
for row in cursor.fetchall():
    leader_summary.append({
        "round_num": row[0],
        "leader_agent_id": row[1],
        "follower_count": row[2]
    })

with open(os.path.join(output_dir, "leader_summary.json"), "w", encoding="utf-8") as f:
    json.dump(leader_summary, f, ensure_ascii=False, indent=2)

# Summary
summary = {
    "total_actions": total_actions,
    "project_info": project_info,
    "agent_count": len(agents),
    "action_types": len(actions)
}

with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("Data extraction complete. Files saved to:", output_dir)
conn.close()
