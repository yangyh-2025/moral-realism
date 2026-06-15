"""
Generate all figures for 5 docs in one pass.
Run: python generate_all_figures.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
import numpy as np
import os, json, sys

# Chinese font support
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 200
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = BASE

OUT_DIRS = {
    'simulation_design': os.path.join(DOCS, 'simulation_design', 'figures'),
    'technical_doc': os.path.join(DOCS, 'technical_doc', 'figures'),
    'prompt_design': os.path.join(DOCS, 'prompt_design', 'figures'),
    'program_design': os.path.join(DOCS, 'program_design', 'figures'),
    'scene_history': os.path.join(DOCS, 'scene_history', 'figures'),
}

for d in OUT_DIRS.values():
    os.makedirs(d, exist_ok=True)

COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'accent': '#e74c3c',
    'green': '#27ae60',
    'orange': '#f39c12',
    'purple': '#8e44ad',
    'teal': '#1abc9c',
    'pink': '#e84393',
    'gray': '#7f8c8d',
    'light_blue': '#85c1e9',
    'dark_red': '#c0392b',
}

# ============================================================
# 1. SIMULATION DESIGN FIGURES
# ============================================================
def make_simulation_design_figures():
    odir = OUT_DIRS['simulation_design']

    # --- Fig1: Simulation Flow Chart ---
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')

    boxes = [
        (5, 9.5, '创建轮次', '#3498db'),
        (5, 8.2, '主动决策\n(N个国家并发)', '#2ecc71'),
        (5, 6.8, '响应决策\n(N个国家并发)', '#2ecc71'),
        (5, 5.4, '国力更新\n(CINC全局重算)', '#f39c12'),
        (5, 4.0, '追随投票\n(N个国家并发)', '#e74c3c'),
        (5, 2.6, '秩序判定\n(双维度四象限)', '#9b59b6'),
        (2.5, 1.2, '目标评估\n(每10轮)', '#1abc9c'),
        (7.5, 1.2, '关系演化', '#1abc9c'),
    ]
    arrows = [
        (5, 9.0, 5, 8.7), (5, 7.7, 5, 7.3), (5, 6.3, 5, 5.9),
        (5, 4.9, 5, 4.5), (5, 3.5, 5, 3.1), (5, 2.1, 2.5, 1.7),
        (5, 2.1, 7.5, 1.7), (2.5, 1.7, 2.5, 0.2), (7.5, 1.7, 7.5, 0.2),
        (2.5, 0.2, 5, -0.2), (7.5, 0.2, 5, -0.2), (5, -0.2, 5, 9.5),
    ]

    for x, y, txt, color in boxes:
        rect = mpatches.FancyBboxPatch((x-2.2, y-0.4), 4.4, 0.8, boxstyle='round,pad=0.1',
                                        fc=color, ec='white', lw=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    for x1, y1, x2, y2 in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.5))

    # Next round label
    ax.text(5, -0.5, '下一轮 (N+1)', ha='center', va='center', fontsize=8,
            color='#7f8c8d', fontstyle='italic')

    ax.set_title('仿真单轮执行流程', fontsize=14, fontweight='bold', pad=15, color=COLORS['primary'])
    fig.savefig(os.path.join(odir, 'fig1_simulation_flow.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig2: Action Space Bar Chart ---
    actions = ['发表公开声明','呼吁/请求','表达合作意向','协商/磋商','开展外交合作','开展实质性合作',
               '提供援助','让步/屈服','调查','要求/索要','表达不满/不赞成','拒绝','威胁','抗议',
               '展示军事姿态','降级关系','胁迫/强制','攻击/袭击','交战/使用常规军事武力','实施非常规大规模暴力']
    categories = ['外交']*9 + ['经济']*2 + ['信息']*2 + ['外交'] + ['信息'] + ['外交'] + ['军事']*5
    initiator_vals = [0,0.1,0.05,0.08,0.1,0.1,0.02,-0.5,0,0,0,0.1,0.1,-0.4,0.1,-0.1,-0.1,-0.3,-0.3,-0.5]
    target_vals = [0,0,0.03,0.08,0.1,0.1,0.15,0.5,-0.1,-0.1,-0.1,-0.1,-0.2,-0.3,-0.3,-0.4,-0.6,-0.7,-0.9,-1.0]
    cat_colors = {'外交':'#3498db', '经济':'#2ecc71', '信息':'#f39c12', '军事':'#e74c3c'}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

    x = np.arange(len(actions))
    colors_bar = [cat_colors[c] for c in categories]
    ax1.bar(x, initiator_vals, color=colors_bar, edgecolor='white', linewidth=0.5)
    ax1.set_xticks(x); ax1.set_xticklabels(actions, rotation=45, ha='right', fontsize=7)
    ax1.set_ylabel('发起方国力变化值', fontsize=10)
    ax1.set_title('20项标准行为 - 发起方视角', fontsize=12, fontweight='bold')
    ax1.axhline(y=0, color='black', linewidth=0.5)

    ax2.bar(x, target_vals, color=colors_bar, edgecolor='white', linewidth=0.5)
    ax2.set_xticks(x); ax2.set_xticklabels(actions, rotation=45, ha='right', fontsize=7)
    ax2.set_ylabel('目标方国力变化值', fontsize=10)
    ax2.set_title('20项标准行为 - 目标方视角', fontsize=12, fontweight='bold')
    ax2.axhline(y=0, color='black', linewidth=0.5)

    patches = [mpatches.Patch(color=v, label=k) for k, v in cat_colors.items()]
    fig.legend(handles=patches, loc='upper center', ncol=4, fontsize=8)
    fig.suptitle('行为空间配置总览', fontsize=14, fontweight='bold', y=1.02)
    fig.savefig(os.path.join(odir, 'fig2_action_space.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig3: Leader Types Radar ---
    categories_radar = ['尊重主权\n偏好', '合作\n倾向', '军事\n倾向', '道义\n约束', '利益\n一致性', '行为\n可预测性']
    N = len(categories_radar)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    values = {
        '王道型': [0.9, 0.8, 0.1, 0.9, 0.7, 0.8],
        '霸权型': [0.5, 0.6, 0.4, 0.4, 0.9, 0.7],
        '强权型': [0.1, 0.2, 0.95, 0.05, 0.6, 0.5],
        '昏庸型': [0.3, 0.3, 0.3, 0.2, 0.1, 0.1],
    }
    colors_radar = {'王道型':'#2ecc71', '霸权型':'#3498db', '强权型':'#e74c3c', '昏庸型':'#95a5a6'}

    fig, axes = plt.subplots(2, 2, figsize=(12, 10), subplot_kw=dict(polar=True))
    for ax, (ltype, vals) in zip(axes.flatten(), values.items()):
        vals_plot = vals + vals[:1]
        ax.fill(angles, vals_plot, color=colors_radar[ltype], alpha=0.25)
        ax.plot(angles, vals_plot, color=colors_radar[ltype], linewidth=2, label=ltype)
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(categories_radar, fontsize=8)
        ax.set_ylim(0, 1); ax.set_title(ltype, fontsize=12, fontweight='bold', pad=15)

    fig.suptitle('四种领导类型行为偏好对比', fontsize=14, fontweight='bold')
    fig.savefig(os.path.join(odir, 'fig3_leader_types_radar.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig4: Three Scene Overview ---
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(1910, 1960); ax.set_ylim(0, 5); ax.axis('off')

    scenes = [
        ('场景一\n一战前后', 1913, 1925.5, '#3498db', '多极体系\n19国/50轮'),
        ('场景二\n二战前后', 1938, 1950.5, '#e74c3c', '多极→两极\n28国/50轮'),
        ('场景三\n冷战初期', 1946, 1958.5, '#2ecc71', '两极体系\n25国/50轮'),
    ]

    for label, x1, x2, color, desc in scenes:
        rect = mpatches.FancyBboxPatch((x1, 1.5), x2-x1, 2.5, boxstyle='round,pad=0.15',
                                        fc=color, ec='white', lw=2, alpha=0.7)
        ax.add_patch(rect)
        ax.text((x1+x2)/2, 3.2, label, ha='center', va='center', fontsize=11, color='white', fontweight='bold')
        ax.text((x1+x2)/2, 2.2, desc, ha='center', va='center', fontsize=8, color='white')

    # Timeline
    ax.plot([1910, 1960], [0.8, 0.8], 'k-', linewidth=2)
    for year in range(1910, 1965, 5):
        ax.plot([year, year], [0.6, 1.0], 'k-', linewidth=0.5)
        ax.text(year, 0.4, str(year), ha='center', fontsize=8)

    ax.set_title('模型校验三场景时间线', fontsize=14, fontweight='bold', pad=15, color=COLORS['primary'])
    fig.savefig(os.path.join(odir, 'fig4_three_scenes_timeline.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig5: CINC Calculation Diagram ---
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis('off')

    indicators = ['军事支出 milex', '军事人员 milper', '钢铁产量 irst', '能源消耗 pec', '总人口 tpop', '城市人口 upop']
    y_positions = [6, 5, 4, 3, 2, 1]

    for i, (ind, y) in enumerate(zip(indicators, y_positions)):
        rect = mpatches.FancyBboxPatch((1.5, y-0.35), 4.5, 0.7, boxstyle='round,pad=0.05',
                                        fc='#ecf0f1', ec='#bdc3c7', lw=1)
        ax.add_patch(rect)
        ax.text(3.75, y, ind, ha='center', va='center', fontsize=10)
        ax.annotate('', xy=(6.5, y), xytext=(6.0, y),
                     arrowprops=dict(arrowstyle='->', color=COLORS['secondary'], lw=1.5))

    # Average box
    rect = mpatches.FancyBboxPatch((6.5, 0.3), 4, 5.5, boxstyle='round,pad=0.15',
                                    fc=COLORS['secondary'], ec='white', lw=2, alpha=0.85)
    ax.add_patch(rect)
    ax.text(8.5, 3.5, 'CINC\n=\n1/6 × Σ(指标份额)', ha='center', va='center', fontsize=10,
            color='white', fontweight='bold')
    ax.text(8.5, 1.2, '体系内CINC\n之和恒为1', ha='center', va='center', fontsize=8, color='white')

    ax.set_title('CINC综合国力指数计算架构', fontsize=14, fontweight='bold', pad=15)
    fig.savefig(os.path.join(odir, 'fig5_cinc_calculation.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig6: Order Type Quadrants ---
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.axhline(y=60, color='#7f8c8d', linestyle='--', linewidth=1)
    ax.axvline(x=60, color='#7f8c8d', linestyle='--', linewidth=1)

    quadrants = [
        (80, 80, '规范接纳', '有公认领导者\n行为普遍尊重主权', '#2ecc71'),
        (80, 30, '大棒威慑', '存在领导者\n依赖强制维持秩序', '#e74c3c'),
        (30, 80, '不干涉', '无明确领导者\n各国行为自律', '#3498db'),
        (30, 30, '恐怖平衡', '无领导者\n行为失范', '#f39c12'),
    ]

    for x, y, title, desc, color in quadrants:
        rect = mpatches.FancyBboxPatch((x-20, y-20), 40, 40, boxstyle='round,pad=0.15',
                                        fc=color, ec='white', lw=2, alpha=0.6)
        ax.add_patch(rect)
        ax.text(x, y+8, title, ha='center', fontsize=12, fontweight='bold', color='white')
        ax.text(x, y-6, desc, ha='center', fontsize=8, color='white')

    ax.set_xlabel('主权尊重比率 (%)', fontsize=11)
    ax.set_ylabel('领导权比例 (%)', fontsize=11)
    ax.set_title('四象限国际秩序类型', fontsize=14, fontweight='bold', pad=15)

    # Annotations
    ax.annotate('高主权尊重', xy=(50, 95), ha='center', fontsize=9, color='#7f8c8d')
    ax.annotate('低主权尊重', xy=(50, 5), ha='center', fontsize=9, color='#7f8c8d')
    ax.annotate('无明确领导', xy=(10, 50), ha='center', fontsize=9, color='#7f8c8d', rotation=90)
    ax.annotate('有明确领导', xy=(90, 50), ha='center', fontsize=9, color='#7f8c8d', rotation=90)

    fig.savefig(os.path.join(odir, 'fig6_order_quadrants.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print('Simulation design figures done.')


# ============================================================
# 2. TECHNICAL DOC FIGURES
# ============================================================
def make_technical_doc_figures():
    odir = OUT_DIRS['technical_doc']

    # --- Fig1: System Architecture ---
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.axis('off')

    layers = [
        (1, 6.5, 12, 1, '前端层 (Vue 3 + Vite + Element Plus + ECharts)', '#3498db'),
        (1, 5, 12, 1, 'API 路由层 (FastAPI - app/api/)', '#2ecc71'),
        (1, 3.5, 12, 1, '业务服务层 (app/services/)', '#f39c12'),
        (1, 2, 12, 1, '核心引擎层 (app/core/ - 决策/国力/追随/秩序/战略)', '#e74c3c'),
        (1, 0.5, 12, 1, '数据持久层 (SQLAlchemy + SQLite)', '#9b59b6'),
    ]

    for x, y, w, h, label, color in layers:
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.1',
                                        fc=color, ec='white', lw=2, alpha=0.85)
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=10, color='white', fontweight='bold')

    # External services
    ax.text(13, 7, 'LLM API\n(OpenAI兼容)', ha='center', fontsize=8, color='#2c3e50')
    ax.annotate('', xy=(13, 6.8), xytext=(13, 6.1), arrowprops=dict(arrowstyle='<->', color='#7f8c8d', lw=1))
    ax.text(13, 5.8, 'COW NMC v6\n数据集', ha='center', fontsize=8, color='#2c3e50')

    ax.set_title('系统架构总览', fontsize=14, fontweight='bold', pad=15, color=COLORS['primary'])
    fig.savefig(os.path.join(odir, 'fig1_system_architecture.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig2: Core Module Interaction ---
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9); ax.axis('off')

    modules = {
        '决策引擎': (6, 7.5, '#e74c3c'),
        '国力更新\n(CINC重算)': (3, 5.5, '#f39c12'),
        '追随投票': (6, 5.5, '#3498db'),
        '秩序判定': (9, 5.5, '#2ecc71'),
        '战略关系\n演化': (3, 3.5, '#9b59b6'),
        '目标评估\n(每10轮)': (6, 3.5, '#1abc9c'),
        'LLM服务': (9, 3.5, '#e84393'),
        '校验引擎\n(3层)': (6, 1.5, '#7f8c8d'),
    }

    for name, (x, y, color) in modules.items():
        rect = mpatches.FancyBboxPatch((x-1.2, y-0.4), 2.4, 0.8, boxstyle='round,pad=0.1',
                                        fc=color, ec='white', lw=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x, y, name, ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    edges = [(6,7.1, 3,5.9), (6,7.1, 6,5.9), (6,7.1, 9,5.9), (3,5.1, 3,3.9), (6,5.1, 6,3.9),
             (9,5.1, 9,3.9), (6,3.1, 6,1.9)]
    for x1,y1,x2,y2 in edges:
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle='->', color='#95a5a6', lw=1))

    ax.set_title('核心模块数据流与依赖关系', fontsize=14, fontweight='bold', pad=15, color=COLORS['primary'])
    fig.savefig(os.path.join(odir, 'fig2_module_interaction.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig3: Verification Pipeline ---
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis('off')

    checks = [
        (2, 'Tier 1\n行为集校验', 'ID/名称匹配\n标准行为集', '#2ecc71'),
        (5, 'Tier 2\n基础校验', 'JSON结构\n必需字段/长度', '#f39c12'),
        (8, 'Tier 3\n前置条件校验', '高烈度行为\n关系/历史要求', '#e74c3c'),
    ]

    ax.annotate('', xy=(8.5, 4.5), xytext=(1.5, 4.5),
                 arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2))

    for x, title, desc, color in checks:
        circle = plt.Circle((x, 4.5), 0.7, color=color, ec='white', lw=2, alpha=0.9)
        ax.add_patch(circle)
        ax.text(x, 4.5, title, ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    ax.text(5, 2, '通过 → 写入DB', ha='center', fontsize=10, color='#2ecc71', fontweight='bold')
    ax.text(5, 1.2, '失败 → 重试提示词(最多3次)', ha='center', fontsize=9, color='#e74c3c')
    ax.text(5, 0.3, '三次失败后无重试写入(保留原始数据)', ha='center', fontsize=8, color='#7f8c8d')

    ax.set_title('决策结果三层校验流程', fontsize=14, fontweight='bold', pad=15)
    fig.savefig(os.path.join(odir, 'fig3_verification_pipeline.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print('Technical doc figures done.')


# ============================================================
# 3. PROMPT DESIGN FIGURES
# ============================================================
def make_prompt_design_figures():
    odir = OUT_DIRS['prompt_design']

    # --- Fig1: Prompt Architecture ---
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis('off')

    # System prompt
    sys_rect = mpatches.FancyBboxPatch((1, 5), 10, 2.5, boxstyle='round,pad=0.2',
                                       fc='#2c3e50', ec='white', lw=2, alpha=0.9)
    ax.add_patch(sys_rect)
    ax.text(6, 7, '系统提示词 (System Prompt)', fontsize=12, color='white', fontweight='bold', ha='center')
    sys_items = ['角色设定', 'CINC/实力层级说明', '核心规则约束(14条)', '领导类型规则', '输出格式要求']
    for i, item in enumerate(sys_items):
        ax.text(2 + i*2.2, 5.8, item, fontsize=8, color='#ecf0f1', ha='center')

    # User prompt
    user_rect = mpatches.FancyBboxPatch((1, 1.5), 10, 3, boxstyle='round,pad=0.2',
                                         fc='#3498db', ec='white', lw=2, alpha=0.9)
    ax.add_patch(user_rect)
    ax.text(6, 4, '用户提示词 (User Prompt)', fontsize=12, color='white', fontweight='bold', ha='center')
    user_items = ['任务描述', '当前态势摘要', '全量信息池', '允许行为列表', 'JSON输出模板']
    for i, item in enumerate(user_items):
        ax.text(2 + i*2.2, 2.5, item, fontsize=8, color='#ecf0f1', ha='center')

    ax.annotate('', xy=(6, 5), xytext=(6, 4.5), arrowprops=dict(arrowstyle='->', color='white', lw=3))
    ax.text(8.5, 4.7, '分层注入', fontsize=9, color='white', fontstyle='italic')

    ax.set_title('智能体提示词分层架构', fontsize=14, fontweight='bold', pad=15)
    fig.savefig(os.path.join(odir, 'fig1_prompt_architecture.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig2: Leader Type Follower Rules ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    rules = {
        '王道型': [
            ('候选领导者\n尊重主权率<60%', -30, '#e74c3c'),
            ('对本国有过\n援助/合作', +20, '#2ecc71'),
            ('对本国使用\n威胁/军事姿态', -40, '#e74c3c'),
        ],
        '霸权型': [
            ('有实质性\n利益输送', +30, '#2ecc71'),
            ('排名下降', -20, '#e74c3c'),
            ('曾背弃\n承诺', -25, '#e74c3c'),
        ],
        '强权型': [
            ('军事指标不\n显著强于本国', -50, '#e74c3c'),
            ('对主要威胁国\n有军事威慑', +20, '#2ecc71'),
            ('追随意愿\n本身很低', -30, '#e74c3c'),
        ],
        '昏庸型': [
            ('随机波动', 0, '#f39c12'),
            ('最近的\n赞扬', +20, '#2ecc71'),
            ('最近的\n批评', -20, '#e74c3c'),
        ],
    }
    colors_l = {'王道型':'#2ecc71','霸权型':'#3498db','强权型':'#e74c3c','昏庸型':'#95a5a6'}

    for ax, (ltype, lrules) in zip(axes.flatten(), rules.items()):
        names = [r[0] for r in lrules]
        vals = [r[1] for r in lrules]
        bar_colors = ['#e74c3c' if v < 0 else '#2ecc71' if v > 0 else '#f39c12' for v in vals]
        bars = ax.barh(names, vals, color=bar_colors, edgecolor='white')
        ax.axvline(x=0, color='black', linewidth=0.5)
        ax.set_xlim(-60, 40)
        ax.set_title(ltype, fontsize=12, fontweight='bold', color=colors_l[ltype])
        for bar, val in zip(bars, vals):
            ax.text(val + (1 if val >= 0 else -3), bar.get_y() + bar.get_height()/2,
                    f'{val:+d}%' if val != 0 else '±25%', va='center', fontsize=9)

    fig.suptitle('四种领导类型追随决策评估标准', fontsize=14, fontweight='bold')
    fig.savefig(os.path.join(odir, 'fig2_leader_follower_rules.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig3: Complete Simulation Lifecycle ---
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')

    steps = [
        (5, 9.3, '项目创建\n配置国家/CINC/领导类型', '#2c3e50'),
        (5, 7.8, '设置初始\n战略关系', '#34495e'),
        (5, 6.3, '轮次循环\n(主动→响应→国力→追随→秩序)', '#3498db'),
        (2.5, 4.5, '目标评估\n(每10轮触发)', '#1abc9c'),
        (7.5, 4.5, '关系演化\n(单轮≤1级)', '#9b59b6'),
        (5, 3, '下一轮', '#7f8c8d'),
        (5, 1.5, '仿真结束\n输出全景数据', '#2ecc71'),
    ]

    for i, (x, y, txt, color) in enumerate(steps):
        rect = mpatches.FancyBboxPatch((x-2.2, y-0.4), 4.4, 0.8, boxstyle='round,pad=0.1',
                                        fc=color, ec='white', lw=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    arrows = [(5,8.9,5,8.2),(5,7.4,5,6.7),(5,5.9,2.5,4.9),(5,5.9,7.5,4.9),
              (2.5,4.1,5,3.4),(7.5,4.1,5,3.4),(5,2.6,5,1.9)]
    for x1,y1,x2,y2 in arrows:
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.5))

    ax.set_title('完整仿真生命周期', fontsize=14, fontweight='bold', pad=15)
    fig.savefig(os.path.join(odir, 'fig3_simulation_lifecycle.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig4: Historical Data Tiered Strategy ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis('off')

    tiers = [
        (5, 4.2, 'Tier 3: 最近5条详细记录', '含完整 action_content\n单条级别', '#2ecc71'),
        (5, 2.8, 'Tier 2: 最近5轮详细聚合', '按关系对分组统计\n合作/对抗次数', '#f39c12'),
        (5, 1.3, 'Tier 1: 早期记录(>5轮)', '仅关系对级别极简统计\n合作次数/对抗次数', '#95a5a6'),
    ]

    for x, y, title, desc, color in tiers:
        rect = mpatches.FancyBboxPatch((2, y-0.5), 6, 1, boxstyle='round,pad=0.1',
                                        fc=color, ec='white', lw=2, alpha=0.85)
        ax.add_patch(rect)
        ax.text(2.3, y+0.15, title, fontsize=11, color='white', fontweight='bold')
        ax.text(7, y+0.15, desc, fontsize=8, color='white', va='top')

    ax.set_title('历史数据三级分层保留策略', fontsize=14, fontweight='bold', pad=15)
    fig.savefig(os.path.join(odir, 'fig4_history_tiers.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print('Prompt design figures done.')


# ============================================================
# 4. PROGRAM DESIGN FIGURES
# ============================================================
def make_program_design_figures():
    odir = OUT_DIRS['program_design']

    # --- Fig1: Module Architecture ---
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.axis('off')

    core_modules = [
        (1, '决策引擎\nDecisionEngine', '行为生成/成本收益分析', '#e74c3c'),
        (4, '提示词模板\nPromptTemplates', '系统/用户提示词构建', '#3498db'),
        (7, 'LLM服务\nLLMService', '并发模型调用', '#2ecc71'),
        (10, '仿真服务\nSimulationService', '轮次编排/流程控制', '#f39c12'),
        (13, '校验引擎\nValidator', '3层校验/重试机制', '#9b59b6'),
    ]

    modules2 = [
        (2.5, '国力更新\nCINCUpdater', '指标映射/全局重算', '#1abc9c'),
        (5.5, '追随决策\nFollowerVote', '被动追随/候选人评估', '#e84393'),
        (8.5, '秩序判定\nOrderEvaluator', '双维度四象限分类', '#27ae60'),
        (11.5, '关系演化\nRelEvolution', 'LLM驱动评估/约束', '#8e44ad'),
    ]

    for x, title, desc, color in core_modules:
        rect = mpatches.FancyBboxPatch((x-1.2, 6), 2.4, 1.5, boxstyle='round,pad=0.1',
                                        fc=color, ec='white', lw=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x, 7.2, title, ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        ax.text(x, 6.4, desc, ha='center', va='center', fontsize=7, color='white')

    for x, title, desc, color in modules2:
        rect = mpatches.FancyBboxPatch((x-1.2, 3.5), 2.4, 1.5, boxstyle='round,pad=0.1',
                                        fc=color, ec='white', lw=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x, 4.7, title, ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        ax.text(x, 3.9, desc, ha='center', va='center', fontsize=7, color='white')

    ax.set_title('核心仿真引擎模块架构', fontsize=14, fontweight='bold', pad=15, color=COLORS['primary'])
    fig.savefig(os.path.join(odir, 'fig1_module_architecture.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig2: Data Persistence ER Diagram ---
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis('off')

    entities = [
        (6, 7.3, 'Project\n仿真项目', '#2c3e50'),
        (1.5, 5.5, 'Agent\n智能体配置', '#3498db'),
        (4, 5.5, 'StrategicRel\n战略关系', '#2ecc71'),
        (8, 5.5, 'NeighborRel\n邻接关系', '#f39c12'),
        (10.5, 5.5, 'Round\n轮次记录', '#e74c3c'),
        (3, 3.5, 'ActionRecord\n行为记录', '#9b59b6'),
        (7, 3.5, 'CINCSnapshot\n国力快照', '#1abc9c'),
        (5, 1.5, 'FollowerRecord\n追随记录', '#e84393'),
        (9, 1.5, 'GoalEval\n目标评估', '#8e44ad'),
    ]

    for x, y, name, color in entities:
        rect = mpatches.FancyBboxPatch((x-1.2, y-0.3), 2.4, 0.8, boxstyle='round,pad=0.1',
                                        fc=color, ec='white', lw=2, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x, y+0.1, name, ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    ax.set_title('数据持久化实体关系概览', fontsize=14, fontweight='bold', pad=15, color=COLORS['primary'])
    fig.savefig(os.path.join(odir, 'fig2_data_er_diagram.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig3: Frontend Dashboard Layout ---
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    panels = [
        ('总览面板', '秩序类型时序\n关系网络图', '#2c3e50'),
        ('国力分析', 'CINC堆叠面积图\n数据查询表格', '#3498db'),
        ('行为分析', '饼图+频率表\n行为分布特征', '#2ecc71'),
        ('增长率', '按领导类型/实力\n分组统计', '#f39c12'),
        ('目标评估', 'KPI+趋势曲线\n达成度分析', '#e74c3c'),
        ('数据导出', '结构化导出\n外部软件分析', '#9b59b6'),
    ]

    for ax, (title, desc, color) in zip(axes.flatten(), panels):
        rect = mpatches.FancyBboxPatch((0.1, 0.1), 0.8, 0.8, boxstyle='round,pad=0.05',
                                        fc=color, ec='white', lw=2, alpha=0.85,
                                        transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.5, 0.65, title, transform=ax.transAxes, ha='center', fontsize=11,
                color='white', fontweight='bold')
        ax.text(0.5, 0.35, desc, transform=ax.transAxes, ha='center', fontsize=8,
                color='white')
        ax.axis('off')

    fig.suptitle('前端研究分析仪表板 - 六功能子模块', fontsize=14, fontweight='bold')
    fig.savefig(os.path.join(odir, 'fig3_frontend_dashboard.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig4: Concurrency Control ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis('off')

    # Semaphore illustration
    for i in range(5):
        rect = mpatches.FancyBboxPatch((0.5 + i*1.9, 3.5), 1.5, 0.5, boxstyle='round,pad=0.05',
                                        fc='#2ecc71', ec='white', lw=1, alpha=0.8)
        ax.add_patch(rect)
        ax.text(1.25 + i*1.9, 3.75, f'Worker {i+1}', ha='center', fontsize=7, color='white', fontweight='bold')

    for i in range(5, 10):
        rect = mpatches.FancyBboxPatch((0.5 + (i-5)*1.9, 2.5), 1.5, 0.5, boxstyle='round,pad=0.05',
                                        fc='#95a5a6', ec='white', lw=1, alpha=0.5)
        ax.add_patch(rect)
        ax.text(1.25 + (i-5)*1.9, 2.75, f'Waiting', ha='center', fontsize=7, color='white')

    ax.text(5, 4.5, '最大并发数 = 5 (可配置1-20)', ha='center', fontsize=11, fontweight='bold', color='#2c3e50')
    ax.text(5, 1.5, '信号量(Semaphore)并发控制 → 等待槽位释放后入队', ha='center', fontsize=9, color='#7f8c8d')

    ax.set_title('LLM调用并发控制机制', fontsize=14, fontweight='bold', pad=15, color=COLORS['primary'])
    fig.savefig(os.path.join(odir, 'fig4_concurrency_control.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print('Program design figures done.')


# ============================================================
# 5. SCENE HISTORY FIGURES
# ============================================================
def make_scene_history_figures():
    odir = OUT_DIRS['scene_history']

    # --- Fig1: Three Scenes Timeline with Events ---
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.set_xlim(1910, 1960)
    ax.set_ylim(0, 100)

    # Scene background bands
    ax.axvspan(1913, 1925.5, alpha=0.15, color='#3498db')
    ax.axvspan(1938, 1950.5, alpha=0.15, color='#e74c3c')
    ax.axvspan(1946, 1958.5, alpha=0.15, color='#2ecc71')

    ax.text(1919.25, 95, '场景一: 一战前后\n19国, 50轮', ha='center', fontsize=11, fontweight='bold', color='#2980b9')
    ax.text(1944.25, 85, '场景二: 二战前后\n28国, 50轮', ha='center', fontsize=11, fontweight='bold', color='#c0392b')
    ax.text(1952.25, 75, '场景三: 冷战初期\n25国, 50轮', ha='center', fontsize=11, fontweight='bold', color='#27ae60')

    # Key events — aligned with ground truth data round positions
    events = [
        # Scene 1 (1913-1925)
        (1913, 88, '伦敦会议', '#3498db'), (1914.5, 82, '一战爆发', '#e74c3c'),
        (1917.2, 76, '俄国二月\n革命', '#e74c3c'), (1917.3, 70, '美国\n参战', '#3498db'),
        (1917.8, 64, '俄国十月\n革命', '#e74c3c'), (1918.7, 58, '一战结束', '#2ecc71'),
        (1919.5, 52, '巴黎和会', '#3498db'), (1920, 46, '国联成立', '#2ecc71'),
        (1923, 40, '鲁尔危机', '#e74c3c'), (1925, 34, '洛迦诺', '#2ecc71'),
        # Scene 2 (1938-1947, data timeline compressed)
        (1938.2, 88, '德奥合并', '#e74c3c'), (1938.7, 82, '慕尼黑', '#e74c3c'),
        (1939.5, 76, '二战爆发', '#c0392b'), (1940.5, 70, '法国沦陷', '#e74c3c'),
        (1941.5, 64, '巴巴罗萨', '#c0392b'), (1943.2, 58, '意大利\n投降', '#2ecc71'),
        (1944, 52, '雅尔塔\n(数据)', '#3498db'), (1944.2, 46, '德国投降\n(数据)', '#2ecc71'),
        (1944.5, 40, '波茨坦\n(数据)', '#2ecc71'),
        (1945.5, 88, '铁幕演说\n(数据)', '#9b59b6'), (1945.8, 82, '杜鲁门主义\n(数据)', '#3498db'),
        (1946, 76, '捷克政变\n(数据)', '#e74c3c'), (1946.2, 70, '铁托分裂\n(数据)', '#8e44ad'),
        (1946.5, 64, '柏林封锁\n(数据)', '#c0392b'), (1947, 58, '北约成立\n(数据)', '#2ecc71'),
        (1947.2, 52, '苏联原子弹\n(数据)', '#e74c3c'),
        (1947.7, 46, '两个德国\n(数据)', '#9b59b6'),
        # Scene 3 (1946-1958)
        (1947, 88, '杜鲁门\n主义', '#3498db'), (1947.5, 82, '马歇尔\n计划', '#3498db'),
        (1948, 76, '捷克政变', '#e74c3c'), (1948.5, 70, '铁托分裂', '#8e44ad'),
        (1949, 64, '北约成立', '#2ecc71'), (1949.7, 58, '苏联原子弹', '#e74c3c'),
        (1950.5, 52, '朝鲜战争', '#c0392b'), (1953, 46, '斯大林去世', '#9b59b6'),
        (1955, 40, '华约成立', '#e74c3c'), (1956.8, 34, '匈牙利革命', '#8e44ad'),
        (1958, 28, '柏林危机', '#e74c3c'),
    ]

    for x, y, label, color in events:
        ax.plot(x, y, 'o', color=color, markersize=5)
        ax.annotate(label, (x, y), textcoords="offset points", xytext=(0, 6),
                    ha='center', fontsize=6, color=color, fontweight='bold')

    ax.set_ylim(30, 100)
    ax.set_xlabel('年份', fontsize=11)
    ax.set_title('三场景关键历史事件时间线', fontsize=14, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(os.path.join(odir, 'fig1_scene_timeline.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig2: Following Pattern Evolution per Scene ---
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))

    # Scene 1 data (simplified from historical rounds)
    rounds_s1 = list(range(1, 51))
    uk_follow_s1 = [12]*7 + [10,9,11,12,11,9,8,10,12,11,10,12,13,13,12,12,13,14,13,14,14,14,14,14]*2
    de_follow_s1 = [4]*7 + [5,3,3,3,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]*2
    ru_follow_s1 = [2]*7 + [2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]*2

    # Pad to 50
    uk_f1 = uk_follow_s1[:50] if len(uk_follow_s1) >= 50 else uk_follow_s1 + [14]*20
    de_f1 = de_follow_s1[:50] if len(de_follow_s1) >= 50 else de_follow_s1 + [0]*20
    ru_f1 = ru_follow_s1[:50] if len(ru_follow_s1) >= 50 else ru_follow_s1 + [0]*20

    uk_f1 = uk_f1[:50]; de_f1 = de_f1[:50]; ru_f1 = ru_f1[:50]

    for i, (ax, uk, de, ru, title, color_uk, color_de, color_ru) in enumerate([
        (axes[0], uk_f1, de_f1, ru_f1, '场景一: 一战前后 (1913-1925)', '#3498db', '#e74c3c', '#f39c12'),
    ]):
        ax.plot(rounds_s1, uk, color='#3498db', linewidth=2, label='追随英国')
        ax.plot(rounds_s1, de, color='#e74c3c', linewidth=2, label='追随德国')
        ax.plot(rounds_s1, ru, color='#f39c12', linewidth=2, label='追随俄国')
        ax.set_xlim(1, 50); ax.set_ylim(0, 16)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_ylabel('追随者数量'); ax.legend(fontsize=8, ncol=3)
        ax.axvspan(7, 24, alpha=0.08, color='#e74c3c')
        ax.text(15.5, 15, '战争期', ha='center', fontsize=8, color='#c0392b', fontstyle='italic')

    # Scene 2 (now 50 rounds)
    rounds_s2 = list(range(1, 51))
    uk_s2 = [18,18,17,17,16,15,9,11,10,8,8,6,8,6,5,7,7,7,6,6,6,7,7,7,4,4,5,5,6,6,6,5,5,6,6,6,5,5,6,6, 5,5,5,5,5,5,5,5,5,5]
    de_s2 = [2,2,3,3,4,4,3,3,2,2,3,3,2,4,4,2,1,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0]
    ru_s2 = [0,0,0,0,0,0,3,4,5,5,4,6,5,5,3,4,5,4,5,5,5,4,5,4,5,5,4,5,4,4,5,5,5,4,4,5,4,5,5,4, 5,4,5,4,4,4,4,5,4,4]

    ax = axes[1]
    ax.plot(rounds_s2, uk_s2, color='#3498db', linewidth=2, label='追随英国')
    ax.plot(rounds_s2, de_s2, color='#e74c3c', linewidth=2, label='追随德国')
    ax.plot(rounds_s2, ru_s2, color='#f39c12', linewidth=2, label='追随苏联')
    ax.set_xlim(1, 50); ax.set_ylim(0, 20)
    ax.set_title('场景二: 二战前后 (1938-1950)', fontsize=11, fontweight='bold')
    ax.set_ylabel('追随者数量'); ax.legend(fontsize=8, ncol=3)
    ax.axvspan(7, 26, alpha=0.08, color='#e74c3c')
    ax.text(16.5, 19, '战争期', ha='center', fontsize=8, color='#c0392b', fontstyle='italic')
    ax.axvline(x=28, color='#9b59b6', linestyle='--', linewidth=1)
    ax.text(28.5, 17, '铁幕', fontsize=7, color='#8e44ad')

    # Scene 3
    rounds_s3 = list(range(1, 51))
    uk_s3 = [14]*50
    ru_s3 = [8]*50
    # Adjustments for key events
    for i in range(10, 12):  # Tito split
        uk_s3[i-1] = 13
        ru_s3[i-1] = 7
    for i in range(34, 35):  # Tito-Stalin thaw
        ru_s3[i-1] = 8
    for i in range(39, 41):  # Yugoslav rapprochement
        uk_s3[i-1] = 13
        ru_s3[i-1] = 8

    ax = axes[2]
    ax.plot(rounds_s3, uk_s3, color='#3498db', linewidth=2, label='追随英国(西方)')
    ax.plot(rounds_s3, ru_s3, color='#f39c12', linewidth=2, label='追随苏联(东方)')
    ax.set_xlim(1, 50); ax.set_ylim(0, 16)
    ax.set_title('场景三: 冷战初期 (1946-1958)', fontsize=11, fontweight='bold')
    ax.set_ylabel('追随者数量'); ax.legend(fontsize=8, ncol=2)
    ax.set_xlabel('轮次')

    fig.suptitle('三场景追随格局演化对比', fontsize=14, fontweight='bold', y=1.02)
    fig.savefig(os.path.join(odir, 'fig2_following_evolution.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig3: Country Count Distribution ---
    fig, ax = plt.subplots(figsize=(10, 6))
    scenes = ['场景一\n一战前后\n(1913-1925)', '场景二\n二战前后\n(1938-1947)', '场景三\n冷战初期\n(1946-1958)']
    total = [19, 28, 25]
    great_powers = [3, 3, 2]
    major_powers = [3, 2, 2]
    small = [13, 23, 21]

    x = np.arange(len(scenes))
    width = 0.55
    bottom_small = np.array(small)
    bottom_major = bottom_small + np.array(major_powers)

    ax.bar(x, small, width, label='中小国家', color='#3498db', edgecolor='white')
    ax.bar(x, major_powers, width, bottom=small, label='次等列强', color='#f39c12', edgecolor='white')
    ax.bar(x, great_powers, width, bottom=bottom_major, label='体系大国', color='#e74c3c', edgecolor='white')

    for i, total_n in enumerate(total):
        ax.text(i, total_n + 0.5, f'{total_n}国', ha='center', fontsize=10, fontweight='bold')

    ax.set_xticks(x); ax.set_xticklabels(scenes, fontsize=9)
    ax.set_ylabel('国家数量', fontsize=11); ax.legend(fontsize=9)
    ax.set_title('三场景国家数量与层级分布', fontsize=14, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

    fig.savefig(os.path.join(odir, 'fig3_country_distribution.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # --- Fig4: System Structure Evolution ---
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis('off')

    systems = [
        (2, '多极均势', '6列强\n同盟→追随≠同盟\n中立空间存在\n低制度化', '#3498db'),
        (5, '多极→两极过渡', '3+2列强\n生存威胁驱动追随\n中立空间压缩\n战争→秩序重建', '#e74c3c'),
        (8, '稳定两极', '2大国\n意识形态+地缘锁定\n中立空间最小\n高制度化(北约/华约/EEC)', '#2ecc71'),
    ]

    for x, title, desc, color in systems:
        rect = mpatches.FancyBboxPatch((x-1.3, 1.5), 2.6, 3, boxstyle='round,pad=0.15',
                                        fc=color, ec='white', lw=2, alpha=0.8)
        ax.add_patch(rect)
        ax.text(x, 4, title, ha='center', fontsize=11, color='white', fontweight='bold')
        ax.text(x, 2.3, desc, ha='center', fontsize=8, color='white')

    # Arrows between
    ax.annotate('', xy=(3.3, 3), xytext=(3.7, 3), arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2))
    ax.annotate('', xy=(6.3, 3), xytext=(6.7, 3), arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2))

    ax.text(3.5, 2.2, '一战', ha='center', fontsize=8, color='#c0392b', fontweight='bold')
    ax.text(6.5, 2.2, '二战', ha='center', fontsize=8, color='#c0392b', fontweight='bold')

    ax.set_title('国际体系结构演化谱系', fontsize=14, fontweight='bold', pad=15, color=COLORS['primary'])
    fig.savefig(os.path.join(odir, 'fig4_system_evolution.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print('Scene history figures done.')


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print('Generating all figures...')
    make_simulation_design_figures()
    make_technical_doc_figures()
    make_prompt_design_figures()
    make_program_design_figures()
    make_scene_history_figures()
    print(f'\nAll figures generated successfully!')
    for name, path in OUT_DIRS.items():
        count = len([f for f in os.listdir(path) if f.endswith('.png')])
        print(f'  {name}: {count} figures')
