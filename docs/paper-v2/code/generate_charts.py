"""
图表生成脚本：领导类型反事实实验论文 · 实验部分可视化
所有数据来自 abm_simulation.db，论文设计为标准
"""
import sqlite3, sys
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans'],
    'axes.unicode_minus': False,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
    'font.size': 9,
})

conn = sqlite3.connect('../../data/abm_simulation.db')
c = conn.cursor()

# Country identification by power (verified)
S1_CTRY = {0.2370: 'GMY', 0.1892: 'RUS', 0.1872: 'UKG'}
S2_CTRY = {0.2734: 'RUS', 0.2411: 'GMY', 0.1356: 'UKG'}
S3_CTRY = {0.3081: 'RUS', 0.2907: 'UKG'}

def match(power, cmap):
    return min(cmap.items(), key=lambda kv: abs(kv[0]-power))[1]

def get_real_gps(pid, cmap):
    c.execute("SELECT agent_id, initial_total_power FROM agent_config WHERE project_id=? AND leader_type IS NOT NULL AND leader_type != '' ORDER BY initial_total_power DESC", (pid,))
    rows = c.fetchall()
    result = {}
    for aid, pwr in rows:
        ctry = match(pwr, cmap)
        if ctry not in result:
            result[ctry] = {'id': aid, 'power': pwr}
    return result

def compute(pid, gps, rounds):
    gids = [g['id'] for g in gps.values()]
    placeholders = ','.join('?' * len(gids))
    c.execute(f"SELECT round_num, leader_agent_id, COUNT(*) FROM follower_relation WHERE project_id=? AND round_num BETWEEN 1 AND ? AND leader_agent_id IN ({placeholders}) GROUP BY round_num, leader_agent_id", [pid, rounds] + gids)
    fr = defaultdict(lambda: defaultdict(int))
    for rnd, lid, cnt in c.fetchall():
        fr[rnd][lid] = cnt
    hhi_vals = []
    for rnd in range(1, rounds + 1):
        t = sum(fr[rnd].values())
        hhi_vals.append(sum((v / t) ** 2 for v in fr[rnd].values()) if t > 0 else 0)
    hhi = sum(hhi_vals) / len(hhi_vals)
    followers = {}
    for ctry, g in gps.items():
        followers[ctry] = sum(fr[rnd].get(g['id'], 0) for rnd in range(1, rounds + 1)) / rounds
    # Also get per-round HHI for time series
    hhi_ts = {rnd: (sum((fr[rnd].get(gid,0)/max(1,sum(fr[rnd].values())))**2 for gid in gids) if sum(fr[rnd].values()) > 0 else 0) for rnd in range(1, rounds+1)}
    c.execute("SELECT SUM(CASE WHEN respect_sov=1 THEN 1 ELSE 0 END)*1.0/COUNT(*) FROM action_record WHERE project_id=? AND round_num BETWEEN 1 AND ?", (pid, rounds))
    sov = c.fetchone()[0]
    # Per-round sov
    c.execute("SELECT round_num, SUM(CASE WHEN respect_sov=1 THEN 1 ELSE 0 END)*1.0/COUNT(*) FROM action_record WHERE project_id=? AND round_num BETWEEN 1 AND ? GROUP BY round_num ORDER BY round_num", (pid, rounds))
    sov_ts = {r[0]: r[1] for r in c.fetchall()}
    goals = {}
    for ctry, g in gps.items():
        c.execute("SELECT AVG(goal_achievement_score) FROM strategic_goal_evaluation WHERE project_id=? AND agent_id=?", (pid, g['id']))
        r = c.fetchone()
        goals[ctry] = r[0] if r[0] else 0
    c.execute("SELECT AVG(goal_achievement_score) FROM strategic_goal_evaluation WHERE project_id=?", (pid,))
    r = c.fetchone()
    sg = r[0] if r[0] else 0
    return {'hhi': round(hhi, 4), 'sov': round(sov, 4), 'sys_g': round(sg, 1), 'followers': followers, 'goals': goals, 'hhi_ts': hhi_ts, 'sov_ts': sov_ts}

