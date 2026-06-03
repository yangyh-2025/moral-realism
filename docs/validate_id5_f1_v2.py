#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ID5 ABM Simulation Validation Script V2
=========================================
修正版：严格区分"追随"与"同盟"，基于历史外交行为而非同盟阵营定义 ground truth。

Dimension 1: Following Behavior F1 (per-round, per-country)
Dimension 2: Action Distribution F1 (per-round, per-country)

追随的定义（来自模型）：
"追随是对某国在特定议题上的领导偏好，不等同于战略同盟关系。
 你的战略关系（盟友/伙伴/冲突/战争）代表双边外交立场，
 而追随代表你在多边议题上的立场选择。"

Ground truth 设计原则：
1. 追随≠同盟：基于各国在实际外交议题上的政策协调对象，而非同盟阵营
2. 大国是被追随者（leader），不追随他人：德国/俄国/英国 = None
3. 中等强国和小国有各自的追随倾向，基于历史外交行为
4. 模型中所有非超大国必须参与追随投票，因此 ground truth 不将大量国家设为 None

Usage:
    python docs/validate_id5_f1_v2.py
"""

import json
import os
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "id5_data")
OUTPUT_JSON = os.path.join(BASE_DIR, "id5_validation_results_v2.json")

PROJECT_ID = 5

AGENT_NAMES = {
    92: "Germany", 93: "Russia", 94: "UK", 95: "France", 96: "Italy",
    97: "Austria-Hungary", 98: "Ottoman Empire", 99: "Bulgaria",
    100: "Spain", 101: "Belgium", 102: "Greece", 103: "Sweden",
    104: "Netherlands", 105: "Romania", 106: "Portugal", 107: "Denmark",
    108: "Switzerland", 109: "Serbia", 110: "Norway",
}

ALL_AGENT_IDS = sorted(AGENT_NAMES.keys())

ACTION_CATEGORY_MAP = {
    1: "Diplomatic", 2: "Diplomatic", 3: "Diplomatic", 4: "Diplomatic",
    5: "Diplomatic", 6: "Economic", 7: "Economic", 8: "Diplomatic",
    9: "Information", 10: "Diplomatic", 11: "Diplomatic", 12: "Diplomatic",
    13: "Information", 14: "Diplomatic", 15: "Military", 16: "Diplomatic",
    17: "Military", 18: "Military", 19: "Military", 20: "Military",
}

ALL_CATEGORIES = ["Diplomatic", "Economic", "Military", "Information"]


# ===========================================================================
# Historical Ground Truth: Following Behavior
# ===========================================================================
#
# 核心设计：
# - 德国/俄国/英国 = 大国/超级大国，是被追随的领导者，自身不追随他人 → None
# - 其他国家 = 基于历史外交行为定义追随对象
# - 追随≠同盟：基于议题上的政策协调，而非同盟阵营划分
# - 模型中所有非超大国必须参与追随投票，因此不将大量国家设为 None
#
# 战前 (rounds 1-4, 模拟1913年)：
# ===========================================================================

PREWAR_FOLLOWING = {
    # ---- 大国：被追随者，自身不追随 ----
    92: None,   # 德国：CINC最高，独立决策者
    93: None,   # 俄国：大国，独立决策者，被塞尔维亚/罗马尼亚追随
    94: None,   # 英国：大国/超级大国，独立决策者，被法国/希腊等追随

    # ---- 中等强国 ----
    95: 94,     # 法国：殖民地和海军议题上追随英国协调立场
    96: 92,     # 意大利：1913年仍在三国同盟中，整体与德国协调
    97: 92,     # 奥匈帝国：巴尔干政策完全追随德国

    # ---- 巴尔干国家 ----
    98: 92,     # 奥斯曼帝国：军事现代化议题上追随德国（德国军事代表团驻土）
    99: 92,     # 保加利亚：第二次巴尔干战争后靠拢奥匈-德国阵营
    102: 94,    # 希腊：外交上倾向英法，追随英国
    105: 93,    # 罗马尼亚：在外交议题上追随俄国
    109: 93,    # 塞尔维亚：亲俄，在巴尔干问题上追随俄国

    # ---- 西欧和北欧国家 ----
    100: 94,    # 西班牙：中立，但殖民地和贸易议题上与英法联系更多
    101: 94,    # 比利时：被保证中立国，安全上依赖英法保证
    103: 92,    # 瑞典：中立，但与德国有文化和经济联系
    104: 92,    # 荷兰：中立，经济上与德国联系密切（莱茵河贸易）
    106: 94,    # 葡萄牙：与英国历史联系密切（英葡同盟），追随英国
    107: 94,    # 丹麦：中立，但与英国有较多贸易联系
    108: 92,    # 瑞士：永久中立国，但德语区主导，与德国联系密切
    110: 94,    # 挪威：1905年独立后与英国经济联系密切（渔业、航运）
}

# 战争阶段 (rounds 5+, 模拟1914年战争爆发后)
WAR_FOLLOWING = {
    # ---- 大国：独立决策者 ----
    92: None,   # 德国
    93: None,   # 俄国
    94: None,   # 英国

    # ---- 同盟国阵营 ----
    95: 94,     # 法国：追随英国战略协调
    96: 94,     # 意大利：1915年加入协约国，追随英国
    97: 92,     # 奥匈帝国：追随德国作战
    98: 92,     # 奥斯曼帝国：1914年10月加入同盟国
    99: 92,     # 保加利亚：1915年加入同盟国
    102: 94,    # 希腊：最终加入协约国
    105: 94,    # 罗马尼亚：1916年加入协约国
    109: 94,    # 塞尔维亚：战争中依赖协约国支持

    # ---- 中立国（有各自的倾向）----
    100: 94,    # 西班牙：中立但倾向协约国
    101: 94,    # 比利时：被入侵后协约国阵营
    103: 92,    # 瑞典：中立但与德国有经济联系
    104: 92,    # 荷兰：中立但与德国有经济联系
    106: 94,    # 葡萄牙：1916年加入协约国
    107: 94,    # 丹麦：中立但与英国有贸易联系
    108: 92,    # 瑞士：中立但德语区倾向德国
    110: 94,    # 挪威：中立但与英国有贸易联系
}


def get_expected_leader(agent_id, round_num):
    """Get the historically expected leader for an agent in a given round."""
    if round_num <= 4:
        return PREWAR_FOLLOWING.get(agent_id, None)
    else:
        return WAR_FOLLOWING.get(agent_id, None)


# ===========================================================================
# Historical Ground Truth: Action Distribution
# ===========================================================================
#
# 基于1913年历史记录的各国主要行为类型。
# 评估方式：每一轮每一国的主导行为类型是否与历史一致。
# ===========================================================================

EXPECTED_ACTION_PRIMARY = {
    92: "Military",      # 德国：Weltpolitik、军备竞赛
    93: "Military",      # 俄国：大军事计划、巴尔干干预
    94: "Diplomatic",    # 英国：平衡外交、协调协约
    95: "Diplomatic",    # 法国：联盟协调、对俄外交
    96: "Military",      # 意大利：利比亚战争后军事扩张
    97: "Military",      # 奥匈：巴尔干军事施压
    98: "Military",      # 奥斯曼：巴尔干战争后军事重建
    99: "Military",      # 保加利亚：巴尔干战争
    100: "Diplomatic",   # 西班牙：中立外交
    101: "Diplomatic",   # 比利时：中立外交
    102: "Military",     # 希腊：巴尔干战争
    103: "Diplomatic",   # 瑞典：中立外交
    104: "Diplomatic",   # 荷兰：中立外交
    105: "Military",     # 罗马尼亚：巴尔干战争
    106: "Diplomatic",   # 葡萄牙：殖民地外交
    107: "Diplomatic",   # 丹麦：中立外交
    108: "Diplomatic",   # 瑞士：永久中立外交
    109: "Military",     # 塞尔维亚：巴尔干战争
    110: "Diplomatic",   # 挪威：中立外交
}

EXPECTED_ACTION_SECONDARY = {
    92: "Diplomatic",
    93: "Diplomatic",
    94: "Military",
    95: "Military",
    96: "Diplomatic",
    97: "Diplomatic",
    98: "Diplomatic",
    99: "Diplomatic",
    100: "Military",
    101: "Military",
    102: "Diplomatic",
    103: "Military",
    104: "Economic",
    105: "Diplomatic",
    106: "Military",
    107: "Economic",
    108: "Economic",
    109: "Diplomatic",
    110: "Economic",
}


# ===========================================================================
# Data Loading
# ===========================================================================

def load_follower_data():
    """Load follower relations from exported JSON."""
    path = os.path.join(DATA_DIR, "follower_relations.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    data = defaultdict(dict)
    for record in raw:
        rn = record["round_num"]
        fid = record["follower_agent_id"]
        lid = record.get("leader_agent_id")
        if lid == fid:
            lid = None
        if fid not in data[rn]:
            data[rn][fid] = lid
    return dict(data)


def load_action_data():
    """Load action records from exported JSON."""
    path = os.path.join(DATA_DIR, "actions.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    data = defaultdict(lambda: defaultdict(list))
    for rn_str, agents in raw.items():
        rn = int(rn_str)
        for agent_key, actions in agents.items():
            agent_id = int(agent_key.split("_")[0])
            for a in actions:
                acid = a.get("action_id")
                cat = ACTION_CATEGORY_MAP.get(acid, a.get("action_category", "Unknown"))
                data[rn][agent_id].append((acid, cat))
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

    所有国家同等评估，不做核心/外围区分。
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

        prewar_exp = PREWAR_FOLLOWING.get(aid)
        war_exp = WAR_FOLLOWING.get(aid)
        prewar_name = AGENT_NAMES.get(prewar_exp, "Neutral") if prewar_exp else "Neutral"
        war_name = AGENT_NAMES.get(war_exp, "Neutral") if war_exp else "Neutral"

        agent_detail[name] = {
            "agent_id": aid,
            "expected_prewar": prewar_name,
            "expected_war": war_name,
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
    print_header("DIMENSION 1: FOLLOWING BEHAVIOR F1 (V2)")

    o = result["overall"]
    print(f"\n  Overall Following F1 Score: {o['f1']:.4f}")
    print(f"    Precision: {o['precision']:.4f}  (TP={o['tp']}, FP={o['fp']})")
    print(f"    Recall:    {o['recall']:.4f}  (TP={o['tp']}, FN={o['fn']})")
    print(f"    TN={o['tn']}")

    print("\n  Per-Country Following Detail:")
    print(f"  {'Country':<20} {'PreWar→':>10} {'War→':>10} {'TP':>4} {'FP':>4} {'FN':>4} {'TN':>4} {'Prec':>7} {'Rec':>7} {'F1':>7} {'Acc':>7}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
    for name in sorted(result["per_agent_detail"].keys()):
        d = result["per_agent_detail"][name]
        print(f"  {name:<20} {d['expected_prewar']:>10} {d['expected_war']:>10}"
              f" {d['tp']:>4} {d['fp']:>4} {d['fn']:>4} {d['tn']:>4}"
              f"  {d['precision']:>7.4f}  {d['recall']:>7.4f}  {d['f1']:>7.4f}  {d['accuracy']:>7.2%}")

    acc = result["per_agent_accuracy"]
    worst = sorted(acc.items(), key=lambda x: x[1])[:5]
    print(f"\n  Worst performing: {', '.join(f'{n} ({a:.2%})' for n, a in worst)}")
    best = sorted(acc.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"  Best performing:  {', '.join(f'{n} ({a:.2%})' for n, a in best)}")


def print_action_report(result):
    print_header("DIMENSION 2: ACTION DISTRIBUTION F1 (V2)")

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


def print_combined_report(combined, following_f1, action_f1):
    print_header("COMBINED SCORE (V2)")
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
    print_header("ID5 SIMULATION VALIDATION V2: PRE-WWI 1913 EUROPE")
    print(f"\n  Data directory: {DATA_DIR}")
    print(f"  Project ID: {PROJECT_ID}")
    print(f"  Agents: {len(AGENT_NAMES)} countries")
    print(f"  Key: FOLLOWING ≠ ALLIANCE (ground truth based on diplomatic behavior)")
    print(f"  Key: Great powers (DE/RU/UK) are leaders, not followers")

    follower_data = load_follower_data()
    action_data = load_action_data()
    max_round = max(max(follower_data.keys()), max(action_data.keys()))
    print(f"  Rounds with data: {max_round}")

    following_result = compute_following_f1(follower_data)
    print_following_report(following_result)

    action_result = compute_action_f1(action_data)
    print_action_report(action_result)

    combined = compute_combined_f1(following_result, action_result)
    print_combined_report(combined, following_result, action_result)

    action_result_save = {k: v for k, v in action_result.items() if k != "per_round_dominant"}
    output = {
        "project_id": PROJECT_ID,
        "validation_type": "F1 Score Validation V2",
        "simulation_description": "Pre-WWI 1913 Europe ABM (ID5)",
        "num_agents": len(AGENT_NAMES),
        "total_rounds_evaluated": max_round,
        "key_distinctions": [
            "追随≠同盟: ground truth based on historical diplomatic behavior, not alliance blocs",
            "Great powers (DE/RU/UK) are leaders (None), not followers",
            "All non-superpower countries have a following target based on historical diplomatic ties"
        ],
        "dimension1_following_f1": following_result,
        "dimension2_action_f1": action_result_save,
        "combined_f1": combined,
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
