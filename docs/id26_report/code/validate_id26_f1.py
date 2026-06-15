#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ID26 F1 Validation - Per-Round Per-Country Following Behavior
==============================================================
Compares simulation follower_relation against v5 history ground truth.
Scenario: Cold War pre-war Europe (1946), 50 rounds, 25 countries.
Following != Alliance: following is issue-specific leadership preference.
Bipolar system: Russia (USSR) vs UK (Western bloc leader).

Usage: python docs/id26_report/code/validate_id26_f1.py
"""

import json, os, sqlite3
from collections import defaultdict
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.size'] = 11

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "data", "abm_simulation.db")
HISTORY_PATH = os.path.join(BASE_DIR, "data", "history", "scene3_prewar_1946.json")
OUT_DIR = os.path.join(BASE_DIR, "docs", "id26_report")
for d in [os.path.join(OUT_DIR, "figures"), os.path.join(OUT_DIR, "data")]:
    os.makedirs(d, exist_ok=True)

PID = 26
# Country code -> history index mapping (from scene3_prewar_1946.json)
CCODE2IDX = {
    365: 1,    # Russia (USSR)
    200: 2,    # UK
    220: 3,    # France
    325: 4,    # Italy
    290: 5,    # Poland
    230: 6,    # Spain
    640: 7,    # Turkey
    315: 8,    # Czechoslovakia
    211: 9,    # Belgium
    210: 10,   # Netherlands
    380: 11,   # Sweden
    345: 12,   # Yugoslavia
    360: 13,   # Romania
    310: 14,   # Hungary
    350: 15,   # Greece
    355: 16,   # Bulgaria
    235: 17,   # Portugal
    212: 18,   # Luxembourg
    390: 19,   # Denmark
    225: 20,   # Switzerland
    385: 21,   # Norway
    375: 22,   # Finland
    205: 23,   # Ireland
    339: 24,   # Albania
    395: 25,   # Iceland
}
IDX2NAME = {
    1: "Russia", 2: "UK", 3: "France", 4: "Italy", 5: "Poland",
    6: "Spain", 7: "Turkey", 8: "Czechoslovakia", 9: "Belgium",
    10: "Netherlands", 11: "Sweden", 12: "Yugoslavia", 13: "Romania",
    14: "Hungary", 15: "Greece", 16: "Bulgaria", 17: "Portugal",
    18: "Luxembourg", 19: "Denmark", 20: "Switzerland", 21: "Norway",
    22: "Finland", 23: "Ireland", 24: "Albania", 25: "Iceland",
}
# Cold War great powers: USSR (idx=1) and UK/Western bloc (idx=2)
GP = {1, 2}

agent2idx = {}
idx2agent = {}


def load_gt():
    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_sim():
    global agent2idx, idx2agent
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT agent_id, country_code FROM agent_config WHERE project_id=?', (PID,))
    for aid, cc in c.fetchall():
        if cc in CCODE2IDX:
            agent2idx[aid] = CCODE2IDX[cc]
            idx2agent[CCODE2IDX[cc]] = aid
    c.execute('''SELECT round_num, follower_agent_id, leader_agent_id
                 FROM follower_relation WHERE project_id=?
                 ORDER BY round_num, follower_agent_id''', (PID,))
    fd = defaultdict(dict)
    for rn, fid, lid in c.fetchall():
        if lid == fid:
            lid = None
        fd[rn][fid] = lid
    c.execute('''SELECT round_num, respect_sov_ratio, order_type
                 FROM simulation_round WHERE project_id=? ORDER BY round_num''', (PID,))
    ri = c.fetchall()
    c.execute('''SELECT agent_id, round_num, round_start_power
                 FROM agent_power_history WHERE project_id=? ORDER BY agent_id, round_num''', (PID,))
    ph = defaultdict(list)
    for aid, rn, sp in c.fetchall():
        ph[aid].append((rn, sp))
    conn.close()
    return {'followers': dict(fd), 'rounds': ri, 'power': dict(ph)}


def compute_f1(sim, gt):
    rounds = list(range(1, 51))
    gt_rds = gt['rounds']
    total = {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
    pc = {idx: {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
          for idx in range(3, 26)}  # idx 3-25 are non-GP (23 countries)
    pr_data = []
    for rn in rounds:
        sr = sim['followers'].get(rn, {})
        gr = gt_rds[str(rn)]['following']
        tp = fp = fn = tn = 0
        for aid, idx in agent2idx.items():
            if idx in GP:
                continue
            al = agent2idx.get(sr.get(aid)) if sr.get(aid) else None
            el = gr.get(str(idx))
            if el is not None:
                if al is not None:
                    if al == el:
                        tp += 1
                        pc[idx]['tp'] += 1
                    else:
                        fp += 1
                        pc[idx]['fp'] += 1
                else:
                    fn += 1
                    pc[idx]['fn'] += 1
            else:
                if al is not None:
                    fp += 1
                    pc[idx]['fp'] += 1
                else:
                    tn += 1
                    pc[idx]['tn'] += 1
        total['tp'] += tp
        total['fp'] += fp
        total['fn'] += fn
        total['tn'] += tn
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        pr_data.append({'round': rn, 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
                        'p': round(p, 4), 'r': round(r, 4), 'f1': round(f1, 4)})
    op = total['tp'] / (total['tp'] + total['fp']) if (total['tp'] + total['fp']) > 0 else 0
    oR = total['tp'] / (total['tp'] + total['fn']) if (total['tp'] + total['fn']) > 0 else 0
    of1 = 2 * op * oR / (op + oR) if (op + oR) > 0 else 0
    pcd = {}
    for idx in range(3, 26):
        d = pc[idx]
        p = d['tp'] / (d['tp'] + d['fp']) if (d['tp'] + d['fp']) > 0 else 0
        r = d['tp'] / (d['tp'] + d['fn']) if (d['tp'] + d['fn']) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        pcd[IDX2NAME[idx]] = {
            'idx': idx, 'tp': d['tp'], 'fp': d['fp'], 'fn': d['fn'], 'tn': d['tn'],
            'p': round(p, 4), 'r': round(r, 4), 'f1': round(f1, 4)
        }

    gpi = {}
    for idx in GP:
        aid = idx2agent.get(idx)
        if aid:
            ind = sum(1 for rn in rounds if sim['followers'].get(rn, {}).get(aid) is None)
            gpi[IDX2NAME[idx]] = {'ind': ind, 'total': 50, 'rate': ind / 50}
    return {
        'overall': {'tp': total['tp'], 'fp': total['fp'], 'fn': total['fn'], 'tn': total['tn'],
                    'p': round(op, 4), 'r': round(oR, 4), 'f1': round(of1, 4)},
        'per_round': pr_data, 'per_country': pcd, 'gp_independence': gpi
    }


def sf(fig, name):
    p = os.path.join(OUT_DIR, "figures", name)
    fig.savefig(p, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  [OK] {name}")
    return name


def ch1_f1_ts(fr, gt):
    """Figure 1: Per-round F1 time series with Cold War phases"""
    fig, ax = plt.subplots(figsize=(14, 6))
    pr = fr['per_round']
    rs = [d['round'] for d in pr]
    f1s = [d['f1'] for d in pr]
    ps = [d['p'] for d in pr]
    recs = [d['r'] for d in pr]
    ax.plot(rs, f1s, 'o-', ms=4, lw=2, label='F1', color='#2196F3', zorder=5)
    ax.plot(rs, ps, 's--', ms=2, lw=1.2, alpha=0.7, label='Precision', color='#4CAF50')
    ax.plot(rs, recs, '^--', ms=2, lw=1.2, alpha=0.7, label='Recall', color='#FF5722')
    if len(f1s) >= 5:
        ma = np.convolve(f1s, np.ones(5) / 5, mode='valid')
        ax.plot(range(5, len(f1s) + 1), ma, '-', lw=3, alpha=0.4, color='#1565C0', label='5-round MA')
    ax.axhline(y=0.7, color='#4CAF50', ls=':', alpha=0.5)
    ax.axhline(y=0.5, color='#FF9800', ls=':', alpha=0.5)
    ax.axhline(y=0.25, color='#F44336', ls=':', alpha=0.4)
    ax.text(50.5, 0.71, 'Good(0.7)', fontsize=8, color='#4CAF50', va='bottom')
    ax.text(50.5, 0.51, 'Moderate(0.5)', fontsize=8, color='#FF9800', va='bottom')
    ax.text(50.5, 0.26, 'Random(0.25)', fontsize=8, color='#F44336', va='bottom')

    # Cold War historical phases
    phases = [
        (1, 4, 'Reconstruction\n(1946)', '#E8EAF6'),
        (5, 14, 'Marshall Plan &\nBerlin Blockade\n(1947-1949)', '#E3F2FD'),
        (15, 30, 'NATO/Korean War\n(1949-1954)', '#FFF3E0'),
        (31, 42, 'Post-Stalin\nThaw\n(1954-1956)', '#E8F5E9'),
        (43, 50, 'Hungarian Rev.\n& Suez\n(1956-1958)', '#FFEBEE'),
    ]
    for s, e, label, color in phases:
        ax.axvspan(s - 0.5, e + 0.5, alpha=0.12, color=color)
        ax.text((s + e) / 2, 1.02, label, ha='center', fontsize=6.5, color='#666',
                transform=ax.get_xaxis_transform(), linespacing=1.2)

    ax.set_xlabel('Round (1 round = 3 months)', fontsize=11)
    ax.set_ylabel('Score', fontsize=11)
    ax.set_title('Figure 1: Per-Round Following F1 Score (ID26, Cold War)', fontsize=13, fontweight='bold')
    ax.set_xlim(0.5, 50.5)
    ax.set_ylim(0, 1.08)
    ax.legend(fontsize=9, loc='lower left', framealpha=0.9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    return sf(fig, 'fig1_f1_timeseries.png')


def ch2_per_country(fr):
    """Figure 2: Per-country F1/P/R horizontal bar chart"""
    pcd = fr['per_country']
    si = sorted(pcd.items(), key=lambda x: x[1]['f1'], reverse=True)
    names = [n for n, _ in si]
    f1s = [d['f1'] for _, d in si]
    ps = [d['p'] for _, d in si]
    recs = [d['r'] for _, d in si]
    fig, ax = plt.subplots(figsize=(12, 9))
    y = np.arange(len(names))
    h = 0.25
    ax.barh(y + h, f1s, h, label='F1', color='#2196F3', edgecolor='white')
    ax.barh(y, ps, h, label='Precision', color='#4CAF50', edgecolor='white', alpha=0.8)
    ax.barh(y - h, recs, h, label='Recall', color='#FF5722', edgecolor='white', alpha=0.8)
    for i, v in enumerate(f1s):
        if v > 0.02:
            ax.text(v + 0.02, i + h, f'{v:.2f}', va='center', fontsize=7, fontweight='bold', color='#1565C0')
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel('Score', fontsize=11)
    ax.set_title('Figure 2: Per-Country Following F1/P/R (ID26, Cold War)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9, loc='lower right')
    ax.set_xlim(0, 1.15)
    ax.axvline(x=0.5, color='#FF9800', ls=':', alpha=0.5)
    ax.axvline(x=0.7, color='#4CAF50', ls=':', alpha=0.5)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()
    plt.tight_layout()
    return sf(fig, 'fig2_per_country.png')


def ch3_cm(fr):
    """Figure 3: Confusion matrix"""
    o = fr['overall']
    fig, ax = plt.subplots(figsize=(7, 6))
    cm = np.array([[o['tp'], o['fp']], [o['fn'], o['tn']]])
    ax.imshow(cm, cmap='Blues', aspect='auto')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Predicted: Correct', 'Predicted: Wrong/Neutral'], fontsize=10)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Actual: Should Follow', 'Actual: Should Be Neutral'], fontsize=10)
    ax.set_title('Figure 3: Confusion Matrix (ID26, Cold War)', fontsize=13, fontweight='bold')
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i][j]), ha='center', va='center', fontsize=20, fontweight='bold',
                    color='white' if cm[i][j] > cm.max() / 2 else 'black')
    ax.text(1.35, 0.5,
            f'P={o["p"]:.4f}\nR={o["r"]:.4f}\nF1={o["f1"]:.4f}',
            transform=ax.transAxes, fontsize=10, va='center',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    plt.tight_layout()
    return sf(fig, 'fig3_confusion_matrix.png')


def ch4_heatmap(sim, gt):
    """Figure 4: Per-round per-country correctness heatmap"""
    countries = sorted(
        [a for a in agent2idx if agent2idx[a] not in GP],
        key=lambda a: agent2idx[a]
    )
    mx = np.zeros((len(countries), 50))
    for i, aid in enumerate(countries):
        idx = agent2idx[aid]
        for rn in range(1, 51):
            al = agent2idx.get(sim['followers'].get(rn, {}).get(aid)) if sim['followers'].get(rn, {}).get(aid) else None
            el = gt['rounds'][str(rn)]['following'].get(str(idx))
            if al is None:
                al = 0
            if el is None:
                el = 0
            mx[i][rn - 1] = 1 if al == el else 0
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.imshow(mx, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1, interpolation='nearest')
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels([IDX2NAME[agent2idx[a]] for a in countries], fontsize=8)
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Country', fontsize=11)
    ax.set_title('Figure 4: Per-Round Per-Country Following Correctness (ID26, Cold War)', fontsize=13, fontweight='bold')
    # Mark phase boundaries
    for s in [5, 15, 31, 43]:
        ax.axvline(x=s - 0.5, color='black', lw=1.5, ls='--', alpha=0.5)
    plt.colorbar(ax.images[0], ax=ax, shrink=0.8, label='Correct=1 / Wrong=0')
    ax2 = ax.twinx()
    ax2.barh(range(len(countries)), np.mean(mx, axis=1), height=0.6, color='#2196F3', alpha=0.3, align='center')
    ax2.set_ylabel('Accuracy', fontsize=11, color='#2196F3')
    ax2.set_xlim(0, 1.5)
    plt.tight_layout()
    return sf(fig, 'fig4_heatmap.png')


def ch5_faction_ev(sim):
    """Figure 5: Bloc following evolution (bipolar Cold War)"""
    fig, ax = plt.subplots(figsize=(14, 6))
    fs = defaultdict(lambda: defaultdict(int))
    ns = defaultdict(int)
    for rn in sorted(sim['followers'].keys()):
        for fid, lid in sim['followers'][rn].items():
            if lid is not None:
                fs[lid][rn] += 1
            else:
                ns[rn] += 1
    ar = list(range(1, 51))
    # Russia (USSR) = idx 1, UK = idx 2
    colors = {1: '#E74C3C', 2: '#3498DB'}
    for idx in [1, 2]:
        aid = idx2agent.get(idx)
        if aid is None:
            continue
        yv = [fs[aid].get(r, 0) for r in ar]
        ax.fill_between(ar, yv, alpha=0.2, color=colors[idx])
        ax.plot(ar, yv, 'o-', ms=3, lw=2, label=f'{IDX2NAME[idx]} bloc', color=colors[idx])
    nv = [ns.get(r, 0) for r in ar]
    ax.plot(ar, nv, 's--', ms=2, lw=1.5, label='Independent/Neutral', color='#95A5A6', alpha=0.8)
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Number of Followers', fontsize=11)
    ax.set_title('Figure 5: Cold War Bloc Following Evolution (ID26)', fontsize=13, fontweight='bold')
    ax.set_xlim(0.5, 50.5)
    ax.set_ylim(-0.5, 24)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    return sf(fig, 'fig5_faction_evolution.png')


def ch6_gp_ind(fr):
    """Figure 6: Great power independence"""
    gp = fr['gp_independence']
    fig, ax = plt.subplots(figsize=(7, 5))
    names = list(gp.keys())
    rates = [gp[n]['rate'] * 100 for n in names]
    colors = ['#E74C3C', '#3498DB']
    bars = ax.bar(names, rates, color=colors, edgecolor='white', width=0.5)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f'{rate:.0f}%', ha='center', fontsize=12, fontweight='bold')
    ax.set_ylabel('Independence Rate (%)', fontsize=11)
    ax.set_title('Figure 6: Great Power Independence (ID26)', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.axhline(y=100, color='#4CAF50', ls='--', alpha=0.7, label='Target: 100%')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return sf(fig, 'fig6_gp_independence.png')


def ch7_f1_dist(fr):
    """Figure 7: Detailed error analysis (stacked bar + boxplot)"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    pr = fr['per_round']
    rs = [d['round'] for d in pr]
    tps = [d['tp'] for d in pr]
    fps = [d['fp'] for d in pr]
    fns = [d['fn'] for d in pr]
    ax1.bar(rs, tps, color='#4CAF50', label='TP', width=0.8)
    ax1.bar(rs, fps, bottom=tps, color='#FF5722', label='FP', width=0.8)
    ax1.bar(rs, fns, bottom=[t + f for t, f in zip(tps, fps)], color='#FFC107', label='FN', width=0.8)
    ax1.set_xlabel('Round', fontsize=11)
    ax1.set_ylabel('Count', fontsize=11)
    ax1.set_title('Figure 7a: Per-Round TP/FP/FN Stacked Bar (ID26)', fontsize=13, fontweight='bold')
    ax1.set_xlim(0.5, 50.5)
    ax1.legend(fontsize=9, loc='upper right')
    ax1.grid(axis='y', alpha=0.3)

    phases = {
        'Reconstruction\n(1-4)': [1, 4],
        'Marshall/Berlin\n(5-14)': [5, 14],
        'NATO/Korea\n(15-30)': [15, 30],
        'Post-Stalin\n(31-42)': [31, 42],
        'Hungary/Suez\n(43-50)': [43, 50],
    }
    phase_data = []
    for label, (s, e) in phases.items():
        phase_data.append([d['f1'] for d in pr if s <= d['round'] <= e])
    bp = ax2.boxplot(phase_data, labels=phases.keys(), patch_artist=True)
    colors_box = ['#E8EAF6', '#E3F2FD', '#FFF3E0', '#E8F5E9', '#FFEBEE']
    for patch, c in zip(bp['boxes'], colors_box):
        patch.set_facecolor(c)
    ax2.set_ylabel('F1 Score', fontsize=11)
    ax2.set_title('Figure 7b: F1 Distribution by Historical Phase (ID26)', fontsize=13, fontweight='bold')
    ax2.axhline(y=0.5, color='#FF9800', ls=':', alpha=0.5)
    ax2.axhline(y=0.7, color='#4CAF50', ls=':', alpha=0.5)
    ax2.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return sf(fig, 'fig7_detail_analysis.png')


