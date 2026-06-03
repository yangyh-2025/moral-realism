#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ID7 Action Cost Rebalancing Script
====================================
基于诊断结果，重新平衡行为成本，解决"威胁"行为占比过高的问题。

核心修改：
1. 提高"威胁"行为的国力损耗（从几乎为0增加到显著负值）
2. 降低外交/经济行为的成本，提高其收益
3. 增加军事行为的国力损耗
4. 提高经济手段的战略价值

Usage:
    python docs/rebalance_action_costs.py
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "abm_simulation.db")

# 行为成本调整方案
# 格式: (action_id, action_name, new_initiator_power_change, new_target_power_change, reason)
COST_ADJUSTMENTS = [
    # === 信息手段 ===
    (9,  "威胁",        -0.06,  -0.02,  "威胁消耗外交信誉，增加军备负担"),
    (13, "胁迫/强制",   -0.08,  -0.03,  "胁迫行为成本高，消耗国际信誉"),

    # === 外交手段 ===
    (1,  "发表公开声明",  0.01,   0.00,  "声明传递信号，低成本"),
    (2,  "谴责/批评",    -0.01,  -0.01,  "批评消耗一定外交关系"),
    (3,  "发展外交关系",  0.03,   0.02,  "外交关系建设带来长期收益"),
    (4,  "协商/磋商",    0.02,   0.02,  "协商建立互信"),
    (5,  "开展外交合作",  0.05,   0.04,  "外交合作带来战略收益"),
    (8,  "谋求/建立",    0.02,   0.01,  "建立新关系有战略价值"),
    (10, "要求/催要",    -0.01,   0.00,  "要求消耗一定外交资本"),
    (11, "表达不满/不赞成", -0.01,  -0.01,  "表达不满消耗关系"),
    (12, "拒绝",        -0.02,   0.00,  "拒绝消耗外交机会"),
    (14, "抗议",        -0.01,  -0.01,  "抗议消耗一定关系"),
    (16, "断绝关系",    -0.05,  -0.03,  "断绝关系成本高"),

    # === 经济手段 ===
    (6,  "开展实质性合作", 0.07,   0.05,  "实质合作提升双方国力（pec/irst）"),
    (7,  "提供援助",      0.05,   0.08,  "援助建立战略依赖，受援国国力提升"),

    # === 军事手段 ===
    (15, "展示军事姿态",  -0.08,  -0.02,  "军事姿态消耗军费（milex）"),
    (17, "攻击/袭击",    -0.10,  -0.08,  "攻击消耗大量军力"),
    (18, "伏击/突袭",    -0.08,  -0.10,  "突袭消耗军力但对敌方打击大"),
    (19, "交战/使用常规军事武力", -0.15, -0.12, "交战消耗巨大国力"),
    (20, "实施非常规模态打击", -0.20, -0.18, "非常规打击消耗极大"),
]


def apply_cost_adjustments():
    """Apply cost adjustments to the action_config table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("=" * 70)
    print("  ID7 Action Cost Rebalancing")
    print("=" * 70)

    # Show current costs
    print("\n  Current Action Costs:")
    print(f"  {'ID':>3} {'Name':<20} {'Current Init':>12} {'Current Tgt':>12}")
    print(f"  {'-'*3} {'-'*20} {'-'*12} {'-'*12}")
    for action_id, name, new_init, new_tgt, reason in COST_ADJUSTMENTS:
        c.execute('SELECT action_name, initiator_power_change, target_power_change FROM action_config WHERE action_id=?', (action_id,))
        row = c.fetchone()
        if row:
            print(f"  {action_id:>3} {row[0]:<20} {row[1]:>12.4f} {row[2]:>12.4f}")

    # Apply changes
    print("\n  Applying changes...")
    for action_id, name, new_init, new_tgt, reason in COST_ADJUSTMENTS:
        c.execute('''
            UPDATE action_config
            SET initiator_power_change = ?, target_power_change = ?
            WHERE action_id = ?
        ''', (new_init, new_tgt, action_id))
        print(f"  ✓ ID={action_id} ({name}): init={new_init:+.2f}, tgt={new_tgt:+.2f} | {reason}")

    conn.commit()

    # Show new costs
    print("\n  New Action Costs:")
    print(f"  {'ID':>3} {'Name':<20} {'New Init':>12} {'New Tgt':>12} {'Reason'}")
    print(f"  {'-'*3} {'-'*20} {'-'*12} {'-'*12} {'-'*30}")
    for action_id, name, new_init, new_tgt, reason in COST_ADJUSTMENTS:
        print(f"  {action_id:>3} {name:<20} {new_init:>+12.2f} {new_tgt:>+12.2f} {reason}")

    conn.close()

    print("\n" + "=" * 70)
    print("  Action cost rebalancing complete!")
    print("  Run a new simulation with Project 7 settings to test the effect.")
    print("=" * 70)


def show_cost_comparison():
    """Show before/after comparison."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("\n  Cost Comparison (Before → After):")
    print(f"  {'ID':>3} {'Name':<20} {'Old Init':>10} {'New Init':>10} {'Old Tgt':>10} {'New Tgt':>10}")
    print(f"  {'-'*3} {'-'*20} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    for action_id, name, new_init, new_tgt, reason in COST_ADJUSTMENTS:
        c.execute('SELECT initiator_power_change, target_power_change FROM action_config WHERE action_id=?', (action_id,))
        row = c.fetchone()
        if row:
            old_init, old_tgt = row
            print(f"  {action_id:>3} {name:<20} {old_init:>+10.4f} {new_init:>+10.2f} {old_tgt:>+10.4f} {new_tgt:>+10.2f}")

    conn.close()


if __name__ == "__main__":
    apply_cost_adjustments()
    show_cost_comparison()
