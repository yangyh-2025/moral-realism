import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

conn = sqlite3.connect('../data/abm_simulation.db')
cursor = conn.cursor()

# 糊名到真实国家映射
mapping = {
    1: ('强国甲', '德国'),
    2: ('强国乙', '俄国'),
    3: ('强国丙', '英国'),
    4: ('中等国甲', '法国'),
    5: ('中等国乙', '奥匈帝国'),
    6: ('中等国丙', '意大利'),
    7: ('小国甲', '奥斯曼帝国'),
    8: ('小国乙', '保加利亚'),
    9: ('小国丙', '西班牙'),
    10: ('小国丁', '比利时'),
    11: ('小国戊', '希腊'),
    12: ('小国己', '瑞典'),
    13: ('小国庚', '荷兰'),
    14: ('小国辛', '罗马尼亚'),
    15: ('小国壬', '葡萄牙'),
    16: ('小国癸', '丹麦'),
    17: ('小国子', '瑞士'),
    18: ('小国丑', '塞尔维亚'),
    19: ('小国寅', '挪威'),
}

# ===== 图1: 国力演化对比图 =====
cursor.execute("""
    SELECT a.agent_id, a.agent_name, a.initial_total_power, h.round_end_power
    FROM agent_config a
    LEFT JOIN (
        SELECT agent_id, round_end_power FROM agent_power_history
        WHERE project_id = 1 AND round_num = (
            SELECT MAX(round_num) FROM agent_power_history WHERE project_id = 1
        )
    ) h ON a.agent_id = h.agent_id
    WHERE a.project_id = 1 ORDER BY a.initial_total_power DESC;
""")

fig, ax = plt.subplots(figsize=(16, 8))
labels = []
init_vals = []
final_vals = []
colors_init = []
colors_final = []
for row in cursor.fetchall():
    aid = row[0]
    alias = row[1]
    real = mapping[aid][1]
    labels.append(f"{alias}\n({real})")
    init_vals.append(row[2])
    final_vals.append(row[3] if row[3] else 0)
    # 为三大国用不同颜色
    if aid == 1:
        colors_init.append('#E74C3C')
        colors_final.append('#C0392B')
    elif aid == 2:
        colors_init.append('#3498DB')
        colors_final.append('#2980B9')
    elif aid == 3:
        colors_init.append('#2ECC71')
        colors_final.append('#27AE60')
    else:
        colors_init.append('#95A5A6')
        colors_final.append('#7F8C8D')

