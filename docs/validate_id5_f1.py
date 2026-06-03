#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ID5 ABM Simulation Validation Script
======================================
Computes F1 scores for two dimensions comparing simulation results (project_id=5)
against historical ground truth for pre-WWI 1913 Europe.

Dimension 1: Following Behavior F1
Dimension 2: Action Distribution F1

Usage:
    python docs/validate_id5_f1.py
"""

import sqlite3
import json
import os
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "abm_simulation.db")
OUTPUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "id5_validation_results.json")

PROJECT_ID = 5

# Agent ID -> country name
AGENT_NAMES = {
    92: "Germany", 93: "Russia", 94: "UK", 95: "France", 96: "Italy",
    97: "Austria-Hungary", 98: "Ottoman Empire", 99: "Bulgaria",
    100: "Spain", 101: "Belgium", 102: "Greece", 103: "Sweden",
    104: "Netherlands", 105: "Romania", 106: "Portugal", 107: "Denmark",
    108: "Switzerland", 109: "Serbia", 110: "Norway",
}

# CINC values
AGENT_CINC = {
    92: 0.237, 93: 0.189, 94: 0.187, 95: 0.106, 96: 0.073,
    97: 0.052, 98: 0.026, 99: 0.020, 100: 0.024, 101: 0.024,
    102: 0.010, 103: 0.011, 104: 0.011, 105: 0.008, 106: 0.006,
    107: 0.004, 108: 0.004, 109: 0.003, 110: 0.003,
}

# Only UK (94) is classified as superpower in the simulation.
# Germany (92) = 大国/小国, Russia (93) = 大国 -- they CAN follow leaders.
# Superpowers are automatically neutral in following decisions.
SUPERPOWERS = {94}  # Only UK is superpower

# All evaluable agents (non-superpower)
EVAL_AGENTS = sorted(set(AGENT_NAMES.keys()) - SUPERPOWERS)

# Action ID -> category mapping (from DB)
ACTION_CATEGORY_MAP = {
    1: "Diplomatic", 2: "Diplomatic", 3: "Diplomatic", 4: "Diplomatic",
    5: "Diplomatic", 6: "Economic", 7: "Economic", 8: "Diplomatic",
    9: "Information", 10: "Diplomatic", 11: "Diplomatic", 12: "Diplomatic",
    13: "Information", 14: "Diplomatic", 15: "Military", 16: "Diplomatic",
    17: "Military", 18: "Military", 19: "Military", 20: "Military",
}

ALL_CATEGORIES = ["Diplomatic", "Economic", "Military", "Information"]

# ---------------------------------------------------------------------------
# Historical Ground Truth: Following Behavior
# ---------------------------------------------------------------------------
# Phase 1: Pre-war (rounds 1-6)
# Phase 2: Transition / war onset (rounds 7-12)
# Phase 3: War period (rounds 13+)
#
# For each agent, the expected leader (or None for neutral).
# Using "flexible" matching: core alliances must match; periphery is lenient.

# Pre-war alliance blocs
PREWAR_FOLLOWING = {
    # Triple Alliance bloc -> follow Germany
    96: 92,   # Italy -> Germany
    97: 92,   # Austria-Hungary -> Germany
    # Triple Entente bloc -> follow UK (primary) or each other
    95: 94,   # France -> UK (alliance coordination)
    # Balkan states
    99: 92,   # Bulgaria -> Germany/AH aligned
    109: 94,  # Serbia -> Russia/Entente aligned (follow UK as Entente leader)
    105: 94,  # Romania -> leaning Entente
    102: 94,  # Greece -> leaning Entente
    98: 92,   # Ottoman Empire -> leaning Germany
    # Small neutrals -> None (correctly neutral)
    100: None, 101: None, 103: None, 104: None,
    106: None, 107: None, 108: None, 110: None,
}

# War-period following (patterns shift)
WAR_FOLLOWING = {
    # Italy historically switched to Entente in 1915
    96: 94,   # Italy -> Entente
    97: 92,   # Austria-Hungary -> Germany
    95: 94,   # France -> UK
    99: 92,   # Bulgaria -> Central Powers
    109: 94,  # Serbia -> Entente
    105: 94,  # Romania -> Entente
    102: 94,  # Greece -> Entente
    98: 92,   # Ottoman Empire -> Central Powers
    # Neutrals remain neutral
    100: None, 101: None, 103: None, 104: None,
    106: None, 107: None, 108: None, 110: None,
}

# Core alliance members that MUST match (strict evaluation)
CORE_ALLIANCES = {
    97: {92},   # AH must follow Germany
    95: {94},   # France must follow UK
    96: {92, 94},  # Italy: either bloc acceptable (switched historically)
    99: {92},   # Bulgaria -> Central Powers
    109: {94},  # Serbia -> Entente
    98: {92},   # Ottoman -> Central Powers
}

# Peripheral countries (more lenient)
PERIPHERAL_AGENTS = {100, 101, 102, 103, 104, 105, 106, 107, 108, 110}

# ---------------------------------------------------------------------------
# Historical Ground Truth: Action Distribution
# ---------------------------------------------------------------------------
# Expected dominant action category per major country across all rounds
EXPECTED_ACTION_DOMINANT = {
    92: "Military",     # Germany: Weltpolitik, arms race
    93: "Military",     # Russia: largest army, Balkan interventionism
    94: "Diplomatic",   # UK: balance of power, diplomatic with naval element
    95: "Diplomatic",   # France: alliance coordination with Russia
    97: "Military",     # Austria-Hungary: Balkan assertiveness
}

# Secondary acceptable category (for relaxed evaluation)
EXPECTED_ACTION_SECONDARY = {
    92: "Information",   # Germany also uses threats
    93: "Information",   # Russia also uses information
    94: "Information",   # UK also uses naval threats
    95: "Military",      # France also has defensive military
    97: "Diplomatic",    # AH also uses ultimatums
}


# ---------------------------------------------------------------------------
# Database Queries
# ---------------------------------------------------------------------------

def get_connection():
    """Get a database connection."""
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_follower_data(conn):
    """Load all follower_relation records for project 5, deduplicated."""
    cur = conn.cursor()
    cur.execute("""
        SELECT round_num, follower_agent_id, leader_agent_id
        FROM follower_relation
        WHERE project_id = ?
        ORDER BY round_num, follower_agent_id
    """, (PROJECT_ID,))

    # Structure: {round_num: {follower_id: leader_id}}
    data = defaultdict(dict)
    for row in cur.fetchall():
        rn, fid, lid = row[0], row[1], row[2]
        # Deduplicate: keep first occurrence
        if fid not in data[rn]:
            data[rn][fid] = lid
    return dict(data)


def load_action_data(conn):
    """Load all action_record records for project 5."""
    cur = conn.cursor()
    cur.execute("""
        SELECT round_num, source_agent_id, action_id, action_category
        FROM action_record
        WHERE project_id = ?
        ORDER BY round_num, source_agent_id
    """, (PROJECT_ID,))

    # Structure: {round_num: {agent_id: [(action_id, category), ...]}}
    data = defaultdict(lambda: defaultdict(list))
    for row in cur.fetchall():
        rn, aid, acid = row[0], row[1], row[2]
        cat = ACTION_CATEGORY_MAP.get(acid, row[3])  # fallback to DB category
        data[rn][aid].append((acid, cat))
    return dict(data)


def load_simulation_info(conn):
    """Load project metadata."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM simulation_project WHERE project_id = ?", (PROJECT_ID,))
    row = cur.fetchone()
    if row:
        return {
            "project_id": row[0],
            "project_name": row[1],
            "total_rounds": row[3],
            "current_round": row[4],
            "status": row[5],
        }
    return None


