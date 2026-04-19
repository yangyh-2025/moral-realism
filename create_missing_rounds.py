# -*- coding: utf-8 -*-
"""Create missing round records based on action_record data"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "abm_simulation.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all distinct rounds from action_record
cursor.execute("""
    SELECT DISTINCT project_id, round_num
    FROM action_record
    ORDER BY project_id, round_num
""")

rounds = cursor.fetchall()
print(f"Found {len(rounds)} (project_id, round_num) pairs in action_record")

# For each round, check if it exists in simulation_round
created = 0
updated = 0

for project_id, round_num in rounds:
    # Check if round exists
    cursor.execute("""
        SELECT round_id FROM simulation_round
        WHERE project_id = ? AND round_num = ?
    """, (project_id, round_num))
    existing = cursor.fetchone()

    if not existing:
        # Create round record
        # Get action stats for this round
        cursor.execute("""
            SELECT COUNT(*) as total_actions,
                   SUM(CASE WHEN respect_sov IN ('true', '1', 'yes') THEN 1 ELSE 0 END) as respect_count
            FROM action_record
            WHERE project_id = ? AND round_num = ?
        """, (project_id, round_num))
        action_stats = cursor.fetchone()

        total_actions = action_stats[0] or 0
        respect_count = action_stats[1] or 0
        respect_ratio = respect_count / total_actions if total_actions > 0 else 0.0

        cursor.execute("""
            INSERT INTO simulation_round (
                project_id, round_num, total_action_count,
                respect_sov_action_count, respect_sov_ratio,
                has_leader, order_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, round_num, total_actions,
            respect_count, respect_ratio,
            "false", "未判定"
        ))

        created += 1
        print(f"Created round {round_num} for project {project_id}: {total_actions} actions")
    else:
        # Update round stats if needed
        cursor.execute("""
            SELECT COUNT(*) as total_actions,
                   SUM(CASE WHEN respect_sov IN ('true', '1', 'yes') THEN 1 ELSE 0 END) as respect_count
            FROM action_record
            WHERE project_id = ? AND round_num = ?
        """, (project_id, round_num))
        action_stats = cursor.fetchone()

        cursor.execute("""
            SELECT total_action_count, respect_sov_action_count, respect_sov_ratio
            FROM simulation_round
            WHERE project_id = ? AND round_num = ?
        """, (project_id, round_num))
        current_stats = cursor.fetchone()

        if action_stats[0] != current_stats[0] or action_stats[1] != current_stats[1]:
            total_actions = action_stats[0]
            respect_count = action_stats[1]
            respect_ratio = respect_count / total_actions if total_actions > 0 else 0.0

            cursor.execute("""
                UPDATE simulation_round
                SET total_action_count = ?,
                    respect_sov_action_count = ?,
                    respect_sov_ratio = ?
                WHERE project_id = ? AND round_num = ?
            """, (total_actions, respect_count, respect_ratio, project_id, round_num))

            updated += 1
            print(f"Updated round {round_num} for project {project_id}: {total_actions} actions")

conn.commit()

print(f"\nTotal rounds created: {created}")
print(f"Total rounds updated: {updated}")

# Verify
cursor.execute("""
    SELECT project_id, COUNT(DISTINCT round_num)
    FROM simulation_round
    GROUP BY project_id
""")

print("\nRound counts per project:")
for row in cursor.fetchall():
    print(f"  Project {row[0]}: {row[1]} rounds")

conn.close()