# Define experiments: name, pid, rounds, cmap, operated country, type change
exps = [
    ('S1_baseline', 22, 50, S1_CTRY, None, None),
    ('S1-G1', 52, 50, S1_CTRY, 'GMY', '强权→王道'),
    ('S1-G2', 54, 50, S1_CTRY, 'GMY', '强权→霸权'),
    ('S1-G3', 55, 50, S1_CTRY, 'GMY', '强权→昏庸'),
    ('S1-R1', 56, 50, S1_CTRY, 'RUS', '强权→王道'),
    ('S1-R2', 78, 50, S1_CTRY, 'RUS', '强权→霸权'),
    ('S1-R3', 79, 50, S1_CTRY, 'RUS', '强权→昏庸'),
    ('S1-U1', 59, 50, S1_CTRY, 'UKG', '王道→强权'),
    ('S1-U2', 60, 50, S1_CTRY, 'UKG', '王道→霸权'),
    ('S1-U3', 61, 50, S1_CTRY, 'UKG', '王道→昏庸'),
    ('S2_baseline', 25, 32, S2_CTRY, None, None),
    ('S2-R1', 62, 32, S2_CTRY, 'RUS', '霸权→王道'),
    ('S2-R2', 63, 32, S2_CTRY, 'RUS', '霸权→强权'),
    ('S2-R3', 64, 32, S2_CTRY, 'RUS', '霸权→昏庸'),
    ('S2-G1', 65, 32, S2_CTRY, 'GMY', '强权→王道'),
    ('S2-G2', 66, 32, S2_CTRY, 'GMY', '强权→霸权'),
    ('S2-G3', 77, 32, S2_CTRY, 'GMY', '强权→昏庸'),
    ('S2-U1', 68, 32, S2_CTRY, 'UKG', '王道→强权'),
    ('S2-U2', 69, 32, S2_CTRY, 'UKG', '王道→霸权'),
    ('S2-U3', 70, 32, S2_CTRY, 'UKG', '王道→昏庸'),
    ('S3_baseline', 26, 50, S3_CTRY, None, None),
    ('S3-R1', 71, 50, S3_CTRY, 'RUS', '强权→王道'),
    ('S3-R2', 72, 50, S3_CTRY, 'RUS', '强权→霸权'),
    ('S3-R3', 73, 50, S3_CTRY, 'RUS', '强权→昏庸'),
    ('S3-U1', 74, 50, S3_CTRY, 'UKG', '王道→强权'),
    ('S3-U2', 75, 50, S3_CTRY, 'UKG', '王道→霸权'),
    ('S3-U3', 76, 50, S3_CTRY, 'UKG', '王道→昏庸'),
]

results = {}
for name, pid, rounds, cmap, op_ctry, op_type in exps:
    gps = get_real_gps(pid, cmap)
    r = compute(pid, gps, rounds)
    r['op_ctry'] = op_ctry
    r['op_type'] = op_type
    r['rounds'] = rounds
    results[name] = r

# Compute deltas
delta_rows = []
for sp, bl_name, gp_list in [('S1','S1_baseline',['GMY','RUS','UKG']), ('S2','S2_baseline',['RUS','GMY','UKG']), ('S3','S3_baseline',['RUS','UKG'])]:
    bl = results[bl_name]
    for name, pid, rounds, cmap, op_ctry, op_type in exps:
        if not name.startswith(sp+'-'): continue
        r = results[name]
        d_hhi = r['hhi'] - bl['hhi']
        d_sov = r['sov'] - bl['sov']
        d_goal = r['goals'][op_ctry] - bl['goals'][op_ctry]
        d_foll = r['followers'][op_ctry] - bl['followers'][op_ctry]
        scene_label = sp.replace('S1','1913多极').replace('S2','1938过渡').replace('S3','1946两极')
        delta_rows.append({
            'name': name, 'scene': scene_label, 'op_ctry': op_ctry, 'op_type': op_type,
            'd_hhi': d_hhi, 'd_sov': d_sov, 'd_goal': d_goal, 'd_foll': d_foll,
            'from_type': op_type.split('→')[0] if op_type else '', 'to_type': op_type.split('→')[1] if op_type else '',
            'bl_goal': bl['goals'][op_ctry], 'exp_goal': r['goals'][op_ctry],
            'bl_foll': bl['followers'][op_ctry], 'exp_foll': r['followers'][op_ctry],
        })

print(f"Extracted {len(delta_rows)} experiment deltas")
conn.close()

