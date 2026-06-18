"""Generate extended analysis figures for S1-G1 report: strategic goals + order dimensions."""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import defaultdict

# Font setup
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

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': [CJK_FONT, 'DejaVu Sans'] if CJK_FONT else ['DejaVu Sans'],
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'axes.unicode_minus': False,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
})

OUT = __import__('pathlib').Path('docs/id52/figures')
with open('data/analysis_extended_s1g1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('data/analysis_s1g1_vs_baseline.json', 'r', encoding='utf-8') as f:
    base = json.load(f)

COLORS = {'s1g1': '#2196F3', 'baseline': '#FF9800', 'grid': '#E0E0E0',
          'pos': '#4CAF50', 'neg': '#F44336'}

THEORY_ORDER = ['GMY','RUS','UKG','FRN','AUH','ITA','TUR','BUL','SPN','BEL',
                'GRC','SWD','NTH','ROM','POR','DEN','SWZ','YUG','NOR']

# ================================================================
# fig11: Strategic Goal Achievement Trends (per country, both projects)
# ================================================================
def fig11_goal_trends():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    periods = [10, 20, 30, 40, 50]
    cmap = plt.get_cmap('tab20', 19)

    for ax, label in [(ax1, 'S1-G1'), (ax2, 'Baseline')]:
        goal = data[label]['goal_achievement']
        for i, code in enumerate(THEORY_ORDER):
            if code in goal['per_country']:
                trend = goal['per_country'][code]['trend']
                ax.plot(periods, trend, color=cmap(i), linewidth=1.5, marker='o', markersize=4, label=code)

        ax.set_xlabel('Evaluation Round')
        ax.set_ylabel('Goal Achievement Score')
        ax.set_title(f'{label}')
        ax.set_ylim(0, 105)
        ax.set_xlim(5, 55)
        ax.grid(True, alpha=0.3, color=COLORS['grid'])
        ax.legend(loc='upper left', ncol=3, fontsize=6)

    fig.suptitle('Figure 11: Strategic Goal Achievement Trends — Per Country (19 countries)',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(OUT / 'fig11_goal_achievement_trends.png', facecolor='white')
    plt.close(fig)
    print("  fig11_goal_achievement_trends.png")

# ================================================================
# fig12: Goal Achievement by Power Level + Great Power Comparison
# ================================================================
def fig12_goal_power_level():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: Per-period average goal achievement
    periods = [10, 20, 30, 40, 50]
    for label, color, marker in [('S1-G1', COLORS['s1g1'], 'o'), ('Baseline', COLORS['baseline'], 's')]:
        goal = data[label]['goal_achievement']
        avg = [goal['per_period_avg'][str(p)] for p in periods]
        ax1.plot(periods, avg, color=color, linewidth=2, marker=marker, markersize=6, label=label)
        ax1.fill_between(periods, avg, alpha=0.1, color=color)

    ax1.set_xlabel('Evaluation Round (cumulative)')
    ax1.set_ylabel('Mean Goal Achievement Score')
    ax1.set_title('Average Goal Achievement Over Time')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, color=COLORS['grid'])
    ax1.set_ylim(40, 80)

    # Panel 2: Great power goal achievement comparison
    x = np.arange(5)
    width = 0.3
    gp_codes = ['GMY', 'RUS', 'UKG', 'FRN', 'AUH']
    for i, label in enumerate(['S1-G1', 'Baseline']):
        goal = data[label]['goal_achievement']
        scores = []
        for code in gp_codes:
            if code in goal['per_country']:
                scores.append(goal['per_country'][code]['mean'])
            else:
                scores.append(0)
        bars = ax2.bar(x + (i-0.5)*width, scores, width, label=label,
                       color=COLORS['s1g1'] if label == 'S1-G1' else COLORS['baseline'],
                       alpha=0.9 if label == 'S1-G1' else 0.7)
        # Annotate
        for bar, score in zip(bars, scores):
            if score > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{score:.0f}', ha='center', fontsize=8, fontweight='bold')

    ax2.set_xticks(x)
    ax2.set_xticklabels(gp_codes, fontsize=10)
    ax2.set_ylabel('Mean Goal Achievement Score')
    ax2.set_title('Great Power Goal Achievement Comparison')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y', color=COLORS['grid'])

    fig.suptitle('Figure 12: Strategic Goal Achievement — System-Level Trends & Great Power Comparison',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(OUT / 'fig12_goal_power_level.png', facecolor='white')
    plt.close(fig)
    print("  fig12_goal_power_level.png")

# ================================================================
# fig13: Action Mix Evolution (per round action category trends)
# ================================================================
def fig13_action_mix_evolution():
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    category_map = {
        '信息手段': 'Information',
        '军事手段': 'Military',
        '外交手段': 'Diplomatic',
        '经济手段': 'Economic'
    }
    cat_colors = {'信息手段': '#9C27B0', '军事手段': '#F44336', '外交手段': '#4CAF50', '经济手段': '#2196F3'}

    for row, label in enumerate(['S1-G1', 'Baseline']):
        ap = data[label]['action_profile']
        # Per-round data
        per_round = ap['per_round']
        rounds = sorted(int(k) for k in per_round.keys())
        cats = sorted(category_map.keys())

        # Panel A (left): stacked area chart
        ax_area = axes[row, 0]
        stack_data = {cat: [] for cat in cats}
        for rn in rounds:
            rd = per_round[str(rn)]
            for cat in cats:
                stack_data[cat].append(rd.get(cat, 0))

        ax_area.stackplot(rounds, [stack_data[cat] for cat in cats],
                          labels=[category_map[c] for c in cats],
                          colors=[cat_colors[c] for c in cats], alpha=0.8)

        ax_area.set_xlabel('Round')
        ax_area.set_ylabel('Action Count')
        ax_area.set_title(f'{label} — Action Mix Over Time (Stacked)')
        ax_area.legend(loc='upper left', fontsize=8)
        ax_area.set_xlim(0, 51)
        ax_area.grid(True, alpha=0.3, color=COLORS['grid'])

        # Panel B (right): normalized percentage area
        ax_pct = axes[row, 1]
        total_per_round = [sum(stack_data[cat][i] for cat in cats) for i in range(len(rounds))]
        pct_data = {}
        for cat in cats:
            pct_data[cat] = [stack_data[cat][i]/total_per_round[i]*100 if total_per_round[i] > 0 else 0
                            for i in range(len(rounds))]

        ax_pct.stackplot(rounds, [pct_data[cat] for cat in cats],
                        labels=[category_map[c] for c in cats],
                        colors=[cat_colors[c] for c in cats], alpha=0.8)

        ax_pct.set_xlabel('Round')
        ax_pct.set_ylabel('Percentage (%)')
        ax_pct.set_title(f'{label} — Action Mix Over Time (Normalized %)')
        ax_pct.legend(loc='upper left', fontsize=8)
        ax_pct.set_xlim(0, 51)
        ax_pct.set_ylim(0, 100)
        ax_pct.grid(True, alpha=0.3, color=COLORS['grid'])

    fig.suptitle('Figure 13: Action Category Evolution — S1-G1 vs Baseline',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(OUT / 'fig13_action_mix_evolution.png', facecolor='white')
    plt.close(fig)
    print("  fig13_action_mix_evolution.png")

# ================================================================
# fig14: Great Power Action Profiles (radar-like bar chart)
# ================================================================
def fig14_gp_action_profiles():
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    all_gps = set()
    for label in ['S1-G1', 'Baseline']:
        all_gps.update(data[label]['gp_action_profiles'].keys())
    all_gps = sorted(all_gps)

    category_map = {'信息手段': 'Info', '军事手段': 'Mil', '外交手段': 'Diplo', '经济手段': 'Econ'}
    cats = ['信息手段', '军事手段', '外交手段', '经济手段']
    cat_colors = ['#9C27B0', '#F44336', '#4CAF50', '#2196F3']

    for col, code in enumerate(all_gps[:6]):
        ax = axes[0, col] if col < 3 else axes[1, col-3]

        x = np.arange(4)
        width = 0.3
        for i, label in enumerate(['S1-G1', 'Baseline']):
            if code in data[label]['gp_action_profiles']:
                profile = data[label]['gp_action_profiles'][code]
                vals = [profile['categories'].get(cat, {}).get('total', 0) for cat in cats]
                total = sum(vals)
                pcts = [v/total*100 if total > 0 else 0 for v in vals]
                rs_rate = profile.get('respect_sov_rate', 0)
                ax.bar(x + (i-0.5)*width, pcts, width,
                       label=f'{label} (RS={rs_rate}%)',
                       color=COLORS['s1g1'] if label == 'S1-G1' else COLORS['baseline'],
                       alpha=0.9 if label == 'S1-G1' else 0.7)

        ax.set_xticks(x)
        ax.set_xticklabels([category_map[c] for c in cats], fontsize=9)
        ax.set_title(f'{code}', fontweight='bold', fontsize=11)
        ax.set_ylim(0, 80)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3, axis='y', color=COLORS['grid'])

        # Hide unused subplot if any
    for col in range(len(all_gps), 6):
        ax = axes[0, col] if col < 3 else axes[1, col-3]
        ax.axis('off')

    fig.suptitle('Figure 14: Great Power Action Profiles — Category Mix & Respect Sovereignty Rate',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(OUT / 'fig14_gp_action_profiles.png', facecolor='white')
    plt.close(fig)
    print("  fig14_gp_action_profiles.png")

# ================================================================
# fig15: Order Dimensions Composite — respect_sov, action mix, goal, HHI
# ================================================================
def fig15_order_dimensions():
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    periods = [10, 20, 30, 40, 50]

    # (0,0): Respect sov by stage
    ax = axes[0, 0]
    stages = ['initiative', 'response']
    x = np.arange(len(stages))
    width = 0.3
    for i, label in enumerate(['S1-G1', 'Baseline']):
        rates = [data[label]['rs_by_stage'][s]['rate'] for s in stages]
        ax.bar(x + (i-0.5)*width, rates, width, label=label,
               color=COLORS['s1g1'] if label == 'S1-G1' else COLORS['baseline'])
        for j, rate in enumerate(rates):
            ax.text(x[j] + (i-0.5)*width, rate + 1, f'{rate}%', ha='center', fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(['Initiative', 'Response'])
    ax.set_title('Respect Sovereign by Stage')
    ax.set_ylim(0, 65)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    # (0,1): Goal achievement trend (system avg)
    ax = axes[0, 1]
    for label, color, marker in [('S1-G1', COLORS['s1g1'], 'o'), ('Baseline', COLORS['baseline'], 's')]:
        goal = data[label]['goal_achievement']
        avg = [goal['per_period_avg'][str(p)] for p in periods]
        ax.plot(periods, avg, color=color, linewidth=2, marker=marker, markersize=6, label=label)
    ax.set_xlabel('Evaluation Period')
    ax.set_ylabel('Mean Goal Score')
    ax.set_title('System Average Goal Achievement')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])

    # (0,2): Action effectiveness trend
    ax = axes[0, 2]
    for label, color, marker in [('S1-G1', COLORS['s1g1'], 'o'), ('Baseline', COLORS['baseline'], 's')]:
        goal = data[label]['goal_achievement']
        ae = [goal['per_period_action_eff'][str(p)] for p in periods]
        ax.plot(periods, ae, color=color, linewidth=2, marker=marker, markersize=6, label=label)
    ax.set_xlabel('Evaluation Period')
    ax.set_ylabel('Action Effectiveness')
    ax.set_title('Action Effectiveness Trend')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])

    # (1,0): Action mix overall comparison
    ax = axes[1, 0]
    cats = ['信息手段', '军事手段', '外交手段', '经济手段']
    x = np.arange(len(cats))
    for i, label in enumerate(['S1-G1', 'Baseline']):
        overall = data[label]['overall_actions']
        vals = [overall.get(cat, {}).get('total', 0) for cat in cats]
        total = sum(vals)
        pcts = [v/total*100 for v in vals] if total else [0]*4
        ax.bar(x + (i-0.5)*width, pcts, width, label=f'{label} (n={total})',
               color=COLORS['s1g1'] if label == 'S1-G1' else COLORS['baseline'])
    ax.set_xticks(x)
    ax.set_xticklabels(['Info', 'Military', 'Diplomatic', 'Economic'])
    ax.set_title('Overall Action Mix (%)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    # (1,1): RS rate comparison by country category
    ax = axes[1, 1]
    # For each project, calculate average RS rate across all action categories
    for i, label in enumerate(['S1-G1', 'Baseline']):
        overall = data[label]['overall_actions']
        total_rs = sum(v.get('respect_sov', 0) for v in overall.values())
        total_all = sum(v.get('total', 0) for v in overall.values())
        rs_rate = total_rs/total_all*100 if total_all else 0

        # Per category RS rate
        cat_rates = {}
        for cat in cats:
            v = overall.get(cat, {})
            if v.get('total', 0) > 0:
                cat_rates[cat] = v['respect_sov']/v['total']*100
            else:
                cat_rates[cat] = 0

        ax.bar(x + (i-0.5)*width, [cat_rates[c] for c in cats], width, label=f'{label} (avg={rs_rate:.1f}%)',
               color=COLORS['s1g1'] if label == 'S1-G1' else COLORS['baseline'])
    ax.set_xticks(x)
    ax.set_xticklabels(['Info', 'Military', 'Diplomatic', 'Economic'])
    ax.set_title('Respect Sovereignty Rate by Action Type')
    ax.set_ylim(0, 105)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    # (1,2): Per-country goal achievement delta (S1-G1 - Baseline)
    ax = axes[1, 2]
    deltas = {}
    for code in THEORY_ORDER:
        s1g1_mean = data['S1-G1']['goal_achievement']['per_country'].get(code, {}).get('mean', 0)
        bl_mean = data['Baseline']['goal_achievement']['per_country'].get(code, {}).get('mean', 0)
        if s1g1_mean > 0 or bl_mean > 0:
            deltas[code] = s1g1_mean - bl_mean

    codes_sorted = sorted(deltas.keys(), key=lambda c: deltas[c])
    colors_delta = [COLORS['pos'] if deltas[c] >= 0 else COLORS['neg'] for c in codes_sorted]
    ax.barh(range(len(codes_sorted)), [deltas[c] for c in codes_sorted], color=colors_delta, alpha=0.8)
    ax.set_yticks(range(len(codes_sorted)))
    ax.set_yticklabels(codes_sorted, fontsize=9)
    ax.set_xlabel('Δ Goal Achievement (S1-G1 - Baseline)')
    ax.set_title('Per-Country Goal Achievement Delta')
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.grid(True, alpha=0.3, axis='x', color=COLORS['grid'])

    fig.suptitle('Figure 15: International Order Dimensions — Composite Analysis',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(OUT / 'fig15_order_dimensions.png', facecolor='white')
    plt.close(fig)
    print("  fig15_order_dimensions.png")

if __name__ == '__main__':
    print("Generating extended figures...")
    fig11_goal_trends()
    fig12_goal_power_level()
    fig13_action_mix_evolution()
    fig14_gp_action_profiles()
    fig15_order_dimensions()
    print(f"\nAll extended figures saved to {OUT.absolute()}")