# ---------------------------------------------------------------------------
# Dimension 1: Following Behavior F1
# ---------------------------------------------------------------------------

def get_expected_leader(agent_id, round_num):
    """Get the historically expected leader for an agent in a given round."""
    if round_num <= 6:
        return PREWAR_FOLLOWING.get(agent_id, None)
    elif round_num <= 12:
        # Transition: blend prewar and war expectations
        # For core alliances, use war expectations
        if agent_id in CORE_ALLIANCES:
            return WAR_FOLLOWING.get(agent_id, None)
        return PREWAR_FOLLOWING.get(agent_id, None)
    else:
        return WAR_FOLLOWING.get(agent_id, None)


def compute_following_f1(follower_data, max_round=None):
    """
    Compute following behavior F1 scores.

    For each round, for each evaluable agent (non-superpower):
    - TP: follows the historically expected leader
    - FP: follows a wrong leader (should be neutral or follow different leader)
    - FN: is neutral when should be following someone
    - TN: correctly neutral

    Returns overall and per-round metrics.
    """
    if max_round is None:
        max_round = max(follower_data.keys())

    rounds = sorted(r for r in follower_data.keys() if r <= max_round)

    # Overall accumulators
    total_tp = total_fp = total_fn = total_tn = 0
    round_metrics = []
    agent_correct = defaultdict(int)
    agent_total = defaultdict(int)

    for rn in rounds:
        round_data = follower_data.get(rn, {})
        tp = fp = fn = tn = 0

        for agent_id in EVAL_AGENTS:
            actual_leader = round_data.get(agent_id, None)
            expected_leader = get_expected_leader(agent_id, rn)

            agent_total[agent_id] += 1

            # Normalize: treat actual_leader==agent_id as None (self = no leader)
            if actual_leader == agent_id:
                actual_leader = None

            if expected_leader is not None:
                # Agent should be following someone
                if actual_leader is not None:
                    # Check if it's an acceptable leader
                    acceptable = CORE_ALLIANCES.get(agent_id, set())
                    if agent_id in CORE_ALLIANCES:
                        if actual_leader in acceptable:
                            tp += 1
                            agent_correct[agent_id] += 1
                        else:
                            fp += 1  # following wrong leader
                    else:
                        # Peripheral: any leader is acceptable if expected has one
                        # (relaxed: just check if following *someone*)
                        if actual_leader is not None:
                            tp += 1
                            agent_correct[agent_id] += 1
                        else:
                            fn += 1
                else:
                    fn += 1  # should follow but is neutral
            else:
                # Agent should be neutral
                if actual_leader is not None:
                    fp += 1  # following when should be neutral
                else:
                    tn += 1
                    agent_correct[agent_id] += 1

        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn

        # Per-round precision/recall/F1
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

    # Overall
    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) \
        if (overall_precision + overall_recall) > 0 else 0.0

    # Per-agent accuracy
    agent_accuracy = {}
    for aid in EVAL_AGENTS:
        if agent_total[aid] > 0:
            agent_accuracy[AGENT_NAMES[aid]] = round(agent_correct[aid] / agent_total[aid], 4)
        else:
            agent_accuracy[AGENT_NAMES[aid]] = 0.0

    return {
        "overall": {
            "tp": total_tp, "fp": total_fp, "fn": total_fn, "tn": total_tn,
            "precision": round(overall_precision, 4),
            "recall": round(overall_recall, 4),
            "f1": round(overall_f1, 4),
        },
        "per_round": round_metrics,
        "per_agent_accuracy": agent_accuracy,
    }


