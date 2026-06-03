#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ID7 ABM Simulation Validation Script
======================================
验证 Project 7（一战前1913年欧洲）仿真结果与历史事实的一致性。

Dimension 1: Following Behavior F1 (per-round, per-country)
Dimension 2: Action Distribution F1 (per-round, per-country)

追随的定义（来自模型）：
"追随是对某国在特定议题上的领导偏好，不等同于战略同盟关系。
 你的战略关系（盟友/伙伴/冲突/战争）代表双边外交立场，
 而追随代表你在多边议题上的立场选择。"

Ground truth 设计原则：
1. 追随≠同盟：基于各国在实际外交议题上的政策协调对象，而非同盟阵营
2. 大国是被追随者（leader），不追随他人
3. 中等强国和小国有各自的追随倾向，基于历史外交行为
4. 追随是"单一议题追随"，同一国家可在不同议题上追随不同领导者

Usage:
    python docs/validate_id7_f1.py
"""

import json
import os
import sys
import sqlite3
from collections import defaultdict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "abm_simulation.db")
OUTPUT_JSON = os.path.join(BASE_DIR, "id7_validation_results.json")

PROJECT_ID = 7

# Project 7 agent ID -> name mapping (from database)
AGENT_NAMES = {
    130: "Germany",       # code=255, 强国甲, 霸权型, power=0.2370
    131: "Russia",        # code=365, 强国乙, 强权型, power=0.1892
    132: "UK",            # code=200, 强国丙, 王道型, power=0.1872
    133: "France",        # code=220, 中等国甲, power=0.1065
    134: "Austria-Hungary", # code=300, 中等国乙, power=0.0734
    135: "Italy",         # code=325, 中等国丙, power=0.0521
    136: "Ottoman Empire", # code=640, 小国甲, power=0.0262
    137: "Bulgaria",      # code=355, 小国丙, power=0.0203
    138: "Spain",         # code=230, 小国丁, power=0.0237
    139: "Belgium",       # code=211, 小国乙, power=0.0244
    140: "Serbia",        # code=350, 小国己, power=0.0099
    141: "Romania",       # code=380, 小国庚, power=0.0113
    142: "Norway",        # code=210, 小国辛, power=0.0113
    143: "Greece",        # code=360, 小国壬, power=0.0082
    144: "Portugal",      # code=235, 小国癸, power=0.0057
    145: "Netherlands",   # code=390, 小国子, power=0.0041
    146: "Switzerland",   # code=225, 小国丑, power=0.0041
    147: "Denmark",       # code=345, 小国寅, power=0.0028
    148: "Poland",        # code=385, 小国卯, power=0.0026
}

ALL_AGENT_IDS = sorted(AGENT_NAMES.keys())

# Action category mapping (action_id -> category)
ACTION_CATEGORY_MAP = {
    1: "Diplomatic",   # 发表公开声明
    2: "Diplomatic",   # 谴责/批评
    3: "Diplomatic",   # 发展外交关系
    4: "Diplomatic",   # 协商/磋商
    5: "Diplomatic",   # 开展外交合作
    6: "Economic",     # 开展实质性合作
    7: "Economic",     # 提供援助
    8: "Diplomatic",   # 谋求/建立
    9: "Information",  # 威胁
    10: "Diplomatic",  # 要求/催要
    11: "Diplomatic",  # 表达不满/不赞成
    12: "Diplomatic",  # 拒绝
    13: "Information", # 胁迫/强制
    14: "Diplomatic",  # 抗议
    15: "Military",    # 展示军事姿态
    16: "Diplomatic",  # 断绝关系
    17: "Military",    # 攻击/袭击
    18: "Military",    # 伏击/突袭
    19: "Military",    # 交战/使用常规军事武力
    20: "Military",    # 实施非常规模态打击
}

ALL_CATEGORIES = ["Diplomatic", "Economic", "Military", "Information"]


# ===========================================================================
# Historical Ground Truth: Following Behavior
# ===========================================================================
#
# 核心设计：
# - 追随≠同盟：基于议题上的政策协调，而非同盟阵营划分
# - 追随是"单一议题追随"：同一国家可在不同议题上追随不同领导者
# - 大国（德国/俄国/英国）是被追随者，自身不追随他人 → None
# - 模型中超级大国自动保持独立（代码逻辑），大国可选择参与领导竞争
#
# 历史背景（1913年）：
# - 三国同盟：德国-奥匈帝国-意大利（但意大利已有松动迹象）
# - 三国协约：英国-法国-俄国（非正式同盟，而是协商机制）
# - 巴尔干战争正在进行，塞尔维亚亲俄，罗马尼亚摇摆
# - 奥斯曼帝国军事现代化依赖德国军事代表团
# - 德国Weltpolitik推动海军竞赛和殖民扩张
# ===========================================================================

PREWAR_FOLLOWING = {
    # ---- 大国：被追随者，自身不追随 ----
    130: None,   # 德国：CINC最高，独立决策者
    131: None,   # 俄国：大国，独立决策者
    132: None,   # 英国：大国/超级大国，独立决策者

    # ---- 中等强国 ----
    133: 132,    # 法国：殖民地和海军议题上追随英国协调立场（协约核心）
    134: 130,    # 奥匈帝国：巴尔干政策完全追随德国（三国同盟核心盟友）
    135: 130,    # 意大利：1913年仍在三国同盟中，整体与德国协调

    # ---- 巴尔干国家 ----
    136: 130,    # 奥斯曼帝国：军事现代化议题上追随德国（德国军事代表团驻土）
    137: 130,    # 保加利亚：第二次巴尔干战争后靠拢奥匈-德国阵营
    140: 131,    # 塞尔维亚：亲俄，在巴尔干问题上追随俄国
    141: 131,    # 罗马尼亚：在外交议题上追随俄国（但有摇摆）
    143: 132,    # 希腊：外交上倾向英法，追随英国

    # ---- 西欧和北欧国家 ----
    138: 132,    # 西班牙：中立，但殖民地和贸易议题上与英法联系更多
    139: 132,    # 比利时：被保证中立国，安全上依赖英法保证
    142: 132,    # 挪威：1905年独立后与英国经济联系密切（渔业、航运）
    144: 132,    # 葡萄牙：与英国历史联系密切（英葡同盟），追随英国
    145: 130,    # 荷兰：中立，经济上与德国联系密切（莱茵河贸易）
    146: 130,    # 瑞士：永久中立国，但德语区主导，与德国联系密切
    147: 132,    # 丹麦：中立，但与英国有较多贸易联系
    148: 130,    # 波兰：处于俄德奥三国瓜分中，倾向德国文化影响
}


def get_expected_leader(agent_id, round_num):
    """Get the historically expected leader for an agent in a given round."""
    # Project 7 全部50轮都是战前阶段（1913年）
    return PREWAR_FOLLOWING.get(agent_id, None)


# ===========================================================================
# Historical Ground Truth: Action Distribution
# ===========================================================================
#
# 基于1913年历史记录的各国主要行为类型。
# 评估方式：每一轮每一国的主导行为类型是否与历史一致。
#
# 1913年历史背景：
# - 欧洲处于"武装和平"状态，军备竞赛激烈
# - 巴尔干战争（1912-1913）正在进行
# - 各国主要行为：军事准备、外交协调、殖民竞争
# - 威胁和军事姿态是常见行为，但外交协调仍是主要手段
# ===========================================================================

EXPECTED_ACTION_PRIMARY = {
    130: "Information",   # 德国：Weltpolitik、海军竞赛、威胁性外交（"威胁"为主）
    131: "Military",      # 俄国：大军事计划、巴尔干干预、军事姿态
    132: "Diplomatic",    # 英国：平衡外交、协调协约、殖民外交
    133: "Diplomatic",    # 法国：联盟协调、对俄外交、殖民外交
    134: "Military",      # 奥匈：巴尔干军事施压、对塞尔维亚威胁
    135: "Military",      # 意大利：利比亚战争后军事扩张
    136: "Military",      # 奥斯曼：巴尔干战争后军事重建
    137: "Military",      # 保加利亚：巴尔干战争
    138: "Diplomatic",    # 西班牙：中立外交
    139: "Diplomatic",    # 比利时：中立外交
    140: "Military",      # 塞尔维亚：巴尔干战争、对奥匈军事对抗
    141: "Military",      # 罗马尼亚：巴尔干战争
    142: "Diplomatic",    # 挪威：中立外交
    143: "Military",      # 希腊：巴尔干战争
    144: "Diplomatic",    # 葡萄牙：殖民地外交
    145: "Diplomatic",    # 荷兰：中立外交
    146: "Diplomatic",    # 瑞士：永久中立外交
    147: "Diplomatic",    # 丹麦：中立外交
    148: "Diplomatic",    # 波兰：被瓜分状态，无独立外交
}

EXPECTED_ACTION_SECONDARY = {
    130: "Military",      # 德国：海军竞赛、军事准备
    131: "Diplomatic",    # 俄国：联盟外交
    132: "Military",      # 英国：海军优势
    133: "Military",      # 法国：军事准备
    134: "Diplomatic",    # 奥匈：同盟外交
    135: "Diplomatic",    # 意大利：同盟外交
    136: "Diplomatic",    # 奥斯曼：改革外交
    137: "Diplomatic",    # 保加利亚：同盟外交
    138: "Economic",      # 西班牙：贸易
    139: "Economic",      # 比利时：贸易
    140: "Diplomatic",    # 塞尔维亚：联盟外交
    141: "Diplomatic",    # 罗马尼亚：联盟外交
    142: "Economic",      # 挪威：渔业贸易
    143: "Diplomatic",    # 希腊：联盟外交
    144: "Military",      # 葡萄牙：殖民地军事
    145: "Economic",      # 荷兰：贸易
    146: "Economic",      # 瑞士：贸易
    147: "Economic",      # 丹麦：贸易
    148: "Economic",      # 波兰：经济依附
}


# ===========================================================================
# Data Loading (from SQLite database)
# ===========================================================================

def load_follower_data():
    """Load follower relations from SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        SELECT round_num, follower_agent_id, leader_agent_id
        FROM follower_relation
        WHERE project_id = ?
        ORDER BY round_num, follower_agent_id
    ''', (PROJECT_ID,))

    data = defaultdict(dict)
    for row in c.fetchall():
        rn, fid, lid = row
        if lid == fid:
            lid = None
        if fid not in data[rn]:
            data[rn][fid] = lid

    conn.close()
    return dict(data)


def load_action_data():
    """Load action records from SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        SELECT round_num, source_agent_id, action_id, action_category
        FROM action_record
        WHERE project_id = ?
        ORDER BY round_num, source_agent_id
    ''', (PROJECT_ID,))

    data = defaultdict(lambda: defaultdict(list))
    for row in c.fetchall():
        rn, agent_id, action_id, action_cat = row
        cat = ACTION_CATEGORY_MAP.get(action_id, action_cat)
        data[rn][agent_id].append((action_id, cat))

    conn.close()
    return dict(data)


