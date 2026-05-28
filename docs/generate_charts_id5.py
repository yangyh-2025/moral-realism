import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

conn = sqlite3.connect('../data/abm_simulation.db')
cursor = conn.cursor()

# ID5 agent mapping (project_id=5, agent_ids 92-110)
# Fixed: Agent 96 CINC=0.073 = Italy, Agent 97 CINC=0.052 = Austria-Hungary
mapping = {
    92: ('强国甲', '德国'),
    93: ('强国乙', '俄国'),
    94: ('强国丙', '英国'),
    95: ('中等国甲', '法国'),
    96: ('中等国丙', '意大利'),
    97: ('中等国乙', '奥匈帝国'),
    98: ('小国甲', '奥斯曼帝国'),
    99: ('小国乙', '保加利亚'),
    100: ('小国丙', '西班牙'),
    101: ('小国丁', '比利时'),
    102: ('小国戊', '希腊'),
    103: ('小国己', '瑞典'),
    104: ('小国庚', '荷兰'),
    105: ('小国辛', '罗马尼亚'),
    106: ('小国壬', '葡萄牙'),
    107: ('小国癸', '丹麦'),
    108: ('小国子', '瑞士'),
    109: ('小国丑', '塞尔维亚'),
    110: ('小国寅', '挪威'),
}

# ===== 图1: 国力演化对比图 =====
cursor.execute("""
    SELECT agent_id, round_start_power as init_power,
           (SELECT round_end_power FROM agent_power_history h2
            WHERE h2.project_id=5 AND h2.agent_id=aph.agent_id
            AND h2.round_num=(SELECT MAX(round_num) FROM agent_power_history WHERE project_id=5 AND agent_id=aph.agent_id)
           ) as final_power
    FROM agent_power_history aph
    WHERE project_id=5 AND round_num=1
    ORDER BY init_power DESC;
""")
rows = cursor.fetchall()

fig, ax = plt.subplots(figsize=(16, 8))
labels, init_vals, final_vals, colors_init, colors_final = [], [], [], [], []
for aid, init_p, final_p in rows:
    alias, real = mapping.get(aid, (f'ID{aid}', f'ID{aid}'))
    labels.append(f"{alias}\n({real})")
    init_vals.append(init_p)
    final_vals.append(final_p if final_p else 0)
    if aid == 92:
        colors_init.append('#E74C3C'); colors_final.append('#C0392B')
    elif aid == 93:
        colors_init.append('#3498DB'); colors_final.append('#2980B9')
    elif aid == 94:
        colors_init.append('#2ECC71'); colors_final.append('#27AE60')
    else:
        colors_init.append('#95A5A6'); colors_final.append('#7F8C8D')