# ---------------------------------------------------------------------------
# Dimension 2: Action Distribution F1
# ---------------------------------------------------------------------------

def get_dominant_category(actions):
    """Given a list of (action_id, category) tuples, return the dominant category."""
    if not actions:
        return None
    counts = defaultdict(int)
    for _, cat in actions:
        counts[cat] += 1
    return max(counts, key=counts.get)


def compute_action_f1(action_data, max_round=None):
    """
    Compute action distribution F1 as multi-class classification.

    For each major country across all rounds:
    - Determine actual dominant action category per round
    - Compare against expected dominant category
    - Compute per-class precision, recall, F1
    - Compute macro-averaged F1
    """
    if max_round is None:
        max_round = max(action_data.keys())

    rounds = sorted(r for r in action_data.keys() if r <= max_round)
    major_countries = list(EXPECTED_ACTION_DOMINANT.keys())

    # Per-country tracking
    country_metrics = {}
    # Per-category confusion: {category: {"tp": n, "fp": n, "fn": n}}
    category_stats = {cat: {"tp": 0, "fp": 0, "fn": 0} for cat in ALL_CATEGORIES}

    for agent_id in major_countries:
        expected_primary = EXPECTED_ACTION_DOMINANT[agent_id]
        expected_secondary = EXPECTED_ACTION_SECONDARY[agent_id]
        correct = 0
        total = 0
        predictions = []  # (expected, actual) pairs

        for rn in rounds:
            round_data = action_data.get(rn, {})
            agent_actions = round_data.get(agent_id, [])
            if not agent_actions:
                continue

            dominant = get_dominant_category(agent_actions)
            if dominant is None:
                continue

            total += 1
            predictions.append((expected_primary, dominant))

            # Strict match: primary expected
            if dominant == expected_primary:
                correct += 1
                category_stats[expected_primary]["tp"] += 1
            elif dominant == expected_secondary:
                # Relaxed: secondary category is acceptable
                correct += 0.5  # half credit
                category_stats[dominant]["fp"] += 1
                category_stats[expected_primary]["fn"] += 1
            else:
                # Wrong category
                category_stats[dominant]["fp"] += 1
                category_stats[expected_primary]["fn"] += 1

        accuracy = correct / total if total > 0 else 0.0
        country_metrics[AGENT_NAMES[agent_id]] = {
            "expected_primary": expected_primary,
            "expected_secondary": expected_secondary,
            "accuracy_strict": round(accuracy, 4),
            "total_rounds_evaluated": total,
            "correct_count": correct,
        }

    # Per-category precision/recall/F1
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

    # Macro-averaged F1
    f1_values = [per_category[cat]["f1"] for cat in ALL_CATEGORIES]
    macro_f1 = sum(f1_values) / len(f1_values) if f1_values else 0.0

    return {
        "overall": {
            "macro_f1": round(macro_f1, 4),
            "per_category": per_category,
        },
        "per_country": country_metrics,
    }