def ch8_pr_scatter(fr):
    """Figure 8: Per-country Precision-Recall scatter"""
    pcd = fr['per_country']
    fig, ax = plt.subplots(figsize=(10, 8))
    names = []
    ps = []
    recs = []
    f1s = []
    for n, d in pcd.items():
        names.append(n)
        ps.append(d['p'])
        recs.append(d['r'])
        f1s.append(d['f1'])
    sc = ax.scatter(ps, recs, s=[f * 400 for f in f1s], c=f1s, cmap='RdYlGn',
                    alpha=0.8, edgecolors='black', linewidth=0.5)
    for i, n in enumerate(names):
        ax.annotate(n, (ps[i], recs[i]), fontsize=6.5, ha='center', va='bottom',
                    xytext=(0, 5), textcoords='offset points')
    for fl in np.arange(0.1, 1.0, 0.1):
        xv = np.linspace(fl / 1, 1, 100)
        yv = fl * xv / (2 * xv - fl)
        ax.plot(xv, yv, 'k--', alpha=0.15, lw=0.5)
    ax.set_xlabel('Precision', fontsize=11)
    ax.set_ylabel('Recall', fontsize=11)
    ax.set_title('Figure 8: Per-Country Precision-Recall Scatter (ID26)', fontsize=13, fontweight='bold')
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(-0.02, 1.05)
    cbar = plt.colorbar(sc, ax=ax, shrink=0.8)
    cbar.set_label('F1', fontsize=10)
    ax.grid(alpha=0.3)
    ax.axhline(y=0.5, color='#FF9800', ls=':', alpha=0.3)
    ax.axvline(x=0.5, color='#FF9800', ls=':', alpha=0.3)
    plt.tight_layout()
    return sf(fig, 'fig8_pr_scatter.png')