x = range(len(labels))
width = 0.35
ax.bar([i - width/2 for i in x], init_vals, width, label='初始CINC', color=colors_init, edgecolor='white')
ax.bar([i + width/2 for i in x], final_vals, width, label='最终CINC', color=colors_final, edgecolor='white')
ax.set_ylabel('CINC值', fontsize=12)
ax.set_title('图1：各国国力变化对比（初始 vs 最终，共38轮）', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
ax.annotate('霸权型', xy=(0 - width/2, init_vals[0]), xytext=(0, init_vals[0] + 0.015),
            fontsize=9, ha='center', color='#C0392B', fontweight='bold')
ax.annotate('强权型', xy=(1 - width/2, init_vals[1]), xytext=(1, init_vals[1] + 0.015),
            fontsize=9, ha='center', color='#2980B9', fontweight='bold')
ax.annotate('王道型', xy=(2 - width/2, init_vals[2]), xytext=(2, init_vals[2] + 0.015),
            fontsize=9, ha='center', color='#27AE60', fontweight='bold')
plt.tight_layout()
plt.savefig('chart1_power_comparison_p5.png', dpi=150, bbox_inches='tight')
plt.close()
print("图1已保存")

# ===== 图2: 全局行为分布饼图 =====
cursor.execute("""
    SELECT action_name, COUNT(*) as cnt FROM action_record
    WHERE project_id=5 GROUP BY action_name ORDER BY cnt DESC;
""")
actions = cursor.fetchall()

action_names, action_counts, other_count = [], [], 0
for name, cnt in actions:
    if cnt >= 50:
        action_names.append(name)
        action_counts.append(cnt)
    else:
        other_count += cnt
if other_count > 0:
    action_names.append('其他(<50次)')
    action_counts.append(other_count)

fig, ax = plt.subplots(figsize=(10, 8))
colors = plt.cm.Set3(range(len(action_names)))
wedges, texts, autotexts = ax.pie(action_counts, labels=action_names, autopct='%1.1f%%',
                                   colors=colors, startangle=90, textprops={'fontsize': 11})
for at in autotexts:
    at.set_fontsize(9)
total = sum(action_counts)
ax.set_title(f'图2：全局行为类别分布（总计{total}次）', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('chart2_action_distribution_p5.png', dpi=150, bbox_inches='tight')
plt.close()
print("图2已保存")

# ===== 图3: 主权尊重率与秩序类型时序图 =====
cursor.execute("""
    SELECT round_num, respect_sov_ratio * 100 as rs, order_type
    FROM simulation_round WHERE project_id=5 ORDER BY round_num;
""")
rounds_data = cursor.fetchall()

fig, ax1 = plt.subplots(figsize=(16, 7))
round_nums = [r[0] for r in rounds_data]
rs_rates = [r[1] for r in rounds_data]
order_types = [r[2] for r in rounds_data]

ax1.fill_between(round_nums, rs_rates, alpha=0.2, color='green')
ax1.plot(round_nums, rs_rates, 'g-', linewidth=2, label='主权尊重率')
ax1.axhline(y=60, color='red', linestyle='--', alpha=0.7, label='阈值(60%)')
ax1.set_xlabel('仿真轮次', fontsize=12)
ax1.set_ylabel('主权尊重率 (%)', color='green', fontsize=12)
ax1.tick_params(axis='y', labelcolor='green')
ax1.set_ylim(0, 100)
ax1.set_xlim(0.5, max(round_nums) + 0.5)
ax1.grid(alpha=0.3)

from matplotlib.patches import Rectangle
colors_order = {'不干涉型': '#4CAF50', '规范接纳型': '#2196F3', '大棒威慑型': '#FF9800', '恐怖平衡型': '#F44336', '未判定': '#9E9E9E'}
legend_elements = []
for ot, color in colors_order.items():
    rounds_of_type = [r for r, o in zip(round_nums, order_types) if o == ot]
    if rounds_of_type:
        legend_elements.append(Rectangle((0,0),1,1, facecolor=color, label=f'{ot}({len(rounds_of_type)}轮)'))
ax1.legend(handles=legend_elements, loc='lower left', fontsize=10, title='秩序类型', framealpha=0.9)

for rn, ot in zip(round_nums, order_types):
    ax1.axvspan(rn - 0.5, rn + 0.5, ymin=0.88, ymax=1.0, color=colors_order.get(ot, 'gray'), alpha=0.6)

ax1.set_title('图3：主权尊重率与秩序类型时序演化（顶部色带=秩序类型）', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('chart3_sovereignty_order_p5.png', dpi=150, bbox_inches='tight')
plt.close()
print("图3已保存")

# ===== 图4: 强国甲乙丙行为类别对比 =====
cursor.execute("""
    SELECT source_agent_id, action_name, COUNT(*) as cnt
    FROM action_record
    WHERE project_id=5 AND source_agent_id IN (92, 93, 94)
    GROUP BY source_agent_id, action_name;
""")
raw = cursor.fetchall()

# Classify actions into categories
action_to_cat = {
    '发表公开声明': '外交手段', '呼吁/请求': '外交手段', '表达合作意向': '外交手段',
    '协商/磋商': '外交手段', '开展外交合作': '外交手段', '提供援助': '经济手段',
    '开展实质性合作': '经济手段', '降级关系': '外交手段', '表达不满/不赞成': '外交手段',
    '拒绝': '外交手段', '抗议': '外交手段',
    '威胁': '信息手段',
    '展示军事姿态': '军事手段', '胁迫/强制': '军事手段',
    '交战/使用常规军事武力': '军事手段', '攻击/袭击': '军事手段',
}

categories = ['外交手段', '经济手段', '军事手段', '信息手段']
country_data = {
    '强国甲(德国)\n霸权型': {},
    '强国乙(俄国)\n强权型': {},
    '强国丙(英国)\n王道型': {}
}
agent_to_label = {92: '强国甲(德国)\n霸权型', 93: '强国乙(俄国)\n强权型', 94: '强国丙(英国)\n王道型'}

for aid, action_name, cnt in raw:
    cat = action_to_cat.get(action_name, '其他')
    label = agent_to_label[aid]
    country_data[label][cat] = country_data[label].get(cat, 0) + cnt

fig, ax = plt.subplots(figsize=(11, 7))
x = np.arange(len(categories))
width = 0.25
bar_colors = ['#E74C3C', '#3498DB', '#2ECC71']
for i, (country, color) in enumerate(zip(country_data.keys(), bar_colors)):
    vals = [country_data[country].get(c, 0) for c in categories]
    bars = ax.bar(x + (i-1)*width, vals, width, label=country, color=color, edgecolor='white')
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val),
                ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('行为次数', fontsize=12)
ax.set_title('图4：强国甲乙丙行为类别对比（真实国家标注）', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=12)
ax.legend(fontsize=10, loc='upper right')
ax.grid(axis='y', alpha=0.3)
max_val = max(max(v.values()) for v in country_data.values())
ax.set_ylim(0, max_val * 1.15)
plt.tight_layout()
plt.savefig('chart4_major_powers_behavior_p5.png', dpi=150, bbox_inches='tight')
plt.close()
print("图4已保存")

# ===== 图5: 德国 vs 俄国 对抗强度时序热力图 =====
cursor.execute("""
    SELECT round_num, source_agent_id, target_agent_id, action_name
    FROM action_record
    WHERE project_id=5
      AND ((source_agent_id=92 AND target_agent_id=93) OR (source_agent_id=93 AND target_agent_id=92))
    ORDER BY round_num;
""")

round_data = {}
for rn, src, tgt, action in cursor.fetchall():
    key = (rn, '德国→俄国' if src == 92 else '俄国→德国')
    if key not in round_data:
        round_data[key] = 0
    intensity = {'发表公开声明': 1, '表达合作意向': 1, '开展外交合作': 1,
                 '展示军事姿态': 2, '威胁': 3, '胁迫/强制': 4,
                 '交战/使用常规军事武力': 5, '攻击/袭击': 5}
    round_data[key] += intensity.get(action, 1)

max_round = max(round_nums)
rounds_list = list(range(1, max_round + 1))
directions = ['德国→俄国', '俄国→德国']
matrix = np.zeros((len(directions), len(rounds_list)))
for i, d in enumerate(directions):
    for j, r in enumerate(rounds_list):
        matrix[i, j] = round_data.get((r, d), 0)

fig, ax = plt.subplots(figsize=(18, 4))
im = ax.imshow(matrix, cmap='Reds', aspect='auto', vmin=0, vmax=max(matrix.max(), 1))
step = 5
ax.set_xticks(range(0, len(rounds_list), step))
ax.set_xticklabels(range(1, max_round + 1, step))
ax.set_yticks(range(len(directions)))
ax.set_yticklabels(directions, fontsize=11)
ax.set_xlabel('仿真轮次', fontsize=12)
ax.set_title('图5：德国 vs 俄国 对抗强度时序热力图（颜色越深=对抗越强）', fontsize=14, fontweight='bold')
cbar = plt.colorbar(im, ax=ax, label='对抗强度')
for i in range(len(directions)):
    for j in range(len(rounds_list)):
        if matrix[i, j] > 0:
            ax.text(j, i, int(matrix[i, j]), ha='center', va='center',
                   color='white' if matrix[i, j] > 5 else 'black', fontsize=7)
plt.tight_layout()
plt.savefig('chart5_germany_russia_rivalry_p5.png', dpi=150, bbox_inches='tight')
plt.close()
print("图5已保存")

# ===== 图6: 阵营追随格局演化 =====
cursor.execute("""
    SELECT round_num, leader_agent_id, COUNT(*) as followers
    FROM follower_relation
    WHERE project_id=5 AND leader_agent_id IS NOT NULL
    GROUP BY round_num, leader_agent_id
    ORDER BY round_num, leader_agent_id;
""")

follower_ts = {}
for rn, lid, cnt in cursor.fetchall():
    if lid not in follower_ts:
        follower_ts[lid] = {}
    follower_ts[lid][rn] = cnt

fig, ax = plt.subplots(figsize=(16, 7))
all_rounds = list(range(1, max_round + 1))
leader_names = {92: '德国', 93: '俄国', 94: '英国'}
leader_colors = {92: '#E74C3C', 93: '#3498DB', 94: '#2ECC71'}

# Count neutrals per round
cursor.execute("""
    SELECT round_num, COUNT(*) as neutrals
    FROM follower_relation
    WHERE project_id=5 AND leader_agent_id IS NULL
    GROUP BY round_num ORDER BY round_num;
""")
neutral_ts = {r[0]: r[1] for r in cursor.fetchall()}

for lid in [94, 92, 93]:
    y_vals = [follower_ts.get(lid, {}).get(r, 0) for r in all_rounds]
    name = leader_names.get(lid, f'ID{lid}')
    color = leader_colors.get(lid, 'gray')
    ax.plot(all_rounds, y_vals, marker='o', markersize=3, linewidth=1.5,
            label=f'{name}', color=color)

# Add neutral line
neutral_vals = [neutral_ts.get(r, 0) for r in all_rounds]
ax.plot(all_rounds, neutral_vals, marker='s', markersize=2, linewidth=1, linestyle='--',
        label='中立', color='#95A5A6', alpha=0.7)

ax.set_xlabel('仿真轮次', fontsize=12)
ax.set_ylabel('追随者数量', fontsize=12)
ax.set_title('图6：阵营追随格局演化（谁是领导者？）', fontsize=14, fontweight='bold')
ax.set_xlim(0.5, max_round + 0.5)
ax.set_ylim(-0.5, 19)
ax.legend(fontsize=11, loc='upper right')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('chart6_follower_evolution_p5.png', dpi=150, bbox_inches='tight')
plt.close()
print("图6已保存")

# ===== 图7: 战略关系演化时序图（ID5新增） =====
import json

with open('../logs/5/relationship_changes.log', 'r', encoding='utf-8') as f:
    rel_changes = []
    for line in f:
        line = line.strip()
        if line:
            rel_changes.append(json.loads(line))

# Count relationship types per round
rel_by_round = {}
for rc in rel_changes:
    rn = rc['round_num']
    if rn not in rel_by_round:
        rel_by_round[rn] = {'war': 0, 'conflict': 0, 'partner': 0, 'alliance': 0, 'improve': 0, 'deteriorate': 0}
    new_type = rc['new_type']
    old_type = rc['current_type']
    if '战争' in new_type:
        rel_by_round[rn]['war'] += 1
    elif '冲突' in new_type:
        rel_by_round[rn]['conflict'] += 1
    elif '伙伴' in new_type:
        rel_by_round[rn]['partner'] += 1
    elif '盟友' in new_type:
        rel_by_round[rn]['alliance'] += 1
    # Track direction
    type_order = {'盟友关系': 4, '伙伴关系': 3, '无外交关系': 2, '冲突关系': 1, '战争关系': 0}
    if type_order.get(new_type, 2) < type_order.get(old_type, 2):
        rel_by_round[rn]['deteriorate'] += 1
    else:
        rel_by_round[rn]['improve'] += 1

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [2, 1]})