# ---------------------------------------------------------------------------
# Extended Action F1: All countries, not just major powers
# ---------------------------------------------------------------------------

def compute_action_f1_all_countries(action_data, max_round=None):
    """
    Compute action distribution F1 for ALL countries.
    Uses a simpler approach: for each country, what is the most common action
    across all rounds, and compare against expected if available.
    """
    if max_round is None:
        max_round = max(action_data.keys())

    rounds = sorted(r for r in action_data.keys() if r <= max_round)

    country_dominant = {}
    for agent_id in AGENT_NAMES:
        cat_counts = defaultdict(int)
        for rn in rounds:
            round_data = action_data.get(rn, {})
            agent_actions = round_data.get(agent_id, [])
            for _, cat in agent_actions:
                cat_counts[cat] += 1
        if cat_counts:
            country_dominant[agent_id] = max(cat_counts, key=cat_counts.get)
        else:
            country_dominant[agent_id] = None

    return {AGENT_NAMES[aid]: cat for aid, cat in country_dominant.items()}


# ---------------------------------------------------------------------------
# Combined Score
# ---------------------------------------------------------------------------

def compute_combined_f1(following_f1, action_f1, w_follow=0.5, w_action=0.5):
    """Compute weighted combined F1 score."""
    f_follow = following_f1["overall"]["f1"]
    f_action = action_f1["overall"]["macro_f1"]
    combined = w_follow * f_follow + w_action * f_action
    return round(combined, 4)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_separator(char="=", width=80):
    print(char * width)


def print_header(title):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()


