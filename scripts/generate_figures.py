"""Generate all figures for S1-G1 experimental report (ID52).

Figures:
  1. fig1_f1_timeseries.png - Per-round accuracy (S1-G1 vs Baseline)
  2. fig2_per_country.png - Per-country accuracy comparison (bar chart)
  3. fig3_order_distribution.png - Order type distribution comparison
  4. fig4_respect_sov_timeseries.png - Respect sovereignty over time
  5. fig5_follower_concentration.png - HHI timeseries
  6. fig6_leader_followers.png - Leader follower counts over time
  7. fig7_country_switches.png - Country switch frequency comparison
  8. fig8_heatmap_s1g1.png - S1-G1 following heatmap
  9. fig9_heatmap_baseline.png - Baseline following heatmap
  10. fig10_delta_heatmap.png - Delta following heatmap
  11. fig11_summary_dashboard.png - Combined summary dashboard
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import matplotlib.font_manager as fm
import seaborn as sns
from pathlib import Path

# Find CJK font
CJK_FONT = None
for f in fm.fontManager.ttflist:
    if 'Microsoft YaHei' in f.name:
        CJK_FONT = f.name
        break
if not CJK_FONT:
    for f in fm.fontManager.ttflist:
        if 'SimHei' in f.name:
            CJK_FONT = f.name
            break

# Style setup
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': [CJK_FONT, 'DejaVu Sans', 'Arial'] if CJK_FONT else ['DejaVu Sans'],
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'axes.unicode_minus': False,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})
if CJK_FONT:
    print(f"Using CJK font: {CJK_FONT}")

# Load data
with open('data/analysis_s1g1_vs_baseline.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

COLORS = {
    's1g1': '#2196F3',
    'baseline': '#FF9800',
    'delta': '#4CAF50',
    'diff_pos': '#4CAF50',
    'diff_neg': '#F44336',
    'grid': '#E0E0E0',
}

OUT = Path('docs/id52/figures')

# ================================================================
# Figure 1: F1 Timeseries
# ================================================================
def fig1_f1_timeseries():
    fig, ax = plt.subplots(figsize=(10, 5))

    rounds = sorted(int(k) for k in data['accuracy']['s1g1_per_round'].keys())
    s1g1_vals = [data['accuracy']['s1g1_per_round'][str(r)] for r in rounds]
    bl_vals = [data['accuracy']['baseline_per_round'][str(r)] for r in rounds]

    ax.plot(rounds, s1g1_vals, color=COLORS['s1g1'], linewidth=1.5, marker='o', markersize=3, label='S1-G1 (GMY 强权→王道)')
    ax.plot(rounds, bl_vals, color=COLORS['baseline'], linewidth=1.5, marker='s', markersize=3, label='Baseline (ID22)')

    ax.axhline(y=data['accuracy']['s1g1_overall'], color=COLORS['s1g1'], linestyle='--', alpha=0.7, linewidth=0.8)
    ax.axhline(y=data['accuracy']['baseline_overall'], color=COLORS['baseline'], linestyle='--', alpha=0.7, linewidth=0.8)

    ax.fill_between(rounds, s1g1_vals, bl_vals, alpha=0.15, color=COLORS['delta'])

    ax.set_xlabel('Round (1 round = 3 months)')
    ax.set_ylabel('Accuracy vs Historical Ground Truth')
    ax.set_title('Figure 1: Per-Round Following Accuracy — S1-G1 vs Baseline')
    ax.legend(loc='lower left', framealpha=0.9)
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, 51)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])

    # Annotate overall values
    ax.text(0.98, 0.12, f'S1-G1 overall: {data["accuracy"]["s1g1_overall"]:.3f}',
            transform=ax.transAxes, ha='right', fontsize=9, color=COLORS['s1g1'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax.text(0.98, 0.05, f'Baseline overall: {data["accuracy"]["baseline_overall"]:.3f}',
            transform=ax.transAxes, ha='right', fontsize=9, color=COLORS['baseline'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    fig.tight_layout()
    fig.savefig(OUT / 'fig1_f1_timeseries.png', facecolor='white')
    plt.close(fig)
    print("  fig1_f1_timeseries.png")

# ================================================================
# Figure 2: Per-Country Accuracy
# ================================================================
def fig2_per_country():
    s1g1_country = data['accuracy']['s1g1_country']
    bl_country = data['accuracy']['baseline_country']
    countries = sorted(s1g1_country.keys())

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(countries))
    width = 0.35

    s1g1_accs = [s1g1_country[c][0] for c in countries]
    bl_accs = [bl_country.get(c, [0,0,0])[0] for c in countries]
    deltas = [s1g1_accs[i] - bl_accs[i] for i in range(len(countries))]

    bars1 = ax.bar(x - width/2, s1g1_accs, width, label='S1-G1', color=COLORS['s1g1'], edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, bl_accs, width, label='Baseline (ID22)', color=COLORS['baseline'], edgecolor='white', linewidth=0.5)

    # Delta arrows
    for i, (s, b, d) in enumerate(zip(s1g1_accs, bl_accs, deltas)):
        color = COLORS['diff_pos'] if d > 0 else COLORS['diff_neg']
        if abs(d) > 0.02:
            ax.annotate(f'{d:+.2f}', (x[i], max(s, b) + 0.02), ha='center', fontsize=7,
                       color=color, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(countries, fontsize=9)
    ax.set_ylabel('Accuracy')
    ax.set_title('Figure 2: Per-Country Following Accuracy Comparison')
    ax.legend(loc='lower left', framealpha=0.9)
    ax.set_ylim(0, 1.15)
    ax.grid(True, alpha=0.3, axis='y', color=COLORS['grid'])
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=0.5)

    fig.tight_layout()
    fig.savefig(OUT / 'fig2_per_country.png', facecolor='white')
    plt.close(fig)
    print("  fig2_per_country.png")

# ================================================================
# Figure 3: Order Type Distribution
# ================================================================
def fig3_order_distribution():
    s1g1_orders = data['order_types']['s1g1']
    bl_orders = data['order_types']['baseline']

    # Count
    from collections import Counter
    s1g1_count = Counter(s1g1_orders.values())
    bl_count = Counter(bl_orders.values())

    all_orders = sorted(set(list(s1g1_count.keys()) + list(bl_count.keys())))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # Pie charts
    colors_pie = ['#4CAF50', '#FF9800', '#F44336', '#2196F3']

    s1g1_vals = [s1g1_count.get(o, 0) for o in all_orders]
    bl_vals = [bl_count.get(o, 0) for o in all_orders]

    wedges1, texts1, autotexts1 = ax1.pie(s1g1_vals, labels=all_orders, autopct='%1.0f%%',
                                           colors=colors_pie[:len(all_orders)], startangle=90)
    ax1.set_title('S1-G1 Order Distribution')

    wedges2, texts2, autotexts2 = ax2.pie(bl_vals, labels=all_orders, autopct='%1.0f%%',
                                           colors=colors_pie[:len(all_orders)], startangle=90)
    ax2.set_title('Baseline Order Distribution')

    fig.suptitle('Figure 3: International Order Type Distribution', fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / 'fig3_order_distribution.png', facecolor='white')
    plt.close(fig)
    print("  fig3_order_distribution.png")

# ================================================================
# Figure 4: Respect Sovereignty Timeseries
# ================================================================
def fig4_respect_sov_timeseries():
    fig, ax = plt.subplots(figsize=(10, 5))

    s1g1_rs = data['respect_sov']['s1g1']
    bl_rs = data['respect_sov']['baseline']

    rounds = sorted(int(k) for k in s1g1_rs.keys())
    s1g1_vals = [s1g1_rs[str(r)] for r in rounds]
    bl_vals = [bl_rs[str(r)] for r in rounds]

    ax.plot(rounds, s1g1_vals, color=COLORS['s1g1'], linewidth=2, label='S1-G1', marker='o', markersize=3)
    ax.plot(rounds, bl_vals, color=COLORS['baseline'], linewidth=2, label='Baseline', marker='s', markersize=3)

    ax.axhline(y=np.mean(s1g1_vals), color=COLORS['s1g1'], linestyle='--', alpha=0.7, linewidth=0.8)
    ax.axhline(y=np.mean(bl_vals), color=COLORS['baseline'], linestyle='--', alpha=0.7, linewidth=0.8)

    ax.fill_between(rounds, s1g1_vals, bl_vals, alpha=0.15, color=COLORS['delta'])

    ax.set_xlabel('Round')
    ax.set_ylabel('Respect Sovereignty Ratio')
    ax.set_title('Figure 4: Respect Sovereignty Ratio Over Time')
    ax.legend(loc='lower left')
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])

    ax.text(0.98, 0.12, f'S1-G1 mean: {np.mean(s1g1_vals):.3f}', transform=ax.transAxes, ha='right', fontsize=9, color=COLORS['s1g1'])
    ax.text(0.98, 0.05, f'Baseline mean: {np.mean(bl_vals):.3f}', transform=ax.transAxes, ha='right', fontsize=9, color=COLORS['baseline'])

    fig.tight_layout()
    fig.savefig(OUT / 'fig4_respect_sov_timeseries.png', facecolor='white')
    plt.close(fig)
    print("  fig4_respect_sov_timeseries.png")

# ================================================================
# Figure 5: HHI Timeseries
# ================================================================
def fig5_hhi_timeseries():
    fig, ax = plt.subplots(figsize=(10, 5))

    s1g1_hhi = {int(k): v for k, v in data['hhi']['s1g1'].items()}
    bl_hhi = {int(k): v for k, v in data['hhi']['baseline'].items()}

    rounds = sorted(s1g1_hhi.keys())
    s1g1_vals = [s1g1_hhi[r] for r in rounds]
    bl_vals = [bl_hhi.get(r, 0) for r in rounds]

    ax.plot(rounds, s1g1_vals, color=COLORS['s1g1'], linewidth=2, label='S1-G1', marker='o', markersize=3)
    ax.plot(rounds, bl_vals, color=COLORS['baseline'], linewidth=2, label='Baseline', marker='s', markersize=3)

    ax.set_xlabel('Round')
    ax.set_ylabel('HHI (Herfindahl-Hirschman Index)')
    ax.set_title('Figure 5: Follower Concentration (HHI) Over Time')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, color=COLORS['grid'])

    ax.text(0.98, 0.05, f'HHI=1.0 = all follow same leader\nHHI=0.05 = perfectly dispersed',
            transform=ax.transAxes, ha='right', fontsize=8, color='gray', va='bottom')

    fig.tight_layout()
    fig.savefig(OUT / 'fig5_hhi_timeseries.png', facecolor='white')
    plt.close(fig)
    print("  fig5_hhi_timeseries.png")

# ================================================================
# Figure 6: Leader Follower Counts Over Time
# Single panel comparison: solid=S1-G1, dashed=Baseline
# ================================================================
def fig6_leader_followers():
    fig, ax = plt.subplots(figsize=(12, 6))

    s1g1_lf = data['leader_followers']['s1g1']
    bl_lf = data['leader_followers']['baseline']
    all_leaders = sorted(set(list(s1g1_lf.keys()) + list(bl_lf.keys())))

    # Assign consistent colors per leader (same color for both S1-G1 and baseline)
    cmap = plt.get_cmap('tab10', len(all_leaders))
    leader_colors = {leader: cmap(i) for i, leader in enumerate(all_leaders)}

    for leader in all_leaders:
        # S1-G1: solid line
        if leader in s1g1_lf:
            vals = s1g1_lf[leader]
            rounds_s = sorted(int(k) for k in vals.keys())
            s_vals = [vals[str(r)] for r in rounds_s]
            ax.plot(rounds_s, s_vals, color=leader_colors[leader], linewidth=1.8,
                    marker='o', markersize=3, label=f'{leader} (S1-G1)')

        # Baseline: dashed line
        if leader in bl_lf:
            vals = bl_lf[leader]
            rounds_b = sorted(int(k) for k in vals.keys())
            b_vals = [vals[str(r)] for r in rounds_b]
            ax.plot(rounds_b, b_vals, color=leader_colors[leader], linewidth=1.4,
                    linestyle='--', marker='s', markersize=2.5, alpha=0.7,
                    label=f'{leader} (Baseline)')

    ax.set_xlabel('Round')
    ax.set_ylabel('Follower Count')
    ax.set_title('Figure 6: Leader Follower Counts Over Time — S1-G1 (solid) vs Baseline (dashed)')
    ax.legend(loc='upper left', ncol=2, fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])
    ax.set_xlim(0, 51)

    # Annotate with mean values
    annotation_lines = []
    for leader in all_leaders:
        s_vals = [s1g1_lf[leader].get(str(r), 0) for r in range(1, 51)] if leader in s1g1_lf else []
        b_vals = [bl_lf[leader].get(str(r), 0) for r in range(1, 51)] if leader in bl_lf else []
        s_mean = np.mean(s_vals) if s_vals else 0
        b_mean = np.mean(b_vals) if b_vals else 0
        if s_mean > 0.1 or b_mean > 0.1:
            annotation_lines.append(f'{leader}: S1-G1 avg={s_mean:.1f}, Baseline avg={b_mean:.1f}')

    ax.text(0.98, 0.95, '\n'.join(annotation_lines), transform=ax.transAxes,
            ha='right', va='top', fontsize=8, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85))

    fig.tight_layout()
    fig.savefig(OUT / 'fig6_leader_followers.png', facecolor='white')
    plt.close(fig)
    print("  fig6_leader_followers.png")

# ================================================================
# Figure 7: Country Switch Frequency
# ================================================================
def fig7_country_switches():
    s1g1_sw = data['switches']['s1g1']
    bl_sw = data['switches']['baseline']

    all_countries = sorted(set(list(s1g1_sw.keys()) + list(bl_sw.keys())))

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(all_countries))
    width = 0.35

    s1g1_vals = [s1g1_sw.get(c, 0) for c in all_countries]
    bl_vals = [bl_sw.get(c, 0) for c in all_countries]

    ax.bar(x - width/2, s1g1_vals, width, label='S1-G1', color=COLORS['s1g1'], edgecolor='white')
    ax.bar(x + width/2, bl_vals, width, label='Baseline', color=COLORS['baseline'], edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(all_countries, fontsize=9)
    ax.set_ylabel('Number of Leader Switches (50 rounds)')
    ax.set_title('Figure 7: Country Following Switch Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y', color=COLORS['grid'])

    fig.tight_layout()
    fig.savefig(OUT / 'fig7_country_switches.png', facecolor='white')
    plt.close(fig)
    print("  fig7_country_switches.png")

# ================================================================
# Figure 8-10: Following Heatmaps
# ================================================================
import sqlite3

def build_heatmap_matrix(pid):
    """Build a round x country matrix of which leader each country follows."""
    conn = sqlite3.connect('data/abm_simulation.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get agents and map
    cursor.execute(f'SELECT agent_id, agent_name, country_code, power_level FROM agent_config WHERE project_id={pid} ORDER BY country_code')
    agents = list(cursor.fetchall())
    if pid == 52:
        order = ['GMY', 'RUS', 'UKG', 'FRN', 'AUH', 'ITA', 'TUR', 'BUL', 'SPN', 'BEL',
                 'GRC', 'SWD', 'NTH', 'ROM', 'POR', 'DEN', 'SWZ', 'YUG', 'NOR']
    else:
        order = ['GMY', 'RUS', 'UKG', 'FRN', 'AUH', 'ITA', 'TUR', 'BUL', 'SPN', 'BEL',
                 'GRC', 'SWD', 'NTH', 'ROM', 'POR', 'DEN', 'SWZ', 'YUG', 'NOR']

    # Map agent_id -> country_code and great power status
    aid_to_code = {}
    aid_to_type = {}
    for a in agents:
        code_map = {255: 'GMY', 365: 'RUS', 200: 'UKG', 220: 'FRN', 300: 'AUH',
                    325: 'ITA', 640: 'TUR', 355: 'BUL', 230: 'SPN', 211: 'BEL',
                    350: 'GRC', 380: 'SWD', 210: 'NTH', 360: 'ROM', 235: 'POR',
                    390: 'DEN', 225: 'SWZ', 345: 'YUG', 385: 'NOR'}
        aid_to_code[a['agent_id']] = code_map.get(a['country_code'], str(a['country_code']))
        aid_to_type[a['agent_id']] = a['power_level']

    # Get follower data
    cursor.execute(f'''
        SELECT round_num, follower_agent_id, leader_agent_id
        FROM follower_relation WHERE project_id={pid}
        ORDER BY round_num, follower_agent_id
    ''')
    followers = cursor.fetchall()

    # Build matrix: round x country -> leader code (or 0 for none, -1 for self)
    # For follower_countries = all non-great-powers + great powers that follow others
    # Rows = rounds 1-50, Cols = all 19 countries
    matrix = np.zeros((50, len(order)))

    for r in followers:
        rn = r['round_num'] - 1  # 0-indexed
        if rn >= 50:
            continue
        col = order.index(aid_to_code[r['follower_agent_id']]) if aid_to_code[r['follower_agent_id']] in order else -1
        if col < 0:
            continue
        if r['leader_agent_id'] is None:
            matrix[rn, col] = 0  # 0 = no leader followed
        else:
            leader_code = aid_to_code.get(r['leader_agent_id'], '?')
            if leader_code in order:
                matrix[rn, col] = order.index(leader_code) + 1  # 1-indexed leader position
            else:
                matrix[rn, col] = 0

    conn.close()
    return matrix, order

def fig_heatmaps():
    """Generate heatmaps for S1-G1, Baseline, and Delta + Historical."""
    s1g1_matrix, countries = build_heatmap_matrix(52)
    bl_matrix, _ = build_heatmap_matrix(22)

    # Leaders: GMY(0), RUS(1), UKG(2), FRN(3), AUH(4)
    leader_order = ['GMY', 'RUS', 'UKG', 'FRN', 'AUH']
    leader_colors = ['#2196F3', '#F44336', '#4CAF50', '#9C27B0', '#FF9800']  # blue, red, green, purple, orange

    # Create custom colormap: 0=white(no follow), 1=GMY, 2=RUS, 3=UKG, 4=FRN, 5=AUH
    from matplotlib.colors import ListedColormap, BoundaryNorm
    colors_hm = ['#F5F5F5'] + leader_colors[:5]  # white + 5 leader colors
    cmap = ListedColormap(colors_hm)
    bounds = np.arange(-0.5, 6.5, 1)
    norm = BoundaryNorm(bounds, cmap.N)

    # Load historical data for comparison
    with open('data/history/scene1_prewar_1913.json', 'r', encoding='utf-8') as f:
        history = json.load(f)
    hist_idx_to_code = {c['index']: c['code'] for c in history['countries']}
    hist_matrix = np.zeros((50, 19))
    for rn_str, rdata in history['rounds'].items():
        rn = int(rn_str) - 1
        if rn >= 50:
            continue
        following = rdata['following']
        for hist_idx_str, leader_idx in following.items():
            hist_idx = int(hist_idx_str)
            follower_code = hist_idx_to_code.get(hist_idx)
            if follower_code is None or follower_code not in countries:
                continue
            col = countries.index(follower_code)
            if leader_idx is None:
                hist_matrix[rn, col] = 0
            else:
                leader_code = hist_idx_to_code.get(leader_idx)
                if leader_code is not None and leader_code in leader_order:
                    hist_matrix[rn, col] = leader_order.index(leader_code) + 1
                else:
                    hist_matrix[rn, col] = 0

    fig, axes = plt.subplots(3, 1, figsize=(16, 18))

    for ax, mat, title in [
        (axes[0], s1g1_matrix, 'S1-G1: GMY 强权→王道'),
        (axes[1], bl_matrix, 'Baseline (ID22): GMY 强权型'),
        (axes[2], hist_matrix, 'Historical Ground Truth'),
    ]:
        im = ax.imshow(mat.T, aspect='auto', cmap=cmap, norm=norm, interpolation='nearest')

        ax.set_yticks(range(len(countries)))
        ax.set_yticklabels(countries, fontsize=9)
        ax.set_xticks(range(0, 50, 5))
        ax.set_xticklabels(range(1, 51, 5), fontsize=8)
        ax.set_xlabel('Round')
        ax.set_title(title, fontweight='bold')

        # Add horizontal lines between countries
        for i in range(len(countries)):
            ax.axhline(y=i - 0.5, color='white', linewidth=0.3)

    # Legend
    legend_patches = [mpatches.Patch(color='#F5F5F5', label='No follower')]
    for i, (leader, color) in enumerate(zip(leader_order, leader_colors)):
        legend_patches.append(mpatches.Patch(color=color, label=f'Follows {leader}'))
    axes[0].legend(handles=legend_patches, loc='upper right', ncol=6, fontsize=8,
                   bbox_to_anchor=(1.0, 1.25))

    fig.suptitle('Figure 8: Following Pattern Heatmaps — S1-G1 vs Baseline vs History',
                 fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(OUT / 'fig8_heatmaps_comparison.png', facecolor='white')
    plt.close(fig)
    print("  fig8_heatmaps_comparison.png")

    # Also generate delta heatmap: S1-G1 minus Baseline
    # Where both agree on leader -> 0, where different -> show which changed
    fig2, ax = plt.subplots(figsize=(16, 7))

    # Delta: 0=same, 1=S1G1 has leader & baseline doesn't, -1=baseline has leader & S1G1 doesn't
    # 2=both have but different leaders
    delta_matrix = np.zeros_like(s1g1_matrix)
    for r in range(50):
        for c in range(19):
            s = s1g1_matrix[r, c]
            b = bl_matrix[r, c]
            if s == b:
                delta_matrix[r, c] = 0  # same
            elif s == 0 and b > 0:
                delta_matrix[r, c] = -2  # baseline follows, S1G1 doesn't
            elif s > 0 and b == 0:
                delta_matrix[r, c] = 2  # S1G1 follows, baseline doesn't
            else:
                delta_matrix[r, c] = 1 if s != b else 0  # both follow different

    delta_cmap = ListedColormap(['#E0E0E0', '#FFEB3B', '#4CAF50', '#F44336'])
    delta_bounds = [-2, -1, 0, 1, 2]
    delta_norm = BoundaryNorm(delta_bounds, delta_cmap.N)

    im = ax.imshow(delta_matrix.T, aspect='auto', cmap=delta_cmap, norm=delta_norm, interpolation='nearest')

    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries, fontsize=9)
    ax.set_xticks(range(0, 50, 5))
    ax.set_xticklabels(range(1, 51, 5), fontsize=8)
    ax.set_xlabel('Round')
    ax.set_title('Figure 9: Follower Deviation — S1-G1 vs Baseline', fontweight='bold')

    delta_legend = [
        mpatches.Patch(color='#E0E0E0', label='Same'),
        mpatches.Patch(color='#FFEB3B', label='Different leader (both follow)'),
        mpatches.Patch(color='#4CAF50', label='S1-G1 follows (Baseline none)'),
        mpatches.Patch(color='#F44336', label='Baseline follows (S1-G1 none)'),
    ]
    ax.legend(handles=delta_legend, loc='upper right', ncol=4, fontsize=8)

    fig2.tight_layout()
    fig2.savefig(OUT / 'fig9_delta_heatmap.png', facecolor='white')
    plt.close(fig2)
    print("  fig9_delta_heatmap.png")

# ================================================================
# Figure 11: Summary Dashboard
# ================================================================
def fig11_summary_dashboard():
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.35)

    # (0,0): Overall accuracy comparison - big number display
    ax_big = fig.add_subplot(gs[0, 0])
    ax_big.axis('off')
    ax_big.set_xlim(0, 10)
    ax_big.set_ylim(0, 10)

    s1g1_overall = data['accuracy']['s1g1_overall']
    bl_overall = data['accuracy']['baseline_overall']
    delta = s1g1_overall - bl_overall

    ax_big.text(5, 8.5, 'Overall Accuracy (F1 vs History)', ha='center', fontsize=13, fontweight='bold')
    ax_big.text(5, 6.5, f'{s1g1_overall:.3f}', ha='center', fontsize=36, fontweight='bold', color=COLORS['s1g1'])
    ax_big.text(5, 5.2, 'S1-G1', ha='center', fontsize=10, color=COLORS['s1g1'])
    ax_big.text(5, 4.0, f'{bl_overall:.3f}', ha='center', fontsize=28, fontweight='bold', color=COLORS['baseline'])
    ax_big.text(5, 3.0, 'Baseline (ID22)', ha='center', fontsize=10, color=COLORS['baseline'])

    delta_color = COLORS['diff_pos'] if delta > 0 else COLORS['diff_neg']
    ax_big.text(5, 1.8, f'Δ = {delta:+.3f}', ha='center', fontsize=16, fontweight='bold', color=delta_color)
    ax_big.text(5, 0.8, f'({delta/bl_overall*100:+.1f}%)', ha='center', fontsize=10, color=delta_color)

    # (0,1): Per-round accuracy
    ax_ts = fig.add_subplot(gs[0, 1])
    rounds = sorted(int(k) for k in data['accuracy']['s1g1_per_round'].keys())
    s1g1_vals = [data['accuracy']['s1g1_per_round'][str(r)] for r in rounds]
    bl_vals = [data['accuracy']['baseline_per_round'][str(r)] for r in rounds]
    ax_ts.plot(rounds, s1g1_vals, color=COLORS['s1g1'], linewidth=1.5, label='S1-G1')
    ax_ts.plot(rounds, bl_vals, color=COLORS['baseline'], linewidth=1.5, label='Baseline')
    ax_ts.set_title('Per-Round Accuracy', fontsize=11)
    ax_ts.set_ylabel('Accuracy')
    ax_ts.legend(fontsize=8)
    ax_ts.grid(True, alpha=0.3)
    ax_ts.set_ylim(0, 1.05)

    # (0,2): Respect sovereignty
    ax_rs = fig.add_subplot(gs[0, 2])
    s1g1_rs = [data['respect_sov']['s1g1'][str(r)] for r in rounds]
    bl_rs = [data['respect_sov']['baseline'][str(r)] for r in rounds]
    ax_rs.plot(rounds, s1g1_rs, color=COLORS['s1g1'], linewidth=1.5, label='S1-G1')
    ax_rs.plot(rounds, bl_rs, color=COLORS['baseline'], linewidth=1.5, label='Baseline')
    ax_rs.set_title('Respect Sovereignty', fontsize=11)
    ax_rs.set_ylabel('Ratio')
    ax_rs.legend(fontsize=8)
    ax_rs.grid(True, alpha=0.3)
    ax_rs.set_ylim(0, 1.05)

    # (1,0): Per-country accuracy
    ax_pc = fig.add_subplot(gs[1, 0])
    s1g1_country = data['accuracy']['s1g1_country']
    bl_country = data['accuracy']['baseline_country']
    countries = sorted(s1g1_country.keys())
    x = np.arange(len(countries))
    width = 0.35
    s1g1_accs = [s1g1_country[c][0] for c in countries]
    bl_accs = [bl_country.get(c, [0,0,0])[0] for c in countries]
    ax_pc.bar(x - width/2, s1g1_accs, width, label='S1-G1', color=COLORS['s1g1'])
    ax_pc.bar(x + width/2, bl_accs, width, label='Baseline', color=COLORS['baseline'])
    ax_pc.set_xticks(x)
    ax_pc.set_xticklabels(countries, fontsize=7)
    ax_pc.set_title('Per-Country Accuracy', fontsize=11)
    ax_pc.legend(fontsize=8)
    ax_pc.grid(True, alpha=0.3, axis='y')
    ax_pc.set_ylim(0, 1.15)

    # (1,1): Order distribution
    ax_ord = fig.add_subplot(gs[1, 1])
    s1g1_orders = data['order_types']['s1g1']
    bl_orders = data['order_types']['baseline']
    from collections import Counter
    s1g1_oc = Counter(s1g1_orders.values())
    bl_oc = Counter(bl_orders.values())
    all_orders = sorted(set(list(s1g1_oc.keys()) + list(bl_oc.keys())))
    s1g1_ov = [s1g1_oc.get(o, 0) for o in all_orders]
    bl_ov = [bl_oc.get(o, 0) for o in all_orders]
    x2 = np.arange(len(all_orders))
    ax_ord.bar(x2 - 0.2, s1g1_ov, 0.4, label='S1-G1', color=COLORS['s1g1'])
    ax_ord.bar(x2 + 0.2, bl_ov, 0.4, label='Baseline', color=COLORS['baseline'])
    ax_ord.set_xticks(x2)
    ax_ord.set_xticklabels(all_orders, fontsize=8)
    ax_ord.set_title('Order Type Distribution', fontsize=11)
    ax_ord.legend(fontsize=8)

    # (1,2): Leader follower distribution (histogram)
    ax_lf = fig.add_subplot(gs[1, 2])
    # For S1-G1: GMY dominant
    s1g1_lf = data['leader_followers']['s1g1']
    bl_lf = data['leader_followers']['baseline']
    leaders = sorted(set(list(s1g1_lf.keys()) + list(bl_lf.keys())))
    s1g1_total = [sum(s1g1_lf.get(l, {}).values()) for l in leaders]
    bl_total = [sum(bl_lf.get(l, {}).values()) for l in leaders]
    x3 = np.arange(len(leaders))
    ax_lf.bar(x3 - 0.2, s1g1_total, 0.4, label='S1-G1', color=COLORS['s1g1'])
    ax_lf.bar(x3 + 0.2, bl_total, 0.4, label='Baseline', color=COLORS['baseline'])
    ax_lf.set_xticks(x3)
    ax_lf.set_xticklabels(leaders, fontsize=9)
    ax_lf.set_title('Total Follower-Events by Leader', fontsize=11)
    ax_lf.legend(fontsize=8)

    # (2,0): Country switches
    ax_sw = fig.add_subplot(gs[2, 0])
    s1g1_sw = data['switches']['s1g1']
    bl_sw = data['switches']['baseline']
    all_sw = sorted(set(list(s1g1_sw.keys()) + list(bl_sw.keys())))
    s1g1_sv = [s1g1_sw.get(c, 0) for c in all_sw]
    bl_sv = [bl_sw.get(c, 0) for c in all_sw]
    x_sw = np.arange(len(all_sw))
    ax_sw.bar(x_sw - 0.2, s1g1_sv, 0.4, label='S1-G1', color=COLORS['s1g1'])
    ax_sw.bar(x_sw + 0.2, bl_sv, 0.4, label='Baseline', color=COLORS['baseline'])
    ax_sw.set_xticks(x_sw)
    ax_sw.set_xticklabels(all_sw, fontsize=7)
    ax_sw.set_title('Leader Switch Count', fontsize=11)
    ax_sw.legend(fontsize=8)
    ax_sw.grid(True, alpha=0.3, axis='y')

    # (2,1): HHI
    ax_hhi = fig.add_subplot(gs[2, 1])
    s1g1_hhi_v = [data['hhi']['s1g1'][str(r)] for r in rounds]
    bl_hhi_v = [data['hhi']['baseline'][str(r)] for r in rounds]
    ax_hhi.plot(rounds, s1g1_hhi_v, color=COLORS['s1g1'], linewidth=1.5, label='S1-G1')
    ax_hhi.plot(rounds, bl_hhi_v, color=COLORS['baseline'], linewidth=1.5, label='Baseline')
    ax_hhi.set_title('Follower Concentration (HHI)', fontsize=11)
    ax_hhi.legend(fontsize=8)
    ax_hhi.grid(True, alpha=0.3)

    # (2,2): Key findings text box
    ax_txt = fig.add_subplot(gs[2, 2])
    ax_txt.axis('off')
    findings = [
        f"Key Findings:",
        f"",
        f"1. Overall accuracy dropped from {bl_overall:.3f} to {s1g1_overall:.3f}",
        f"   (Δ = {delta:+.3f}, {delta/bl_overall*100:+.1f}%)",
        f"",
        f"2. GMY (王道型) became dominant leader:",
        f"   mean {np.mean(list(data['leader_followers']['s1g1'].get('GMY', {}).values())):.1f} followers/round",
        f"   vs {np.mean(list(data['leader_followers']['baseline'].get('UKG', {}).values())):.1f} for UKG in baseline",
        f"",
        f"3. Order shifted from 恐怖平衡-dominated",
        f"   to 大棒威慑-dominated (90% vs 28%)",
        f"",
        f"4. Respect sovereignty improved:",
        f"   {np.mean(s1g1_rs):.3f} vs {np.mean(bl_rs):.3f}",
        f"",
        f"5. Follower concentration (HHI) more stable",
        f"   in S1-G1 (std={np.std(s1g1_hhi_v):.3f}) vs",
        f"   baseline (std={np.std(bl_hhi_v):.3f})",
    ]
    ax_txt.text(0, 1, '\n'.join(findings), transform=ax_txt.transAxes,
                fontsize=8.5, va='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#F5F5F5', alpha=0.9))

    fig.suptitle('Figure 10: S1-G1 Experimental Results — Summary Dashboard',
                 fontsize=15, fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(OUT / 'fig10_summary_dashboard.png', facecolor='white', dpi=200)
    plt.close(fig)
    print("  fig10_summary_dashboard.png")

# ================================================================
# Run all
# ================================================================
if __name__ == '__main__':
    print("Generating figures...")
    fig1_f1_timeseries()
    fig2_per_country()
    fig3_order_distribution()
    fig4_respect_sov_timeseries()
    fig5_hhi_timeseries()
    fig6_leader_followers()
    fig7_country_switches()
    fig_heatmaps()
    fig11_summary_dashboard()
    print(f"\nAll figures saved to {OUT.absolute()}")