# ============================================================
# Figure 1: HHI change by operation direction (grouped bar)
# ============================================================
fig, ax = plt.subplots(figsize=(12, 5.5))
directions_order = ['强权→王道', '强权→霸权', '强权→昏庸', '霸权→王道', '霸权→强权', '霸权→昏庸', '王道→强权', '王道→霸权', '王道→昏庸']
scene_colors = {'1913多极': '#4472C4', '1938过渡': '#ED7D31', '1946两极': '#A5A5A5'}
x_positions = []
labels = []
colors_list = []
values = []
for i, d in enumerate(directions_order):
    matches = [r for r in delta_rows if r['op_type'] == d]
    for m in matches:
        x_positions.append(i + (len(labels) - sum(1 for r in delta_rows if r['op_type'] in directions_order[:i]) - 0.15) * 0)
        labels.append(f"{m['name']}\n{m['op_ctry']}")
        colors_list.append(scene_colors[m['scene']])
        values.append(m['d_hhi'])

# Better: grouped by direction
unique_dirs = []
dir_labels = []
for d in directions_order:
    matches = [r for r in delta_rows if r['op_type'] == d]
    if not matches: continue
    unique_dirs.append(d)
    dir_labels.append(d)

bar_width = 0.18
x = np.arange(len(unique_dirs))
for di, d in enumerate(unique_dirs):
    matches = [r for r in delta_rows if r['op_type'] == d]
    for mi, m in enumerate(matches):
        offset = (mi - (len(matches)-1)/2) * bar_width
        bar = ax.bar(x[di] + offset, m['d_hhi'], bar_width * 0.9,
                     color=scene_colors[m['scene']], edgecolor='white', linewidth=0.5,
                     label=m['scene'] if di == 0 and mi == 0 else "")
        # Add value label on bar
        if abs(m['d_hhi']) > 0.01:
            ax.text(x[di] + offset, m['d_hhi'] + (0.01 if m['d_hhi'] > 0 else -0.015),
                    f'{m["d_hhi"]:+.2f}', ha='center', va='bottom' if m['d_hhi'] > 0 else 'top',
                    fontsize=5.5, rotation=90 if len(matches) > 2 else 0)
        if mi == 0 and di == 0:
            bar.set_label(m['scene'])

ax.axhline(y=0, color='black', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(dir_labels, fontsize=8)
ax.set_ylabel('ΔHHI', fontsize=10)
ax.set_title('图1  各操作方向下追随集中度（HHI）的变化', fontsize=11, fontweight='bold')
# Build legend
handles = [plt.Rectangle((0,0),1,1, color=scene_colors[s]) for s in ['1913多极', '1938过渡', '1946两极']]
ax.legend(handles, ['1913多极', '1938过渡', '1946两极'], fontsize=7, loc='lower left')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
fig.savefig('figures/fig1_hhi_by_direction.png', dpi=200)
plt.close()
print("Figure 1 saved")

# ============================================================
# Figure 2: Sovereignty respect rate change by direction
# ============================================================
fig, ax = plt.subplots(figsize=(12, 5.5))
for di, d in enumerate(unique_dirs):
    matches = [r for r in delta_rows if r['op_type'] == d]
    for mi, m in enumerate(matches):
        offset = (mi - (len(matches)-1)/2) * bar_width
        bar = ax.bar(x[di] + offset, m['d_sov'], bar_width * 0.9,
                     color=scene_colors[m['scene']], edgecolor='white', linewidth=0.5)
        if abs(m['d_sov']) > 0.003:
            ax.text(x[di] + offset, m['d_sov'] + (0.004 if m['d_sov'] > 0 else -0.008),
                    f'{m["d_sov"]:+.3f}', ha='center', va='bottom' if m['d_sov'] > 0 else 'top',
                    fontsize=5.5, rotation=90 if len(matches) > 2 else 0)

ax.axhline(y=0, color='black', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(dir_labels, fontsize=8)
ax.set_ylabel('Δ主权尊重率', fontsize=10)
ax.set_title('图2  各操作方向下主权尊重率的变化', fontsize=11, fontweight='bold')
handles = [plt.Rectangle((0,0),1,1, color=scene_colors[s]) for s in ['1913多极', '1938过渡', '1946两极']]
ax.legend(handles, ['1913多极', '1938过渡', '1946两极'], fontsize=7, loc='lower left')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
fig.savefig('figures/fig2_sov_by_direction.png', dpi=200)
plt.close()
print("Figure 2 saved")

# ============================================================
# Figure 3: Scatter — dGoal vs dFollower (the "空走廊" finding)
# ============================================================
fig, ax = plt.subplots(figsize=(8, 6.5))
country_markers = {'GMY': 's', 'RUS': '^', 'UKG': 'o'}
country_names = {'GMY': '德国', 'RUS': '苏联/俄国', 'UKG': '英国'}
country_colors_plot = {'GMY': '#ED7D31', 'RUS': '#4472C4', 'UKG': '#70AD47'}
for r in delta_rows:
    marker = country_markers.get(r['op_ctry'], 'D')
    color = country_colors_plot.get(r['op_ctry'], 'gray')
    ax.scatter(r['d_foll'], r['d_goal'], c=color, marker=marker, s=90,
               edgecolors='white', linewidth=0.5, zorder=5,
               label=country_names.get(r['op_ctry'], r['op_ctry']))
    # Annotate with experiment name
    ax.annotate(r['name'].replace('S1-','').replace('S2-','').replace('S3-',''),
                (r['d_foll'], r['d_goal']), fontsize=5.5, ha='center', va='bottom',
                xytext=(0, 5), textcoords='offset points')

# Draw quadrant lines
ax.axhline(y=0, color='gray', linewidth=0.6, linestyle='--')
ax.axvline(x=0, color='gray', linewidth=0.6, linestyle='--')
# Draw the "empty corridor" — diagonal from top-left to bottom-right
ax.fill_between([-12, 12], [-5, -5], [5, 5], alpha=0.06, color='red')
ax.text(4, -18, '空走廊', fontsize=9, color='darkred', alpha=0.6, style='italic')

ax.set_xlabel('Δ吸引力（追随者数量）', fontsize=10)
ax.set_ylabel('Δ战略目标达成度', fontsize=10)
ax.set_title('图3  操作国自身效应：吸引力变化 vs 目标达成度变化', fontsize=11, fontweight='bold')
# De-duplicate legend
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), fontsize=8, loc='upper left')
ax.grid(alpha=0.2)
plt.tight_layout()
fig.savefig('figures/fig3_goal_vs_follower.png', dpi=200)
plt.close()
print("Figure 3 saved")