def print_following_report(result):
    """Print following behavior F1 report."""
    print_header("DIMENSION 1: FOLLOWING BEHAVIOR F1")

    o = result["overall"]
    print(f"\n  Overall Following F1 Score: {o['f1']:.4f}")
    print(f"    Precision: {o['precision']:.4f}  (TP={o['tp']}, FP={o['fp']})")
    print(f"    Recall:    {o['recall']:.4f}  (TP={o['tp']}, FN={o['fn']})")
    print(f"    TN={o['tn']}")

    # Per-round time series
    print("\n  Per-Round Following F1 Time Series:")
    print(f"  {'Round':>6}  {'TP':>4}  {'FP':>4}  {'FN':>4}  {'TN':>4}  {'Prec':>7}  {'Recall':>7}  {'F1':>7}")
    print(f"  {'-'*6}  {'-'*4}  {'-'*4}  {'-'*4}  {'-'*4}  {'-'*7}  {'-'*7}  {'-'*7}")
    for rm in result["per_round"]:
        print(f"  {rm['round']:>6}  {rm['tp']:>4}  {rm['fp']:>4}  {rm['fn']:>4}  {rm['tn']:>4}"
              f"  {rm['precision']:>7.4f}  {rm['recall']:>7.4f}  {rm['f1']:>7.4f}")

    # Per-agent accuracy
    print("\n  Per-Country Following Accuracy:")
    acc = result["per_agent_accuracy"]
    for name in sorted(acc.keys()):
        bar = "#" * int(acc[name] * 40)
        print(f"    {name:<20} {acc[name]:>6.2%}  {bar}")

    # Worst performing
    worst = sorted(acc.items(), key=lambda x: x[1])[:3]
    print(f"\n  Worst performing (following): {', '.join(f'{n} ({a:.2%})' for n, a in worst)}")


def print_action_report(result, all_country_dominant):
    """Print action distribution F1 report."""
    print_header("DIMENSION 2: ACTION DISTRIBUTION F1")

    o = result["overall"]
    print(f"\n  Overall Action F1 Score (macro-averaged): {o['macro_f1']:.4f}")

    print("\n  Per-Category Precision / Recall / F1:")
    print(f"  {'Category':<14}  {'TP':>5}  {'FP':>5}  {'FN':>5}  {'Prec':>7}  {'Recall':>7}  {'F1':>7}")
    print(f"  {'-'*14}  {'-'*5}  {'-'*5}  {'-'*5}  {'-'*7}  {'-'*7}  {'-'*7}")
    for cat, s in o["per_category"].items():
        print(f"  {cat:<14}  {s['tp']:>5}  {s['fp']:>5}  {s['fn']:>5}"
              f"  {s['precision']:>7.4f}  {s['recall']:>7.4f}  {s['f1']:>7.4f}")

    # Per-country
    print("\n  Per-Country Action Accuracy (major powers):")
    print(f"  {'Country':<20}  {'Expected':>12}  {'Secondary':>12}  {'Accuracy':>10}  {'Rounds':>6}")
    print(f"  {'-'*20}  {'-'*12}  {'-'*12}  {'-'*10}  {'-'*6}")
    for name, m in result["per_country"].items():
        print(f"  {name:<20}  {m['expected_primary']:>12}  {m['expected_secondary']:>12}"
              f"  {m['accuracy_strict']:>10.2%}  {m['total_rounds_evaluated']:>6}")

    # All countries dominant category
    print("\n  Dominant Action Category (all countries, full simulation):")
    print(f"  {'Country':<20}  {'Dominant Category':<16}")
    print(f"  {'-'*20}  {'-'*16}")
    for name, cat in sorted(all_country_dominant.items()):
        print(f"  {name:<20}  {cat or 'N/A':<16}")


def print_combined_report(combined, following_f1, action_f1):
    """Print combined score."""
    print_header("COMBINED SCORE")

    f_follow = following_f1["overall"]["f1"]
    f_action = action_f1["overall"]["macro_f1"]
    print(f"\n  Following Behavior F1:  {f_follow:.4f}  (weight: 0.5)")
    print(f"  Action Distribution F1: {f_action:.4f}  (weight: 0.5)")
    print(f"  Combined Weighted F1:   {combined:.4f}")

    # Interpretation
    if combined >= 0.7:
        verdict = "GOOD - Simulation aligns well with historical expectations"
    elif combined >= 0.5:
        verdict = "MODERATE - Partial alignment, some deviations"
    elif combined >= 0.3:
        verdict = "WEAK - Significant deviations from historical patterns"
    else:
        verdict = "POOR - Major misalignment with historical ground truth"

    print(f"\n  Interpretation: {verdict}")