x = range(len(labels))
width = 0.35
ax.bar([i - width/2 for i in x], init_vals, width, label='初始CINC', color=colors_init, edgecolor='white')
ax.bar([i + width/2 for i in x], final_vals, width, label='最终CINC', color=colors_final, edgecolor='white')
ax.set_ylabel('CINC值', fontsize=12)
ax.set_title('图1：各国国力变化对比（初始 vs 最终，共50轮）', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
# 添加德国/俄国/英国标注
ax.annotate('霸权型', xy=(0 - width/2, init_vals[0]), xytext=(0, init_vals[0] + 0.05),
            fontsize=9, ha='center', color='#C0392B', fontweight='bold')
ax.annotate('强权型', xy=(1 - width/2, init_vals[1]), xytext=(1, init_vals[1] + 0.05),
            fontsize=9, ha='center', color='#2980B9', fontweight='bold')
ax.annotate('王道型', xy=(2 - width/2, init_vals[2]), xytext=(2, init_vals[2] + 0.05),
            fontsize=9, ha='center', color='#27AE60', fontweight='bold')
plt.tight_layout()
plt.savefig('chart1_power_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("图1已保存")

# ===== 图2: 全局行为分布饼图 =====
cursor.execute("""
    SELECT action_name, COUNT(*) as cnt FROM action_record
    WHERE project_id = 1 GROUP BY action_name ORDER BY cnt DESC;
""")
actions = cursor.fetchall()

action_names = []
action_counts = []
other_count = 0
for name, cnt in actions:
    if cnt >= 100:
        action_names.append(name)
        action_counts.append(cnt)
    else:
        other_count += cnt
if other_count > 0:
    action_names.append('其他(<100次)')
    action_counts.append(other_count)

fig, ax = plt.subplots(figsize=(10, 8))
colors = plt.cm.Set3(range(len(action_names)))
wedges, texts, autotexts = ax.pie(action_counts, labels=action_names, autopct='%1.1f%%',
                                   colors=colors, startangle=90, textprops={'fontsize': 11})
for autotext in autotexts:
    autotext.set_fontsize(9)
ax.set_title('图2：全局行为类别分布（总计7,982次）', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('chart2_action_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("图2已保存")

# ===== 图3: 主权尊重率与秩序类型时序图 =====
cursor.execute("""
    SELECT round_num, respect_sov_ratio * 100 as rs, order_type
    FROM simulation_round WHERE project_id = 1 ORDER BY round_num;
""")
rounds = cursor.fetchall()

fig, ax1 = plt.subplots(figsize=(16, 7))
round_nums = [r[0] for r in rounds]
rs_rates = [r[1] for r in rounds]
order_types = [r[2] for r in rounds]

# 绘制主权尊重率
ax1.fill_between(round_nums, rs_rates, alpha=0.2, color='green')
ax1.plot(round_nums, rs_rates, 'g-', linewidth=2, label='主权尊重率')
ax1.axhline(y=60, color='red', linestyle='--', alpha=0.7, label='阈值(60%)')
ax1.set_xlabel('仿真轮次', fontsize=12)
ax1.set_ylabel('主权尊重率 (%)', color='green', fontsize=12)
ax1.tick_params(axis='y', labelcolor='green')
ax1.set_ylim(0, 100)
ax1.set_xlim(0.5, 50.5)
ax1.legend(loc='upper right', fontsize=11)
ax1.grid(alpha=0.3)

# 在顶部添加秩序类型标注
colors_order = {'不干涉型': '#4CAF50', '规范接纳型': '#2196F3', '大棒威慑型': '#FF9800', '恐怖平衡型': '#F44336'}
from matplotlib.patches import Rectangle
legend_elements = []
for ot, color in colors_order.items():
    rounds_of_type = [r for r, o in zip(round_nums, order_types) if o == ot]
    if rounds_of_type:
        legend_elements.append(Rectangle((0,0),1,1, facecolor=color, label=f'{ot}({len(rounds_of_type)}轮)'))
ax1.legend(handles=legend_elements, loc='lower left', fontsize=10, title='秩序类型', framealpha=0.9)

# 在背景用颜色条表示秩序类型
for i, (rn, ot) in enumerate(zip(round_nums, order_types)):
    ax1.axvspan(rn - 0.5, rn + 0.5, ymin=0.88, ymax=1.0, color=colors_order.get(ot, 'gray'), alpha=0.6)

ax1.set_title('图3：主权尊重率与秩序类型时序演化（顶部色带=秩序类型）', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('chart3_sovereignty_order.png', dpi=150, bbox_inches='tight')
plt.close()
print("图3已保存")

# ===== 图4: 强国甲乙丙行为对比 =====
cursor.execute("""
    SELECT a.agent_name, ar.action_category, COUNT(*) as cnt
    FROM action_record ar
    JOIN agent_config a ON ar.source_agent_id = a.agent_id AND ar.project_id = a.project_id
    WHERE ar.project_id = 1 AND a.agent_id IN (1,2,3)
    GROUP BY a.agent_name, ar.action_category
    ORDER BY a.agent_id;
""")

categories = ['外交手段', '经济手段', '军事手段', '信息手段']
country_data = {
    '强国甲(德国)\n霸权型': {},
    '强国乙(俄国)\n强权型': {},
    '强国丙(英国)\n王道型': {}
}
for alias, cat, cnt in cursor.fetchall():
    real_map = {'强国甲': '强国甲(德国)\n霸权型', '强国乙': '强国乙(俄国)\n强权型', '强国丙': '强国丙(英国)\n王道型'}
    country_data[real_map[alias]][cat] = cnt

fig, ax = plt.subplots(figsize=(11, 7))
x = np.arange(len(categories))
width = 0.25
countries = list(country_data.keys())
bar_colors = ['#E74C3C', '#3498DB', '#2ECC71']
for i, country in enumerate(countries):
    vals = [country_data[country].get(c, 0) for c in categories]
    bars = ax.bar(x + (i-1)*width, vals, width, label=country, color=bar_colors[i], edgecolor='white')
    # 在柱子上添加数值
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val),
                ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('行为次数', fontsize=12)
ax.set_title('图4：强国甲乙丙行为类别对比（真实国家标注）', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=12)
ax.legend(fontsize=10, loc='upper right')
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, max([max(country_data[c].values()) for c in country_data]) * 1.15)
plt.tight_layout()
plt.savefig('chart4_major_powers_behavior.png', dpi=150, bbox_inches='tight')
plt.close()
print("图4已保存")

# ===== 图5: 德国vs俄国对抗强度时序 =====
cursor.execute("""
    SELECT round_num, source_agent_id, target_agent_id, action_name
    FROM action_record
    WHERE project_id = 1
      AND ((source_agent_id = 1 AND target_agent_id = 2) OR (source_agent_id = 2 AND target_agent_id = 1))
    ORDER BY round_num;
""")

round_data = {}
for rn, src, tgt, action in cursor.fetchall():
    key = (rn, f"{'德国→俄国' if src == 1 else '俄国→德国'}")
    if key not in round_data:
        round_data[key] = 0
    intensity = {'发表公开声明': 1, '表达合作意向': 1, '开展外交合作': 1,
                 '展示军事姿态': 2, '威胁': 3, '胁迫/强制': 4,
                 '交战/使用常规军事武力': 5, '攻击/袭击': 5}
    round_data[key] += intensity.get(action, 1)

rounds_list = list(range(1, 51))
directions = ['德国→俄国', '俄国→德国']
matrix = np.zeros((len(directions), len(rounds_list)))
for i, d in enumerate(directions):
    for j, r in enumerate(rounds_list):
        matrix[i, j] = round_data.get((r, d), 0)

fig, ax = plt.subplots(figsize=(18, 4))
im = ax.imshow(matrix, cmap='Reds', aspect='auto', vmin=0, vmax=10)
ax.set_xticks(range(0, 50, 5))
ax.set_xticklabels(range(1, 51, 5))
ax.set_yticks(range(len(directions)))
ax.set_yticklabels(directions, fontsize=11)
ax.set_xlabel('仿真轮次', fontsize=12)
ax.set_title('图5：德国 vs 俄国 对抗强度时序热力图（颜色越深=对抗越强）', fontsize=14, fontweight='bold')
cbar = plt.colorbar(im, ax=ax, label='对抗强度')
# 在强度>0的位置标注数值
for i in range(len(directions)):
    for j in range(len(rounds_list)):
        if matrix[i, j] > 0:
            ax.text(j, i, int(matrix[i, j]), ha='center', va='center',
                   color='white' if matrix[i, j] > 5 else 'black', fontsize=7)
plt.tight_layout()
plt.savefig('chart5_germany_russia_rivalry.png', dpi=150, bbox_inches='tight')
plt.close()
print("图5已保存")

# ===== 图6: 阵营追随格局演化 =====
fig, ax = plt.subplots(figsize=(16, 7))
# 读取follower数据
cursor.execute("""
    SELECT round_num, leader_agent_id, COUNT(*) as followers
    FROM follower_relation
    WHERE project_id = 1 AND leader_agent_id IS NOT NULL
    GROUP BY round_num, leader_agent_id
    ORDER BY round_num, leader_agent_id;
""")

# 构建追随者数时序
follower_ts = {1: {}, 2: {}, 3: {}, 4: {}}
for rn, lid, cnt in cursor.fetchall():
    if lid not in follower_ts:
        follower_ts[lid] = {}
    follower_ts[lid][rn] = cnt

# 读取所有轮次
all_rounds = list(range(1, 51))
leader_names = {1: '德国', 2: '俄国', 3: '英国', 4: '法国'}
leader_colors = {1: '#E74C3C', 2: '#3498DB', 3: '#2ECC71', 4: '#9B59B6'}

for lid in [3, 1, 2, 4]:
    y_vals = [follower_ts.get(lid, {}).get(r, 0) for r in all_rounds]
    ax.plot(all_rounds, y_vals, marker='o', markersize=3, linewidth=1.5,
            label=f'{leader_names.get(lid, f"ID{lid}")}', color=leader_colors.get(lid, 'gray'))

ax.set_xlabel('仿真轮次', fontsize=12)
ax.set_ylabel('追随者数量', fontsize=12)
ax.set_title('图6：阵营追随格局演化（谁是领导者？）', fontsize=14, fontweight='bold')
ax.set_xlim(0.5, 50.5)
ax.set_ylim(-0.5, 18)
ax.legend(fontsize=11, loc='upper right')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('chart6_follower_evolution.png', dpi=150, bbox_inches='tight')
plt.close()
print("图6已保存")

print("\n所有6张图表已生成完毕!")