# ============================================================
# Figure 4: Cross-scene comparison — same operation, three scenes
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
ops_to_compare = [
    ('王道→强权', 'UKG'),
    ('王道→霸权', 'UKG'),
    ('王道→昏庸', 'UKG'),
]
scene_list = ['1913多极', '1938过渡', '1946两极']
colors_3 = ['#4472C4', '#ED7D31', '#70AD47']
for ax_i, (op_d, op_c) in enumerate(ops_to_compare):
    ax = axes[ax_i]
    matches = [r for r in delta_rows if r['op_type'] == op_d and r['op_ctry'] == op_c]
    match_by_scene = {}
    for m in matches:
        match_by_scene[m['scene']] = m
    x_pos = np.arange(len(scene_list))
    d_goals = [match_by_scene.get(s, {}).get('d_goal', 0) for s in scene_list]
    d_folls = [match_by_scene.get(s, {}).get('d_foll', 0) for s in scene_list]
    w = 0.35
    bars1 = ax.bar(x_pos - w/2, d_goals, w, color='#4472C4', alpha=0.7, label='Δ目标达成度')
    bars2 = ax.bar(x_pos + w/2, d_folls, w, color='#ED7D31', alpha=0.7, label='Δ吸引力')
    for bar in bars1:
        v = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., v + (2 if v >= 0 else -5),
                f'{v:+.1f}', ha='center', va='bottom' if v >= 0 else 'top', fontsize=7.5)
    for bar in bars2:
        v = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., v + (0.5 if v >= 0 else -1.5),
                f'{v:+.1f}', ha='center', fontsize=7.5)
    ax.axhline(y=0, color='black', linewidth=0.6)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(scene_list, fontsize=8)
    ax.set_title(f'英国 {op_d}', fontsize=10, fontweight='bold')
    if ax_i == 0:
        ax.legend(fontsize=7)
    ax.grid(axis='y', alpha=0.2)

fig.suptitle('图4  同一操作方向的跨场景效应对比（英国三向转变）', fontsize=11, fontweight='bold', y=1.02)
plt.tight_layout()
fig.savefig('figures/fig4_cross_scene_UKG.png', dpi=200)
plt.close()
print("Figure 4 saved")