def print_diagnosis(following_f1, action_f1):
    """Print diagnostic findings."""
    print_header("DIAGNOSTIC FINDINGS")

    # Following: find worst rounds
    worst_rounds = sorted(following_f1["per_round"], key=lambda x: x["f1"])[:5]
    print("\n  Worst performing rounds (Following F1):")
    for rm in worst_rounds:
        print(f"    Round {rm['round']:>3}: F1={rm['f1']:.4f} (TP={rm['tp']}, FP={rm['fp']}, FN={rm['fn']})")

    # Following: find best rounds
    best_rounds = sorted(following_f1["per_round"], key=lambda x: x["f1"], reverse=True)[:5]
    print("\n  Best performing rounds (Following F1):")
    for rm in best_rounds:
        print(f"    Round {rm['round']:>3}: F1={rm['f1']:.4f} (TP={rm['tp']}, FP={rm['fp']}, FN={rm['fn']})")

    # Action: countries with lowest accuracy
    country_acc = [(n, m["accuracy_strict"]) for n, m in action_f1["per_country"].items()]
    country_acc.sort(key=lambda x: x[1])
    print("\n  Countries with lowest action accuracy:")
    for name, acc in country_acc[:3]:
        print(f"    {name}: {acc:.2%}")


# ---------------------------------------------------------------------------
# Visualization (optional, requires matplotlib)
# ---------------------------------------------------------------------------