# ===========================================================================
# Dimension 1: Following Behavior F1
# ===========================================================================

def compute_following_f1(follower_data):
    """
    Compute following behavior F1 scores.

    对每个 (round, agent) 对：
    - TP: 追随了历史正确的领导者
    - FP: 追随了错误的领导者（应追随其他人）
    - FN: 应追随某人但保持了中立
    - TN: 正确保持中立
    """
    rounds = sorted(follower_data.keys())

    total_tp = total_fp = total_fn = total_tn = 0
    round_metrics = []
    agent_correct = defaultdict(int)
    agent_total = defaultdict(int)
    agent_tp = defaultdict(int)
    agent_fp = defaultdict(int)
    agent_fn = defaultdict(int)
    agent_tn = defaultdict(int)

    for rn in rounds:
        round_data = follower_data.get(rn, {})
        tp = fp = fn = tn = 0

        for agent_id in ALL_AGENT_IDS:
            actual_leader = round_data.get(agent_id, None)
            expected_leader = get_expected_leader(agent_id, rn)

            agent_total[agent_id] += 1

            if expected_leader is not None:
                if actual_leader is not None:
                    if actual_leader == expected_leader:
                        tp += 1
                        agent_correct[agent_id] += 1
                        agent_tp[agent_id] += 1
                    else:
                        fp += 1
                        agent_fp[agent_id] += 1
                else:
                    fn += 1
                    agent_fn[agent_id] += 1
            else:
                if actual_leader is not None:
                    fp += 1
                    agent_fp[agent_id] += 1
                else:
                    tn += 1
                    agent_correct[agent_id] += 1
                    agent_tn[agent_id] += 1

        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        round_metrics.append({
            "round": rn,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        })

    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) \
        if (overall_precision + overall_recall) > 0 else 0.0

    agent_accuracy = {}
    agent_detail = {}
    for aid in ALL_AGENT_IDS:
        name = AGENT_NAMES[aid]
        acc = agent_correct[aid] / agent_total[aid] if agent_total[aid] > 0 else 0.0
        agent_accuracy[name] = round(acc, 4)

        p = agent_tp[aid] / (agent_tp[aid] + agent_fp[aid]) if (agent_tp[aid] + agent_fp[aid]) > 0 else 0.0
        r = agent_tp[aid] / (agent_tp[aid] + agent_fn[aid]) if (agent_tp[aid] + agent_fn[aid]) > 0 else 0.0
        f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

        expected = PREWAR_FOLLOWING.get(aid)
        expected_name = AGENT_NAMES.get(expected, "Neutral") if expected else "Neutral"

        # Count actual following patterns
        actual_followers = defaultdict(int)
        for rn in rounds:
            lid = follower_data.get(rn, {}).get(aid)
            if lid is not None:
                actual_followers[AGENT_NAMES.get(lid, f"ID:{lid}")] += 1
        top_actual = sorted(actual_followers.items(), key=lambda x: -x[1])[:3]

        agent_detail[name] = {
            "agent_id": aid,
            "expected_leader": expected_name,
            "top_actual_followers": top_actual,
            "tp": agent_tp[aid], "fp": agent_fp[aid],
            "fn": agent_fn[aid], "tn": agent_tn[aid],
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f, 4),
            "accuracy": round(acc, 4),
        }

    return {
        "overall": {
            "tp": total_tp, "fp": total_fp, "fn": total_fn, "tn": total_tn,
            "precision": round(overall_precision, 4),
            "recall": round(overall_recall, 4),
            "f1": round(overall_f1, 4),
        },
        "per_round": round_metrics,
        "per_agent_accuracy": agent_accuracy,
        "per_agent_detail": agent_detail,
    }