# ============================================================
# Figure 5: Per-round HHI timeline for key experiments
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
key_pairs = [
    ('S1', 'S1_baseline', ['S1-U3', 'S1-G1', 'S1-R1'], '1913年多极体系'),
    ('S2', 'S2_baseline', ['S2-U3', 'S2-G1', 'S2-R1'], '1938年过渡体系'),
    ('S3', 'S3_baseline', ['S3-U3', 'S3-G1', 'S3-R1'], '1946年两极体系'),
]
# S3 doesn't have G1 experiment
key_pairs[2] = ('S3', 'S3_baseline', ['S3-U3', 'S3-R1', 'S3-U1'], '1946年两极体系')

for ax_i, (sp, bl_name, exp_names, title) in enumerate(key_pairs):
    ax = axes[ax_i]
    bl = results[bl_name]
    rounds = bl['rounds']
    # Plot baseline
    bl_hhi = [bl['hhi_ts'].get(r+1, 0) for r in range(rounds)]
    ax.plot(range(1, rounds+1), bl_hhi, color='black', linewidth=1.5, label='基线', alpha=0.7)
    colors_exp = ['#ED7D31', '#4472C4', '#70AD47']
    labels_exp = {'U3': '昏庸化', 'G1': '王道化', 'R1': '王道化', 'U1': '强权化'}
    for ei, ename in enumerate(exp_names):
        if ename not in results: continue
        exp_r = results[ename]
        exp_hhi = [exp_r['hhi_ts'].get(r+1, 0) for r in range(rounds)]
        label_suffix = labels_exp.get(ename.split('-')[-1][:2], ename)
        ax.plot(range(1, rounds+1), exp_hhi, color=colors_exp[ei], linewidth=1.2,
                label=f'{ename.split("-")[-1]} ({label_suffix})', alpha=0.85)
    ax.set_xlabel('轮次', fontsize=8)
    ax.set_ylabel('HHI', fontsize=8)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.legend(fontsize=6.5, loc='best')
    ax.grid(alpha=0.2)

fig.suptitle('图5  关键实验中追随集中度（HHI）的逐轮时序', fontsize=11, fontweight='bold', y=1.02)
plt.tight_layout()
fig.savefig('figures/fig5_hhi_timeline.png', dpi=200)
plt.close()
print("Figure 5 saved")

# ============================================================
# Figure 6: Three structural positions — asymmetric profit/loss
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(13, 4.8))
position_data = [
    ('边缘大国：苏联/俄国', 'RUS', ['S1-R1','S1-R2','S1-R3','S2-R1','S2-R2','S2-R3','S3-R1','S3-R2','S3-R3']),
    ('中间大国：德国', 'GMY', ['S1-G1','S1-G2','S1-G3','S2-G1','S2-G2','S2-G3']),
    ('主导大国：英国', 'UKG', ['S1-U1','S1-U2','S1-U3','S2-U1','S2-U2','S2-U3','S3-U1','S3-U2','S3-U3']),
]
for ax_i, (title, country, exp_list) in enumerate(position_data):
    ax = axes[ax_i]
    matches = [r for r in delta_rows if r['name'] in exp_list]
    if not matches: continue
    xs = [m['d_foll'] for m in matches]
    ys = [m['d_goal'] for m in matches]
    names = [m['name'].replace('S1-','').replace('S2-','').replace('S3-','') for m in matches]
    ax.scatter(xs, ys, c=country_colors_plot[country], s=80, edgecolors='white', linewidth=0.5, zorder=5)
    for i, n in enumerate(names):
        ax.annotate(n, (xs[i], ys[i]), fontsize=6, ha='center', va='bottom',
                    xytext=(0, 4), textcoords='offset points')
    ax.axhline(y=0, color='gray', linewidth=0.6, linestyle='--')
    ax.axvline(x=0, color='gray', linewidth=0.6, linestyle='--')
    ax.set_xlabel('Δ吸引力', fontsize=9)
    ax.set_ylabel('Δ目标达成度', fontsize=9)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.grid(alpha=0.2)

fig.suptitle('图6  三种结构性位置下的损益函数差异', fontsize=11, fontweight='bold', y=1.02)
plt.tight_layout()
fig.savefig('figures/fig6_position_asymmetry.png', dpi=200)
plt.close()
print("Figure 6 saved")

print("\n=== All 6 figures saved to figures/ ===")