# Top: relationship type distribution
sorted_rounds = sorted(rel_by_round.keys())
war_counts = [rel_by_round[r]['war'] for r in sorted_rounds]
conflict_counts = [rel_by_round[r]['conflict'] for r in sorted_rounds]

ax1.bar(sorted_rounds, war_counts, label='升级为战争关系', color='#F44336', alpha=0.8)
ax1.bar(sorted_rounds, conflict_counts, bottom=war_counts, label='升级为冲突关系', color='#FF9800', alpha=0.8)
ax1.set_ylabel('关系变化数量', fontsize=12)
ax1.set_title('图7：战略关系演化——战争与冲突关系变化时序（ID5新增机制）', fontsize=14, fontweight='bold')
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3)

# Bottom: deterioration vs improvement
det_counts = [rel_by_round[r]['deteriorate'] for r in sorted_rounds]
imp_counts = [rel_by_round[r]['improve'] for r in sorted_rounds]
ax2.bar(sorted_rounds, det_counts, label='关系恶化', color='#E74C3C', alpha=0.7)
ax2.bar([-r for r in sorted_rounds], [0]*len(sorted_rounds))  # placeholder
ax2.bar(sorted_rounds, [-c for c in imp_counts], label='关系改善', color='#2ECC71', alpha=0.7)
ax2.set_xlabel('仿真轮次', fontsize=12)
ax2.set_ylabel('变化数量', fontsize=12)
ax2.legend(fontsize=11)
ax2.grid(axis='y', alpha=0.3)
ax2.axhline(y=0, color='black', linewidth=0.5)

plt.tight_layout()
plt.savefig('chart7_relationship_evolution_p5.png', dpi=150, bbox_inches='tight')
plt.close()
print("图7已保存")

conn.close()
print("\n所有7张图表已生成完毕!")