# ===========================================================================
# Dimension 2: Action Distribution F1
# ===========================================================================

def get_dominant_category(actions):
    if not actions:
        return None
    counts = defaultdict(int)
    for _, cat in actions:
        counts[cat] += 1
    return max(counts, key=counts.get)


def compute_action_f1(action_data):
    """
    Compute action distribution F1 as multi-class classification.
    """
    rounds = sorted(action_data.keys())

    category_stats = {cat: {"tp": 0, "fp": 0, "fn": 0} for cat in ALL_CATEGORIES}
    country_metrics = {}

    for agent_id in ALL_AGENT_IDS:
        expected_primary = EXPECTED_ACTION_PRIMARY.get(agent_id)
        expected_secondary = EXPECTED_ACTION_SECONDARY.get(agent_id)
        correct = 0
        total = 0

        for rn in rounds:
            round_data = action_data.get(rn, {})
            agent_actions = round_data.get(agent_id, [])
            if not agent_actions:
                continue

            dominant = get_dominant_category(agent_actions)
            if dominant is None:
                continue

            total += 1
            if dominant == expected_primary:
                correct += 1
                category_stats[expected_primary]["tp"] += 1
            elif dominant == expected_secondary:
                correct += 0.5
                category_stats[dominant]["fp"] += 1
                category_stats[expected_primary]["fn"] += 1
            else:
                category_stats[dominant]["fp"] += 1
                category_stats[expected_primary]["fn"] += 1

        accuracy = correct / total if total > 0 else 0.0
        country_metrics[AGENT_NAMES[agent_id]] = {
            "agent_id": agent_id,
            "expected_primary": expected_primary,
            "expected_secondary": expected_secondary,
            "accuracy": round(accuracy, 4),
            "total_rounds_evaluated": total,
            "correct_count": correct,
        }

    per_category = {}
    for cat in ALL_CATEGORIES:
        s = category_stats[cat]
        p = s["tp"] / (s["tp"] + s["fp"]) if (s["tp"] + s["fp"]) > 0 else 0.0
        r = s["tp"] / (s["tp"] + s["fn"]) if (s["tp"] + s["fn"]) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        per_category[cat] = {
            "tp": s["tp"], "fp": s["fp"], "fn": s["fn"],
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
        }

    f1_values = [per_category[cat]["f1"] for cat in ALL_CATEGORIES]
    macro_f1 = sum(f1_values) / len(f1_values) if f1_values else 0.0

    return {
        "overall": {
            "macro_f1": round(macro_f1, 4),
            "per_category": per_category,
        },
        "per_country": country_metrics,
    }


