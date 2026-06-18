"""Extract and analyze S1-G1 (project 52) simulation data vs baseline (project 22) vs historical ground truth."""
import sqlite3, json
import numpy as np
from collections import defaultdict, Counter

conn = sqlite3.connect('data/abm_simulation.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# CINC code -> history index mapping (scene1_prewar_1913.json)
CINC_TO_HIST = {
    255: 1, 365: 2, 200: 3, 220: 4, 300: 5,
    325: 6, 640: 7, 355: 8, 230: 9, 211: 10,
    350: 11, 380: 12, 210: 13, 360: 14, 235: 15,
    390: 16, 225: 17, 345: 18, 385: 19
}
HIST_TO_CODE = {v: k for k, v in CINC_TO_HIST.items()}

CINC_TO_3CODE = {
    255: 'GMY', 365: 'RUS', 200: 'UKG', 220: 'FRN', 300: 'AUH',
    325: 'ITA', 640: 'TUR', 355: 'BUL', 230: 'SPN', 211: 'BEL',
    350: 'GRC', 380: 'SWD', 210: 'NTH', 360: 'ROM', 235: 'POR',
    390: 'DEN', 225: 'SWZ', 345: 'YUG', 385: 'NOR'
}

# Load historical ground truth
with open('data/history/scene1_prewar_1913.json', 'r', encoding='utf-8') as f:
    history = json.load(f)

hist_following = {}
for rn_str, rdata in history['rounds'].items():
    rn = int(rn_str)
    hist_following[rn] = rdata['following']

hist_idx_to_code = {c['index']: c['code'] for c in history['countries']}

GREAT_POWER_CODES = {'GMY', 'RUS', 'UKG', 'FRN', 'AUH'}

def get_agent_map(pid):
    cursor.execute(f'SELECT agent_id, agent_name, country_code, leader_type, power_level FROM agent_config WHERE project_id={pid}')
    return {r['agent_id']: dict(r) for r in cursor.fetchall()}

def get_follower_matrix(pid):
    cursor.execute(f'''SELECT round_num, follower_agent_id, leader_agent_id
        FROM follower_relation WHERE project_id={pid}
        ORDER BY round_num, follower_agent_id''')
    matrix = defaultdict(dict)
    for r in cursor.fetchall():
        matrix[r['round_num']][r['follower_agent_id']] = r['leader_agent_id']
    return dict(matrix)

def get_round_data(pid):
    cursor.execute(f'''SELECT round_num, order_type, respect_sov_ratio, leader_agent_id, leader_follower_ratio
        FROM simulation_round WHERE project_id={pid} ORDER BY round_num''')
    return {r['round_num']: dict(r) for r in cursor.fetchall()}

p52_agents = get_agent_map(52)
p22_agents = get_agent_map(22)
p52_matrix = get_follower_matrix(52)
p22_matrix = get_follower_matrix(22)
p52_rounds = get_round_data(52)
p22_rounds = get_round_data(22)

# ============================================================
# F1 scores
# ============================================================
def compute_accuracy(project_matrix, project_agents, hist_following):
    per_round = {}
    all_correct = 0
    all_total = 0
    per_country_correct = defaultdict(int)
    per_country_total = defaultdict(int)

    for rn in range(1, 51):
        if rn not in project_matrix or rn not in hist_following:
            continue
        sim_round = project_matrix[rn]
        hist_round = hist_following[rn]
        round_correct = 0
        round_total = 0

        for agent_id, sim_leader_id in sim_round.items():
            agent_cinc = project_agents[agent_id]['country_code']
            hist_idx = CINC_TO_HIST.get(agent_cinc)
            if hist_idx is None:
                continue

            hist_leader_idx = hist_round.get(str(hist_idx))
            if hist_leader_idx is None:
                continue

            round_total += 1
            per_country_total[agent_cinc] += 1

            # Both null = no follow
            if hist_leader_idx is None and sim_leader_id is None:
                round_correct += 1
                per_country_correct[agent_cinc] += 1
                continue

            # One null, one follows
            if hist_leader_idx is None or sim_leader_id is None:
                continue

            # Both follow - compare CINC codes
            hist_leader_cinc = HIST_TO_CODE.get(hist_leader_idx)
            sim_leader_cinc = project_agents[sim_leader_id]['country_code']

            if hist_leader_cinc == sim_leader_cinc:
                round_correct += 1
                per_country_correct[agent_cinc] += 1

        if round_total > 0:
            per_round[rn] = round_correct / round_total
            all_correct += round_correct
            all_total += round_total

    overall = all_correct / all_total if all_total > 0 else 0

    # Per country
    country_acc = {}
    for cinc in sorted(per_country_total.keys()):
        acc = per_country_correct[cinc] / per_country_total[cinc]
        country_acc[cinc] = (acc, per_country_correct[cinc], per_country_total[cinc])

    return per_round, overall, all_correct, all_total, country_acc

print("Computing S1-G1 accuracy...")
p52_pr, p52_overall, p52_c, p52_t, p52_country = compute_accuracy(p52_matrix, p52_agents, hist_following)
print("Computing baseline accuracy...")
p22_pr, p22_overall, p22_c, p22_t, p22_country = compute_accuracy(p22_matrix, p22_agents, hist_following)

print(f"\n{'='*70}")
print(f"OVERALL ACCURACY (vs Historical Ground Truth)")
print(f"{'='*70}")
print(f"S1-G1 (Project 52):    {p52_overall:.4f} ({p52_c}/{p52_t})")
print(f"Baseline (Project 22): {p22_overall:.4f} ({p22_c}/{p22_t})")
print(f"Delta (S1-G1 - Baseline): {p52_overall - p22_overall:+.4f}")

print(f"\n{'='*70}")
print(f"PER-COUNTRY ACCURACY")
print(f"{'='*70}")
print(f"{'Code':<6} {'S1-G1':>8} {'Baseline':>8} {'Delta':>8} {'Detail(S1-G1)':>20}")
print(f"{'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*20}")
for cinc in sorted(p52_country.keys()):
    code = CINC_TO_3CODE.get(cinc, f'???{cinc}')
    p52_a = p52_country[cinc]
    p22_a = p22_country.get(cinc, (0, 0, 0))
    delta = p52_a[0] - p22_a[0]
    detail = f"({p52_a[1]}/{p52_a[2]})"
    print(f"  {code:<4} {p52_a[0]:.3f}   {p22_a[0]:.3f}   {delta:+.3f}     {detail}")

# ============================================================
# Order type comparison
# ============================================================
print(f"\n{'='*70}")
print(f"ORDER TYPE DISTRIBUTION")
print(f"{'='*70}")
for label, rdata in [('S1-G1', p52_rounds), ('Baseline', p22_rounds)]:
    orders = Counter()
    for rn, rd in rdata.items():
        orders[rd['order_type']] += 1
    print(f"\n{label}:")
    for o, c in orders.most_common():
        print(f"  {o}: {c} rounds ({c/50*100:.0f}%)")

# ============================================================
# Respect sovereignty statistics
# ============================================================
print(f"\n{'='*70}")
print(f"RESPECT SOVEREIGNTY STATISTICS")
print(f"{'='*70}")
for label, rdata in [('S1-G1', p52_rounds), ('Baseline', p22_rounds)]:
    values = [rd['respect_sov_ratio'] for rd in rdata.values()]
    print(f"\n{label}:")
    print(f"  Mean: {np.mean(values):.4f}")
    print(f"  Median: {np.median(values):.4f}")
    print(f"  Std: {np.std(values):.4f}")
    print(f"  Min: {np.min(values):.4f}")
    print(f"  Max: {np.max(values):.4f}")

# ============================================================
# Leader following dynamics
# ============================================================
print(f"\n{'='*70}")
print(f"LEADER FOLLOWING DYNAMICS (follower count per round per leader)")
print(f"{'='*70}")

def leader_follow_counts(matrix, agents):
    result = {}
    for rn in sorted(matrix.keys()):
        for fid, lid in matrix[rn].items():
            if lid is not None and lid in agents:
                lcinc = agents[lid]['country_code']
                code = CINC_TO_3CODE.get(lcinc, f'???{lcinc}')
                if code not in result:
                    result[code] = {}
                result[code][rn] = result[code].get(rn, 0) + 1
    return result

p52_lf = leader_follow_counts(p52_matrix, p52_agents)
p22_lf = leader_follow_counts(p22_matrix, p22_agents)

# Average followers per leader
print("\nAverage followers per round:")
for label, lf_data in [('S1-G1', p52_lf), ('Baseline', p22_lf)]:
    print(f"\n{label}:")
    for code in sorted(lf_data.keys()):
        vals = list(lf_data[code].values())
        avg = np.mean(vals) if vals else 0
        print(f"  {code}: mean={avg:.1f}, min={min(vals)}, max={max(vals)}")

# ============================================================
# HHI (Herfindahl-Hirschman Index) for follower concentration
# ============================================================
print(f"\n{'='*70}")
print(f"HHI - FOLLOWER CONCENTRATION")
print(f"{'='*70}")

def compute_hhi(matrix, agents):
    hhi_per_round = {}
    for rn in sorted(matrix.keys()):
        leader_counts = defaultdict(int)
        total = 0
        for fid, lid in matrix[rn].items():
            if lid is not None and lid in agents:
                lcode = CINC_TO_3CODE.get(agents[lid]['country_code'], '???')
                leader_counts[lcode] += 1
                total += 1
        if total > 0:
            hhi = sum((c/total)**2 for c in leader_counts.values())
            hhi_per_round[rn] = hhi
    return hhi_per_round

p52_hhi = compute_hhi(p52_matrix, p52_agents)
p22_hhi = compute_hhi(p22_matrix, p22_agents)

for label, hhi_data in [('S1-G1', p52_hhi), ('Baseline', p22_hhi)]:
    vals = list(hhi_data.values())
    print(f"\n{label}:")
    print(f"  Mean HHI: {np.mean(vals):.4f}")
    print(f"  Std HHI:  {np.std(vals):.4f}")

# ============================================================
# Leader persistence (how often each leader ID appears)
# ============================================================
print(f"\n{'='*70}")
print(f"LEADER AGENT ID PERSISTENCE")
print(f"{'='*70}")

for label, rdata in [('S1-G1', p52_rounds), ('Baseline', p22_rounds)]:
    leaders = Counter()
    for rn, rd in rdata.items():
        lid = rd.get('leader_agent_id')
        if lid is not None:
            leaders[lid] += 1
    print(f"\n{label}:")
    for lid, count in leaders.most_common():
        print(f"  agent_id={lid}: {count} rounds as sole leader")

# ============================================================
# Country switch analysis
# ============================================================
print(f"\n{'='*70}")
print(f"COUNTRY FOLLOWING SWITCH ANALYSIS")
print(f"{'='*70}")

def count_switches(matrix, agents):
    switches = defaultdict(int)
    for fid in matrix[1].keys():  # get all follower agent ids
        prev_leader = None
        for rn in sorted(matrix.keys()):
            if rn in matrix and fid in matrix[rn]:
                leader = matrix[rn][fid]
                if leader != prev_leader and prev_leader is not None:
                    cinc = agents[fid]['country_code']
                    code = CINC_TO_3CODE.get(cinc, f'???{cinc}')
                    switches[code] += 1
                prev_leader = leader
    return dict(switches)

p52_switches = count_switches(p52_matrix, p52_agents)
p22_switches = count_switches(p22_matrix, p22_agents)

print(f"\n{'Code':<6} {'S1-G1 switches':>14} {'Baseline switches':>18} {'Delta':>8}")
for code in sorted(set(list(p52_switches.keys()) + list(p22_switches.keys()))):
    s52 = p52_switches.get(code, 0)
    s22 = p22_switches.get(code, 0)
    print(f"  {code:<4} {s52:>14} {s22:>18} {s52-s22:>+8}")

# ============================================================
# Action record analysis (respect_sov)
# ============================================================
print(f"\n{'='*70}")
print(f"ACTION-LEVEL RESPECT SOVEREIGNTY")
print(f"{'='*70}")

for pid, label in [(52, 'S1-G1'), (22, 'Baseline')]:
    cursor.execute(f'''
        SELECT action_category, COUNT(*) as cnt,
               SUM(CASE WHEN respect_sov=1 THEN 1 ELSE 0 END) as respect_cnt
        FROM action_record WHERE project_id={pid}
        GROUP BY action_category
    ''')
    print(f"\n{label}:")
    for r in cursor.fetchall():
        ratio = r['respect_cnt'] / r['cnt'] if r['cnt'] > 0 else 0
        print(f"  {r['action_category']}: {r['respect_cnt']}/{r['cnt']} = {ratio:.3f}")

# ============================================================
# Save comprehensive data for visualization
# ============================================================
print(f"\n{'='*70}")
print("Saving comprehensive analysis data...")
print(f"{'='*70}")

output = {
    'metadata': {
        'experiment_id': 'S1-G1',
        'project_id': 52,
        'baseline_project_id': 22,
        'scene': 'Scene 1 (1913 Multi-polar)',
        'manipulation': 'GMY 强权型 -> 王道型',
        'total_rounds': 50,
    },
    'accuracy': {
        's1g1_per_round': {str(k): v for k, v in p52_pr.items()},
        'baseline_per_round': {str(k): v for k, v in p22_pr.items()},
        's1g1_overall': p52_overall,
        'baseline_overall': p22_overall,
        's1g1_country': {CINC_TO_3CODE.get(k, str(k)): list(v) for k, v in p52_country.items()},
        'baseline_country': {CINC_TO_3CODE.get(k, str(k)): list(v) for k, v in p22_country.items()},
    },
    'order_types': {
        's1g1': {str(rn): rd['order_type'] for rn, rd in p52_rounds.items()},
        'baseline': {str(rn): rd['order_type'] for rn, rd in p22_rounds.items()},
    },
    'respect_sov': {
        's1g1': {str(rn): rd['respect_sov_ratio'] for rn, rd in p52_rounds.items()},
        'baseline': {str(rn): rd['respect_sov_ratio'] for rn, rd in p22_rounds.items()},
    },
    'leader_followers': {
        's1g1': p52_lf,
        'baseline': p22_lf,
    },
    'hhi': {
        's1g1': p52_hhi,
        'baseline': p22_hhi,
    },
    'switches': {
        's1g1': p52_switches,
        'baseline': p22_switches,
    },
    'leader_persistence': {
        's1g1': {str(rn): str(rd.get('leader_agent_id')) for rn, rd in p52_rounds.items()},
        'baseline': {str(rn): str(rd.get('leader_agent_id')) for rn, rd in p22_rounds.items()},
    }
}

with open('data/analysis_s1g1_vs_baseline.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Saved to data/analysis_s1g1_vs_baseline.json")
conn.close()
print("Done!")