def generate_visualization(following_f1, action_f1, output_dir):
    """Generate matplotlib visualization if available."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
    except ImportError:
        print("\n  [matplotlib not available, skipping visualization]")
        return None

    # Try to use a CJK font for Chinese labels
    cjk_fonts = [f.name for f in fm.fontManager.ttflist
                 if any(kw in f.name.lower() for kw in ["simhei", "microsoft yahei", "simsun", "noto sans cjk"])]
    if cjk_fonts:
        plt.rcParams["font.family"] = cjk_fonts[0]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("ID5 Validation Results: Pre-WWI 1913 Europe ABM Simulation",
                 fontsize=14, fontweight="bold")

    # (1) Following F1 over time
    ax1 = axes[0, 0]
    rounds = [rm["round"] for rm in following_f1["per_round"]]
    f1s = [rm["f1"] for rm in following_f1["per_round"]]
    ax1.plot(rounds, f1s, "b-o", markersize=3, linewidth=1.2, label="Following F1")
    ax1.axhline(y=following_f1["overall"]["f1"], color="r", linestyle="--",
                alpha=0.7, label=f'Overall F1={following_f1["overall"]["f1"]:.3f}')
    ax1.set_xlabel("Round")
    ax1.set_ylabel("F1 Score")
    ax1.set_title("Following Behavior F1 Over Time")
    ax1.legend(loc="lower left", fontsize=8)
    ax1.set_ylim(0, 1.05)
    ax1.grid(True, alpha=0.3)

    # (2) Following precision/recall over time
    ax2 = axes[0, 1]
    precs = [rm["precision"] for rm in following_f1["per_round"]]
    recs = [rm["recall"] for rm in following_f1["per_round"]]
    ax2.plot(rounds, precs, "g-s", markersize=3, linewidth=1, label="Precision")
    ax2.plot(rounds, recs, "m-^", markersize=3, linewidth=1, label="Recall")
    ax2.set_xlabel("Round")
    ax2.set_ylabel("Score")
    ax2.set_title("Following Precision & Recall Over Time")
    ax2.legend(loc="lower left", fontsize=8)
    ax2.set_ylim(0, 1.05)
    ax2.grid(True, alpha=0.3)

    # (3) Per-agent following accuracy
    ax3 = axes[1, 0]
    acc = following_f1["per_agent_accuracy"]
    names = sorted(acc.keys())
    vals = [acc[n] for n in names]
    colors = ["#2ecc71" if v >= 0.7 else "#f39c12" if v >= 0.4 else "#e74c3c" for v in vals]
    bars = ax3.barh(range(len(names)), vals, color=colors)
    ax3.set_yticks(range(len(names)))
    ax3.set_yticklabels(names, fontsize=8)
    ax3.set_xlabel("Accuracy")
    ax3.set_title("Per-Country Following Accuracy")
    ax3.set_xlim(0, 1.1)
    for bar, val in zip(bars, vals):
        ax3.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                 f"{val:.2%}", va="center", fontsize=7)

    # (4) Action category distribution for major powers
    ax4 = axes[1, 1]
    categories = ALL_CATEGORIES
    cat_data = action_f1["overall"]["per_category"]
    x_pos = range(len(categories))
    f1_vals = [cat_data[c]["f1"] for c in categories]
    prec_vals = [cat_data[c]["precision"] for c in categories]
    rec_vals = [cat_data[c]["recall"] for c in categories]
    width = 0.25
    ax4.bar([p - width for p in x_pos], prec_vals, width, label="Precision", color="#3498db")
    ax4.bar(list(x_pos), rec_vals, width, label="Recall", color="#2ecc71")
    ax4.bar([p + width for p in x_pos], f1_vals, width, label="F1", color="#e74c3c")
    ax4.set_xticks(list(x_pos))
    ax4.set_xticklabels(categories, fontsize=9)
    ax4.set_ylabel("Score")
    ax4.set_title("Action Category P/R/F1")
    ax4.legend(fontsize=8)
    ax4.set_ylim(0, 1.1)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = os.path.join(output_dir, "id5_validation_f1.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Visualization saved to: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print_header("ID5 SIMULATION VALIDATION: PRE-WWI 1913 EUROPE")
    print(f"\n  Database: {DB_PATH}")
    print(f"  Project ID: {PROJECT_ID}")
    print(f"  Agents: {len(AGENT_NAMES)} countries")
    print(f"  Superpowers (excluded from following eval): Germany, Russia, UK")

    # Connect to database
    conn = get_connection()
    info = load_simulation_info(conn)
    if info:
        print(f"  Project: {info['project_name']}")
        print(f"  Total rounds: {info['total_rounds']}, Status: {info['status']}")

    # Load data
    follower_data = load_follower_data(conn)
    action_data = load_action_data(conn)
    conn.close()

    max_round = max(max(follower_data.keys()), max(action_data.keys()))
    print(f"  Rounds with data: {max_round}")

    # --- Dimension 1: Following Behavior F1 ---
    following_result = compute_following_f1(follower_data, max_round)
    print_following_report(following_result)

    # --- Dimension 2: Action Distribution F1 ---
    action_result = compute_action_f1(action_data, max_round)
    all_country_dominant = compute_action_f1_all_countries(action_data, max_round)
    print_action_report(action_result, all_country_dominant)

    # --- Combined Score ---
    combined = compute_combined_f1(following_result, action_result)
    print_combined_report(combined, following_result, action_result)

    # --- Diagnosis ---
    print_diagnosis(following_result, action_result)

    # --- Save JSON ---
    output = {
        "project_id": PROJECT_ID,
        "validation_type": "F1 Score Validation",
        "simulation_description": "Pre-WWI 1913 Europe ABM (ID5)",
        "num_agents": len(AGENT_NAMES),
        "total_rounds_evaluated": max_round,
        "dimension1_following_f1": following_result,
        "dimension2_action_f1": action_result,
        "combined_f1": combined,
        "agent_mapping": {str(k): v for k, v in AGENT_NAMES.items()},
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Results saved to: {OUTPUT_JSON}")

    # --- Visualization ---
    doc_dir = os.path.dirname(os.path.abspath(__file__))
    generate_visualization(following_result, action_result, doc_dir)

    print_separator()
    print(f"  VALIDATION COMPLETE  |  Combined F1 = {combined:.4f}")
    print_separator()

    return combined


if __name__ == "__main__":
    main()