# ===========================================================================
# Combined Score
# ===========================================================================

def compute_combined_f1(following_f1, action_f1, w_follow=0.5, w_action=0.5):
    f_follow = following_f1["overall"]["f1"]
    f_action = action_f1["overall"]["macro_f1"]
    return round(w_follow * f_follow + w_action * f_action, 4)


# ===========================================================================
# Diagnostic Analysis
# ===========================================================================

def diagnose_following_problems(follower_data):
    """Diagnose key problems in following behavior."""
    rounds = sorted(follower_data.keys())
    problems = []

    # Problem 1: Who is the most common leader?
    leader_counts = defaultdict(int)
    for rn in rounds:
        for agent_id, leader_id in follower_data.get(rn, {}).items():
            if leader_id is not None:
                leader_counts[AGENT_NAMES.get(leader_id, f"ID:{leader_id}")] += 1
    top_leaders = sorted(leader_counts.items(), key=lambda x: -x[1])
    problems.append(f"Most common leaders: {top_leaders[:5]}")

    # Problem 2: Historical errors - Russia following UK
    russia_uk_count = 0
    russia_total = 0
    for rn in rounds:
        lid = follower_data.get(rn, {}).get(131)  # Russia
        if lid is not None:
            russia_total += 1
            if lid == 132:  # UK
                russia_uk_count += 1
    if russia_total > 0:
        problems.append(f"Russia following UK: {russia_uk_count}/{russia_total} rounds ({russia_uk_count/russia_total*100:.0f}%) - HISTORICALLY WRONG")

    # Problem 3: Ottoman Empire following Germany
    ottoman_germany = 0
    ottoman_total = 0
    for rn in rounds:
        lid = follower_data.get(rn, {}).get(136)  # Ottoman
        if lid is not None:
            ottoman_total += 1
            if lid == 130:  # Germany
                ottoman_germany += 1
    if ottoman_total > 0:
        problems.append(f"Ottoman following Germany: {ottoman_germany}/{ottoman_total} rounds ({ottoman_germany/ottoman_total*100:.0f}%) - should be HIGH")

    # Problem 4: Austria-Hungary following Germany
    ah_germany = 0
    ah_total = 0
    for rn in rounds:
        lid = follower_data.get(rn, {}).get(134)  # Austria-Hungary
        if lid is not None:
            ah_total += 1
            if lid == 130:  # Germany
                ah_germany += 1
    if ah_total > 0:
        problems.append(f"Austria-Hungary following Germany: {ah_germany}/{ah_total} rounds ({ah_germany/ah_total*100:.0f}%) - should be HIGH")

    # Problem 5: Countries that should follow UK but don't
    uk_followers_expected = [133, 138, 139, 142, 144, 147]  # France, Spain, Belgium, Norway, Portugal, Denmark
    for aid in uk_followers_expected:
        actual_uk = 0
        actual_total = 0
        for rn in rounds:
            lid = follower_data.get(rn, {}).get(aid)
            if lid is not None:
                actual_total += 1
                if lid == 132:
                    actual_uk += 1
        if actual_total > 0:
            name = AGENT_NAMES[aid]
            problems.append(f"{name} following UK: {actual_uk}/{actual_total} rounds ({actual_uk/actual_total*100:.0f}%)")

    return problems