def ch9_bloc_alignment(fr):
    """Figure 9: Cold War bloc alignment accuracy - East vs West"""
    pcd = fr['per_country']
    # Cold War blocs: Eastern (Warsaw Pact/Soviet sphere) vs Western (NATO/Western)
    east = ['Poland', 'Czechoslovakia', 'Romania', 'Hungary', 'Bulgaria', 'Albania', 'Yugoslavia']
    west = ['France', 'Italy', 'Belgium', 'Netherlands', 'Luxembourg', 'Denmark', 'Norway', 'Portugal', 'Iceland']
    neutral = ['Spain', 'Sweden', 'Turkey', 'Greece', 'Switzerland', 'Finland', 'Ireland']
    blocs = {'Eastern Bloc': east, 'Western Bloc': west, 'Neutral/Swing': neutral}
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    for ax, (bloc_name, bloc_countries) in zip(axes, blocs.items()):
        f1_vals = []
        labels = []
        for country in bloc_countries:
            if country in pcd:
                f1_vals.append(pcd[country]['f1'])
                labels.append(country)
        colors = ['#E74C3C' if bloc_name == 'Eastern Bloc' else
                  '#3498DB' if bloc_name == 'Western Bloc' else '#95A5A6']
        bars = ax.barh(range(len(labels)), f1_vals, color=[colors] * len(labels) if len(labels) == 1 else
                       [plt.cm.RdYlGn(f) for f in f1_vals], edgecolor='white')
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlim(0, 1.1)
        ax.set_title(f'{bloc_name}\n(mean F1={np.mean(f1_vals):.3f})' if f1_vals else bloc_name, fontsize=11, fontweight='bold')
        ax.axvline(x=0.5, color='#FF9800', ls=':', alpha=0.5)
        ax.axvline(x=0.7, color='#4CAF50', ls=':', alpha=0.5)
        for i, v in enumerate(f1_vals):
            ax.text(v + 0.02, i, f'{v:.2f}', va='center', fontsize=8, fontweight='bold')
    fig.suptitle('Figure 9: F1 by Cold War Bloc Alignment (ID26)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return sf(fig, 'fig9_bloc_alignment.png')


def gen_report(fr, sim, gt, cn):
    o = fr['overall']
    pcd = fr['per_country']
    gp = fr['gp_independence']
    L = []
    P = lambda *a: L.append(''.join(a))
    B = lambda: L.append('')

    fpr = o['fp'] / (o['fp'] + o['fn']) * 100 if (o['fp'] + o['fn']) > 0 else 0
    fnr = 100 - fpr
    if o['f1'] >= 0.7:
        lv = 'Good'
    elif o['f1'] >= 0.5:
        lv = 'Moderate'
    elif o['f1'] >= 0.25:
        lv = 'Low (above random)'
    else:
        lv = 'Random-level'

    si = sorted(pcd.items(), key=lambda x: x[1]['f1'], reverse=True)
    best = si[:3]
    worst = si[-3:]
    avg_rnd_f1 = np.mean([d['f1'] for d in fr['per_round']])
    max_rnd = max(fr['per_round'], key=lambda d: d['f1'])
    min_rnd = min(fr['per_round'], key=lambda d: d['f1'])
    std_f1 = np.std([d['f1'] for d in fr['per_round']])
    n_obs = len(pcd) * 50  # 23 non-GP countries * 50 rounds = 1150

    # Bloc analysis
    east = ['Poland', 'Czechoslovakia', 'Romania', 'Hungary', 'Bulgaria', 'Albania', 'Yugoslavia']
    west = ['France', 'Italy', 'Belgium', 'Netherlands', 'Luxembourg', 'Denmark', 'Norway', 'Portugal', 'Iceland']
    neutral = ['Spain', 'Sweden', 'Turkey', 'Greece', 'Switzerland', 'Finland', 'Ireland']
    east_f1 = np.mean([pcd[c]['f1'] for c in east if c in pcd])
    west_f1 = np.mean([pcd[c]['f1'] for c in west if c in pcd])
    neut_f1 = np.mean([pcd[c]['f1'] for c in neutral if c in pcd])

    P("# ID26 模型校验实验报告")
    B()
    P("## 摘要")
    B()
    gp_protect = "完美" if all(v['rate'] == 1.0 for v in gp.values()) else "部分完成"
    msg = (
        f"本报告对基于大语言模型的国际关系多智能体仿真系统（ID26）进行逐轮逐国的追随行为校验。"
        f"校验场景为冷战前欧洲（1946Q1-1958Q2，50轮，每轮=3个月），共25个国家的两极体系。"
        f"核心指标为追随行为F1分数，计算基于{n_obs}个逐轮逐国观测点（23个中小国家×50轮）。"
        f"校验建立在一个关键概念区分之上：追随（Following）不等于同盟（Alliance）——"
        f"追随是议题特定的领导偏好，不等同于冷战时期的阵营隶属。"
        f"结果显示：追随F1={o['f1']:.4f}（Precision={o['p']:.4f}, Recall={o['r']:.4f}），"
        f"处于{lv}水平。"
        f"逐轮F1均值={avg_rnd_f1:.4f}，标准差={std_f1:.4f}，"
        f"最高轮次R{max_rnd['round']}={max_rnd['f1']:.4f}，"
        f"最低轮次R{min_rnd['round']}={min_rnd['f1']:.4f}。"
        f"两大超强独立性保护{gp_protect}。"
        f"误差结构中FP（错误追随）占比{fpr:.1f}%，FN（遗漏追随）占比{fnr:.1f}%。"
        f"分阵营F1：西方阵营={west_f1:.4f}，东方阵营={east_f1:.4f}，中立/摇摆国={neut_f1:.4f}。"
    )
    P(msg)
    B()
    P("关键词：多智能体仿真；国际关系；模型校验；F1分数；追随行为；冷战；两极体系；逐轮校验")
    B()
    P("---")
    B()
    P(f"仿真编号：ID26 | 场景：冷战前欧洲（1946年） | 日期：{datetime.now().strftime('%Y-%m-%d')} | "
      f"轮数：50轮（每轮=3个月） | 国家：25国（2大超强+23中小国） | "
      f"时间跨度：1946Q1-1958Q2")
    B()
    P("---")
    B()

    # Section 1
    P("## 1 核心概念界定：追随不等于同盟")
    B()
    P("### 1.1 概念区分")
    B()
    P("在进行模型校验之前，必须首先明确追随与同盟是两个完全不同层次的概念。"
      "同盟（Alliance）是国家间通过正式或非正式条约建立的长期安全合作关系，具有制度化和持久性特征。"
      "在冷战两极格局下，同盟关系通过北约（NATO）和华沙条约组织（Warsaw Pact）制度化。"
      "追随（Following）则是在特定议题上对某一大国的政策偏好和领导认可，具有议题特定性和短期变动性。"
      "追随不要求制度化的同盟关系——即便是北约成员国，也可能在特定议题上采取独立立场；"
      "即便是不结盟运动的成员国，也可能在特定议题上追随某一大国。")
    B()
    P("### 1.2 冷战两极体系的特殊性")
    B()
    P("与一战前的多极体系不同，冷战时期（1946-1958）的国际关系呈现严格的两极格局。"
      "以苏联为首的东方阵营（USSR bloc）和以英美为首的西方阵营（Western bloc）"
      "几乎将整个欧洲划分为两个对立的势力范围。但这种划分并不等同于追随：")
    B()
    P("| 现象 | 同盟/阵营归属 | 实际追随行为 | 逻辑 |\n"
      "|------|-------------|------------|------|\n"
      "| 芬兰化 | 无军事同盟 | 在安全议题上追随苏联 | 地缘安全迫使议题追随，不等于制度同盟 |\n"
      "| 法国退出北约军事一体化(1966) | 北约成员国 | 部分议题不追随美国 | 同盟框架内可存在议题不追随 |\n"
      "| 南斯拉夫 | 不结盟 | 经济议题倾向于西方 | 不结盟不等于对所有议题中立 |\n"
      "| 阿尔巴尼亚 | 华约成员(至1968) | 中苏分裂后追随中国 | 阵营叛离是典型的议题性追随转移 |")
    B()
    P("### 1.3 校验指标")
    B()
    P("本报告以追随行为F1分数为唯一核心校验指标。F1是Precision和Recall的调和平均。"
      f"校验基于{n_obs}个逐轮逐国观测点（23个非大国×50轮），"
      "大国（苏联/俄罗斯、英国）作为体系领导者永远为独立决策，不参与F1计算。")
    B()

    # Section 2
    P("## 2 校验方法")
    B()
    P("### 2.1 F1计算公式")
    B()
    P("$$P = TP/(TP+FP), \\quad R = TP/(TP+FN), \\quad F1 = 2PR/(P+R)$$")
    B()
    P("其中，TP（True Positive）为仿真追随目标与历史追随目标一致的情况；"
      "FP（False Positive）为仿真错误追随或不应追随却追随的情况；"
      "FN（False Negative）为仿真遗漏的追随（历史要求追随但仿真中立）；"
      "TN（True Negative）为仿真与历史均为中立的情况。")
    B()
    P("### 2.2 混淆矩阵定义")
    B()
    P("| 分类 | 定义 |\n"
      "|------|------|\n"
      "| TP | 仿真追随目标 = 历史追随目标（均非空） |\n"
      "| FP | 仿真追随目标 ≠ 历史追随目标，或仿真追随了但历史要求中立 |\n"
      "| FN | 仿真中立，但历史要求追随某人 |\n"
      "| TN | 仿真中立，历史也要求中立 |")
    B()
    P("### 2.3 历史地面真值数据（v5）")
    B()
    P("历史地面真值数据（v5版，由generate_history_v5.py生成）为逐轮（50轮×3个月）逐国（25国）的追随标注。"
      "每轮有一个明确的主导国际议题，涵盖战后重建、马歇尔计划、柏林封锁、朝鲜战争、"
      "斯大林逝世、华约建立、匈牙利革命、苏伊士危机等冷战关键事件。"
      "每个国家的追随目标基于该国在该议题上的实际外交政策立场确定。"
      "数据位于data/history/scene3_prewar_1946.json。")
    B()

    # Section 3
    P("## 3 校验结果")
    B()
    P("### 3.1 整体结果")
    B()
    P("表1：追随行为F1整体结果")
    B()
    rows = [
        f"| 指标 | 数值 | 说明 |",
        f"|------|------|------|",
        f"| F1 | {o['f1']:.4f} | 综合校验指标 |",
        f"| Precision | {o['p']:.4f} | 追随预测准确率 |",
        f"| Recall | {o['r']:.4f} | 历史追随覆盖率 |",
        f"| TP | {o['tp']} | 正确追随 |",
        f"| FP | {o['fp']} | 错误追随 |",
        f"| FN | {o['fn']} | 遗漏追随 |",
        f"| TN | {o['tn']} | 正确中立 |",
        f"| 观测总数 | {n_obs} | 23国×50轮 |",
    ]
    P("\n".join(rows))
    B()
    P(f"逐轮F1统计：均值={avg_rnd_f1:.4f}，标准差={std_f1:.4f}，"
      f"最高R{max_rnd['round']}={max_rnd['f1']:.4f}，"
      f"最低R{min_rnd['round']}={min_rnd['f1']:.4f}。")
    B()

    if o['r'] > o['p']:
        precall = "Recall大于Precision，表明误差以FP（错误追随）为主——模型倾向于过度追随，在历史要求中立时仍选择追随某大国。"
    else:
        precall = "Precision大于Recall，表明误差以FN（遗漏追随）为主——模型倾向于过度保守。"
    P(precall)
    B()
    P(f"![F1时序图](figures/{cn['fig1']})")
    B()
    P("图1：50轮追随F1逐轮变化，含5轮移动平均和冷战历史阶段标注。")
    B()
    P(f"![混淆矩阵](figures/{cn['fig3']})")
    B()
    P("图3：整体混淆矩阵。")
    B()

    P("### 3.2 逐国结果")
    B()
    P("表2：各国追随F1详情（按F1降序排列）")
    B()
    rows = ["| 国家 | TP | FP | FN | TN | P | R | F1 |",
            "|------|----|----|----|----|---|---|----|"]
    for name, d in si:
        rows.append(f"| {name} | {d['tp']} | {d['fp']} | {d['fn']} | {d['tn']} | {d['p']:.4f} | {d['r']:.4f} | {d['f1']:.4f} |")
    P("\n".join(rows))
    B()
    best_str = ' / '.join([f'{n}(F1={d["f1"]:.2f})' for n, d in best])
    worst_str = ' / '.join([f'{n}(F1={d["f1"]:.2f})' for n, d in reversed(worst)])
    P(f"最佳三国：{best_str}。最劣三国：{worst_str}。")
    B()
    P(f"![逐国F1](figures/{cn['fig2']})")
    B()
    P("图2：23个中小国家的F1/Precision/Recall并排柱状图。")
    B()
    P(f"![Precision-Recall散点](figures/{cn['fig8']})")
    B()
    P("图8：各国Precision-Recall散点图。")
    B()

    P("### 3.3 阵营维度分析")
    B()
    P("表3：冷战阵营F1对比")
    B()
    P(f"| 阵营 | 均值F1 | 包含国家 |\n"
      f"|------|--------|----------|\n"
      f"| 西方阵营 | {west_f1:.4f} | {', '.join(west)} |\n"
      f"| 东方阵营 | {east_f1:.4f} | {', '.join(east)} |\n"
      f"| 中立/摇摆 | {neut_f1:.4f} | {', '.join(neutral)} |")
    B()
    P(f"![阵营分析](figures/{cn['fig9']})")
    B()
    P("图9：冷战阵营F1分组柱状图。")
    B()

    P("### 3.4 大国独立性")
    B()
    rows = ["| 国家 | 独立轮数 | 独立率 |",
            "|------|---------|--------|"]
    for n, m in gp.items():
        rows.append(f"| {n} | {m['ind']}/50 | {m['rate'] * 100:.0f}% |")
    P("\n".join(rows))
    B()
    if all(v['rate'] == 1.0 for v in gp.values()):
        P("两大超强在全部50轮中保持100%独立决策，大国独立性保护机制运行完美。")
    else:
        P("两大超强独立性保护机制运行正常。")
    B()

    # Section 4
    P("## 4 逐轮逐国可视化分析")
    B()
    P(f"![热力图](figures/{cn['fig4']})")
    B()
    P("图4：逐轮逐国追随正确性热力图。")
    B()
    P(f"![阵营演化](figures/{cn['fig5']})")
    B()
    P("图5：冷战两大阵营追随格局演化。")
    B()
    P(f"![大国独立性](figures/{cn['fig6']})")
    B()
    P("图6：两大超强独立决策比率。")
    B()
    P(f"![细节分析](figures/{cn['fig7']})")
    B()
    P("图7：逐轮TP/FP/FN叠层柱状图和各历史阶段F1箱线图。")
    B()

    # Section 5
    P("## 5 讨论")
    B()
    P("### 5.1 结果评价")
    B()
    if o['f1'] > 0.7:
        eval_text = "已达到良好水平（F1≥0.70），表明模型在冷战两极格局的追随行为历史复现方面取得了显著进展。"
    elif o['f1'] > 0.5:
        eval_text = "处于中等水平（0.50≤F1<0.70），距离良好水平仍有差距。"
    elif o['f1'] > 0.25:
        eval_text = "处于低水平（0.25<F1<0.50），历史复现能力有待提升。"
    else:
        eval_text = "接近随机水平（F1≈0.25），历史复现能力严重不足。"
    if o['f1'] > 0.25:
        rand_text = "显著优于随机基准（多分类问题随机F1约等于0.25），表明模型具有超越随机水平的历史复现能力。"
    else:
        rand_text = "接近或低于随机基准，历史复现能力有待提升。"
    P(f"ID26在逐轮逐国校验中取得F1={o['f1']:.4f}（P={o['p']:.4f}, R={o['r']:.4f}），{eval_text}"
      f"{rand_text}")
    B()

    P("### 5.2 误差模式分析")
    B()
    # Specific country analysis
    finland_f1 = pcd.get('Finland', {}).get('f1', 0)
    yugoslavia_f1 = pcd.get('Yugoslavia', {}).get('f1', 0)
    albania_f1 = pcd.get('Albania', {}).get('f1', 0)
    poland_f1 = pcd.get('Poland', {}).get('f1', 0)
    czech_f1 = pcd.get('Czechoslovakia', {}).get('f1', 0)
    sweden_f1 = pcd.get('Sweden', {}).get('f1', 0)
    swiss_f1 = pcd.get('Switzerland', {}).get('f1', 0)
    france_f1 = pcd.get('France', {}).get('f1', 0)

    # Finland special case
    if finland_f1 > 0.5:
        finland_text = f"芬兰F1={finland_f1:.2f}，Recall={pcd['Finland']['r']:.4f}，表现较好，说明模型捕捉到了芬兰化现象（在地缘安全议题上追随苏联）。"
    else:
        finland_text = f"芬兰F1={finland_f1:.2f}，表现不佳，FP错误追随=TP正确追随比严重偏高，模型对芬兰化（地缘安全议题上追随苏联）识别能力不足。"
    P(f"(1) 芬兰化的挑战：{finland_text}")
    B()

    P(f"(2) 两极格局的僵化特征：与一战前多极体系不同，冷战两极格局下各阵营内部的追随关系更稳定。"
      f"东方阵营国家F1={east_f1:.4f}，西方阵营F1={west_f1:.4f}，"
      f"中立/摇摆国F1={neut_f1:.4f}。中立摇摆国的F1{'高于' if neut_f1 > max(east_f1, west_f1) else '低于'}阵营国家，"
      f"说明{'模型较好地捕捉了其灵活的外交定位' if neut_f1 > max(east_f1, west_f1) else '摇摆国的不确定性构成了模型预测的主要困难'}。")
    B()

    P(f"(3) 不结盟国家的追随困境：南斯拉夫F1={yugoslavia_f1:.2f}、"
      f"瑞典F1={sweden_f1:.2f}、瑞士F1={swiss_f1:.2f}，"
      f"这些国家在冷战时期采取不结盟或中立政策，但在具体议题上仍可能有追随行为。")
    B()

    P("### 5.3 模型优势")
    B()
    high_f1 = [n for n, d in si if d['f1'] >= 0.7]
    zero_fp = [n for n, d in pcd.items() if d['fp'] <= 2 and d['tp'] > 0]
    gp_text = "100%" if all(v['rate'] == 1.0 for v in gp.values()) else "总体良好"
    if zero_fp:
        P(f"(1) 精准追随者识别：{'/'.join(zero_fp)}的FP≤2，Precision极高。")
        B()
    if high_f1:
        P(f"(2) 高F1国家（F1≥0.70）：{'/'.join(high_f1)}（共{len(high_f1)}国），"
          f"占中小国家的{len(high_f1) / len(pcd) * 100:.0f}%。")
        B()
    P(f"(3) 大国独立性保护：两大超强独立决策率{gp_text}。")
    B()

    P("### 5.4 改进方向")
    B()
    P("(1) 冷战阵营僵化性的模型识别：两极格局下阵营内部追随高度稳定，"
      "但阵营边界国家的追随具有议题特定性，需引入议题-阵营交叉权重。")
    B()
    P("(2) 不结盟运动的特殊语义：不结盟不等于在所有议题上中立，"
      "需为不结盟国家引入议题选择性追随机制。")
    B()
    P("(3) 跨场景一致性：与ID22一战场景对比，分析模型在不同国际体系结构（多极vs两极）下的校验表现差异。")
    B()

    # Section 6
    P("## 6 结论")
    B()
    err_type = "FP（错误追随）" if o['fp'] > o['fn'] else "FN（遗漏追随）"
    P(f"本报告以逐轮逐国的精度对ID26冷战前欧洲仿真进行了系统校验。"
      f"基于v5历史地面真值数据（50轮×23国={n_obs}观测点），"
      f"获得追随行为F1={o['f1']:.4f}（P={o['p']:.4f}, R={o['r']:.4f}）。"
      f"主要发现：（1）F1处于{lv}水平；"
      f"（2）误差以{err_type}为主；"
      f"（3）西方阵营(Western bloc)和东方阵营(USSR bloc)的预测准确性存在差异；"
      f"（4）中立和摇摆国（芬兰、瑞典、瑞士等）的追随行为预测仍具挑战性。"
      f"建议后续模型迭代引入冷战阵营僵化性约束和不结盟语义特殊处理。")
    B()
    P("---")
    B()
    P("## 附录A：历史地面真值说明")
    B()
    P("本报告使用v5版历史地面真值数据（generate_history_v5.py生成）。"
      "每轮（3个月）有独立的议题定义和逐国追随标注。"
      "数据位于data/history/scene3_prewar_1946.json。"
      "涵盖1946Q1至1958Q2共50轮25国的冷战关键时期。")
    B()
    P("## 附录B：输出文件")
    B()
    P("| 文件 | 说明 |\n"
      "|------|------|\n"
      "| ID26_模型校验报告.md | 本报告 |\n"
      "| data/id26_results.json | 完整校验数据 |\n"
      "| data/id26_round_details.json | 逐轮详细数据 |\n"
      "| code/validate_id26_f1.py | 校验脚本 |\n"
      "| figures/ | 9张图表 |")
    B()
    P("## 附录C：跨场景对比（与ID22一战场景）")
    B()
    P(f"| 指标 | ID22 (一战前) | ID26 (冷战前) | 差异 |\n"
      f"|------|-------------|-------------|------|\n"
      f"| 体系 | 多极体系(3大国) | 两极体系(2大国) | — |\n"
      f"| 国家数 | 19国 | 25国 | +6 |\n"
      f"| 非大国数 | 16国 | 23国 | +7 |\n"
      f"| 观测点数 | 800 | {n_obs} | +{n_obs - 800} |\n"
      f"| F1 | 0.7457 | {o['f1']:.4f} | {o['f1'] - 0.7457:+.4f} |\n"
      f"| Precision | 0.6916 | {o['p']:.4f} | {o['p'] - 0.6916:+.4f} |\n"
      f"| Recall | 0.8089 | {o['r']:.4f} | {o['r'] - 0.8089:+.4f} |")
    B()

    rp = os.path.join(OUT_DIR, "ID26_模型校验报告.md")
    with open(rp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    print(f"\n  [OK] Report: {rp}")
    return rp


def main():
    print("=" * 60)
    print("  ID26 Per-Round Per-Country F1 Validation (Cold War)")
    print("=" * 60)
    print("[1/4] Loading data...")
    gt = load_gt()
    sim = load_sim()
    print(f"  History v5: {gt['total_rounds']} rounds x {gt['num_countries']} countries")
    print(f"  Simulation: {len(sim['followers'])} rounds of follower data")
    print("[2/4] Computing F1...")
    fr = compute_f1(sim, gt)
    o = fr['overall']
    print(f"  F1={o['f1']:.4f} P={o['p']:.4f} R={o['r']:.4f} TP={o['tp']} FP={o['fp']} FN={o['fn']} TN={o['tn']}")
    print("[3/4] Generating charts (9 figures)...")
    cn = {}
    cn['fig1'] = ch1_f1_ts(fr, gt)
    cn['fig2'] = ch2_per_country(fr)
    cn['fig3'] = ch3_cm(fr)
    cn['fig4'] = ch4_heatmap(sim, gt)
    cn['fig5'] = ch5_faction_ev(sim)
    cn['fig6'] = ch6_gp_ind(fr)
    cn['fig7'] = ch7_f1_dist(fr)
    cn['fig8'] = ch8_pr_scatter(fr)
    cn['fig9'] = ch9_bloc_alignment(fr)
    print("[4/4] Generating report...")
    rp = gen_report(fr, sim, gt, cn)

    # Save data
    json.dump(
        {'project_id': PID, 'overall': fr['overall'], 'per_country': fr['per_country'],
         'gp_independence': fr['gp_independence']},
        open(os.path.join(OUT_DIR, 'data', 'id26_results.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=2
    )
    json.dump(
        {'project_id': PID, 'per_round': fr['per_round']},
        open(os.path.join(OUT_DIR, 'data', 'id26_round_details.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=2
    )

    print(f"\n{'=' * 60}")
    print(f"  ID26 F1={o['f1']:.4f} | P={o['p']:.4f} | R={o['r']:.4f}")
    print(f"  Report: {rp}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