# ===========================================================================
# Reporting
# ===========================================================================

def print_separator(char="=", width=80):
    print(char * width)

def print_header(title):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()

def print_following_report(result):
    print_header("DIMENSION 1: FOLLOWING BEHAVIOR F1")

    o = result["overall"]
    print(f"\n  Overall Following F1 Score: {o['f1']:.4f}")
    print(f"    Precision: {o['precision']:.4f}  (TP={o['tp']}, FP={o['fp']})")
    print(f"    Recall:    {o['recall']:.4f}  (TP={o['tp']}, FN={o['fn']})")
    print(f"    TN={o['tn']}")

    print("\n  Per-Country Following Detail:")
    print(f"  {'Country':<20} {'Expected→':>12} {'TP':>4} {'FP':>4} {'FN':>4} {'TN':>4} {'Prec':>7} {'Rec':>7} {'F1':>7} {'Acc':>7}")
    print(f"  {'-'*20} {'-'*12} {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
    for name in sorted(result["per_agent_detail"].keys()):
        d = result["per_agent_detail"][name]
        print(f"  {name:<20} {d['expected_leader']:>12}"
              f" {d['tp']:>4} {d['fp']:>4} {d['fn']:>4} {d['tn']:>4}"
              f"  {d['precision']:>7.4f}  {d['recall']:>7.4f}  {d['f1']:>7.4f}  {d['accuracy']:>7.2%}")

    acc = result["per_agent_accuracy"]
    worst = sorted(acc.items(), key=lambda x: x[1])[:5]
    print(f"\n  Worst performing: {', '.join(f'{n} ({a:.2%})' for n, a in worst)}")
    best = sorted(acc.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"  Best performing:  {', '.join(f'{n} ({a:.2%})' for n, a in best)}")


def print_action_report(result):
    print_header("DIMENSION 2: ACTION DISTRIBUTION F1")

    o = result["overall"]
    print(f"\n  Overall Action F1 Score (macro-averaged): {o['macro_f1']:.4f}")

    print("\n  Per-Category Precision / Recall / F1:")
    print(f"  {'Category':<14}  {'TP':>5}  {'FP':>5}  {'FN':>5}  {'Prec':>7}  {'Recall':>7}  {'F1':>7}")
    print(f"  {'-'*14}  {'-'*5}  {'-'*5}  {'-'*5}  {'-'*7}  {'-'*7}  {'-'*7}")
    for cat, s in o["per_category"].items():
        print(f"  {cat:<14}  {s['tp']:>5}  {s['fp']:>5}  {s['fn']:>5}"
              f"  {s['precision']:>7.4f}  {s['recall']:>7.4f}  {s['f1']:>7.4f}")

    print("\n  Per-Country Action Accuracy:")
    print(f"  {'Country':<20}  {'Expected':>12}  {'Secondary':>12}  {'Accuracy':>10}  {'Rounds':>6}")
    print(f"  {'-'*20}  {'-'*12}  {'-'*12}  {'-'*10}  {'-'*6}")
    for name in sorted(result["per_country"].keys()):
        m = result["per_country"][name]
        print(f"  {name:<20}  {m['expected_primary']:>12}  {m['expected_secondary']:>12}"
              f"  {m['accuracy']:>10.2%}  {m['total_rounds_evaluated']:>6}")


def print_diagnosis(problems):
    print_header("DIAGNOSTIC: KEY PROBLEMS IDENTIFIED")
    for i, p in enumerate(problems, 1):
        print(f"  {i}. {p}")


def print_combined_report(combined, following_f1, action_f1):
    print_header("COMBINED SCORE")
    f_follow = following_f1["overall"]["f1"]
    f_action = action_f1["overall"]["macro_f1"]
    print(f"\n  Following Behavior F1:  {f_follow:.4f}  (weight: 0.5)")
    print(f"  Action Distribution F1: {f_action:.4f}  (weight: 0.5)")
    print(f"  Combined Weighted F1:   {combined:.4f}")

    if combined >= 0.7:
        verdict = "GOOD - Simulation aligns well with historical expectations"
    elif combined >= 0.5:
        verdict = "MODERATE - Partial alignment, some deviations"
    elif combined >= 0.3:
        verdict = "WEAK - Significant deviations from historical patterns"
    else:
        verdict = "POOR - Major misalignment with historical ground truth"
    print(f"\n  Interpretation: {verdict}")


# ===========================================================================
# Main
# ===========================================================================

def main():
    print_header("ID7 SIMULATION VALIDATION: PRE-WWI 1913 EUROPE")
    print(f"\n  Database: {DB_PATH}")
    print(f"  Project ID: {PROJECT_ID}")
    print(f"  Agents: {len(AGENT_NAMES)} countries")
    print(f"  Key: FOLLOWING ≠ ALLIANCE (ground truth based on diplomatic behavior)")
    print(f"  Key: Great powers (DE/RU/UK) are leaders, not followers")

    follower_data = load_follower_data()
    action_data = load_action_data()
    max_round = max(max(follower_data.keys()), max(action_data.keys()))
    print(f"  Rounds with data: {max_round}")

    # Dimension 1
    following_result = compute_following_f1(follower_data)
    print_following_report(following_result)

    # Dimension 2
    action_result = compute_action_f1(action_data)
    print_action_report(action_result)

    # Diagnosis
    problems = diagnose_following_problems(follower_data)
    print_diagnosis(problems)

    # Combined
    combined = compute_combined_f1(following_result, action_result)
    print_combined_report(combined, following_result, action_result)

    # Save results
    action_result_save = {k: v for k, v in action_result.items() if k != "per_round_dominant"}
    output = {
        "project_id": PROJECT_ID,
        "validation_type": "F1 Score Validation",
        "simulation_description": "Pre-WWI 1913 Europe ABM (ID7)",
        "num_agents": len(AGENT_NAMES),
        "total_rounds_evaluated": max_round,
        "key_distinctions": [
            "追随≠同盟: ground truth based on historical diplomatic behavior, not alliance blocs",
            "Great powers (DE/RU/UK) are leaders (None), not followers",
            "Following is issue-specific, not permanent alliance commitment"
        ],
        "dimension1_following_f1": following_result,
        "dimension2_action_f1": action_result_save,
        "combined_f1": combined,
        "diagnosis": problems,
        "agent_mapping": {str(k): v for k, v in AGENT_NAMES.items()},
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Results saved to: {OUTPUT_JSON}")

    print_separator()
    print(f"  VALIDATION COMPLETE  |  Combined F1 = {combined:.4f}")
    print_separator()

    return combined


if __name__ == "__main__":
    main()
