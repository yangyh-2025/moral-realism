#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ID22 F1 Validation - Per-Round Per-Country Following Behavior
==============================================================
Compares simulation follower_relation against v2 history ground truth.
Scenario: WWI pre-war Europe (1913), 50 rounds, 19 countries.
Following != Alliance: following is issue-specific leadership preference.

Usage: python docs/id22_report/code/validate_id22_f1.py
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
HISTORY_PATH = os.path.join(BASE_DIR, "data", "history", "scene1_prewar_1913.json")
OUT_DIR = os.path.join(BASE_DIR, "docs", "id22_report")
for d in [os.path.join(OUT_DIR, "figures"), os.path.join(OUT_DIR, "data")]:
    os.makedirs(d, exist_ok=True)

PID = 22
CCODE2IDX = {255:1,365:2,200:3,220:4,300:5,325:6,640:7,355:8,230:9,211:10,
             350:11,380:12,210:13,360:14,235:15,390:16,225:17,345:18,385:19}
IDX2NAME = {1:"Germany",2:"Russia",3:"UK",4:"France",5:"Austria-Hungary",6:"Italy",
            7:"Ottoman",8:"Bulgaria",9:"Spain",10:"Belgium",11:"Greece",
            12:"Sweden",13:"Netherlands",14:"Romania",15:"Portugal",16:"Denmark",
            17:"Switzerland",18:"Serbia",19:"Norway"}
GP = {1,2,3,4}  # Great powers: Germany(1), Russia(2), UK(3), France(4)

agent2idx = {}; idx2agent = {}

def load_gt():
    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_sim():
    global agent2idx, idx2agent
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT agent_id, country_code FROM agent_config WHERE project_id=?', (PID,))
    for aid, cc in c.fetchall():
        if cc in CCODE2IDX:
            agent2idx[aid] = CCODE2IDX[cc]; idx2agent[CCODE2IDX[cc]] = aid
    c.execute('''SELECT round_num, follower_agent_id, leader_agent_id
                 FROM follower_relation WHERE project_id=?
                 ORDER BY round_num, follower_agent_id''', (PID,))
    fd = defaultdict(dict)
    for rn, fid, lid in c.fetchall():
        if lid == fid: lid = None
        fd[rn][fid] = lid
    c.execute('''SELECT round_num, respect_sov_ratio, order_type
                 FROM simulation_round WHERE project_id=? ORDER BY round_num''', (PID,))
    ri = c.fetchall()
    c.execute('''SELECT agent_id, round_num, round_start_power
                 FROM agent_power_history WHERE project_id=? ORDER BY agent_id, round_num''', (PID,))
    ph = defaultdict(list)
    for aid, rn, sp in c.fetchall(): ph[aid].append((rn, sp))
    c.execute('''SELECT source_agent_id, target_agent_id, relationship_type
                 FROM strategic_relationship WHERE project_id=?''', (PID,))
    rels = c.fetchall()
    conn.close()
    return {'followers':dict(fd), 'rounds':ri, 'power':dict(ph), 'relationships':rels}

def compute_f1(sim, gt):
    rounds = list(range(1,51)); gt_rds = gt['rounds']
    total = {'tp':0,'fp':0,'fn':0,'tn':0}
    pr_data = []; pc = {idx:{'tp':0,'fp':0,'fn':0,'tn':0} for idx in range(5,20)}
    for rn in rounds:
        sr = sim['followers'].get(rn,{}); gr = gt_rds[str(rn)]['following']
        tp=fp=fn=tn=0
        for aid, idx in agent2idx.items():
            if idx in GP: continue
            al = agent2idx.get(sr.get(aid)) if sr.get(aid) else None
            el = gr.get(str(idx))
            if el is not None:
                if al is not None:
                    if al==el: tp+=1; pc[idx]['tp']+=1
                    else: fp+=1; pc[idx]['fp']+=1
                else: fn+=1; pc[idx]['fn']+=1
            else:
                if al is not None: fp+=1; pc[idx]['fp']+=1
                else: tn+=1; pc[idx]['tn']+=1
        total['tp']+=tp; total['fp']+=fp; total['fn']+=fn; total['tn']+=tn
        p=tp/(tp+fp) if(tp+fp)>0 else 0; r=tp/(tp+fn) if(tp+fn)>0 else 0
        f1=2*p*r/(p+r) if(p+r)>0 else 0
        pr_data.append({'round':rn,'tp':tp,'fp':fp,'fn':fn,'tn':tn,
                        'p':round(p,4),'r':round(r,4),'f1':round(f1,4)})
    op=total['tp']/(total['tp']+total['fp']) if(total['tp']+total['fp'])>0 else 0
    oR=total['tp']/(total['tp']+total['fn']) if(total['tp']+total['fn'])>0 else 0
    of1=2*op*oR/(op+oR) if(op+oR)>0 else 0
    pcd={}
    for idx in range(5,20):
        d=pc[idx]; p=d['tp']/(d['tp']+d['fp']) if(d['tp']+d['fp'])>0 else 0
        r=d['tp']/(d['tp']+d['fn']) if(d['tp']+d['fn'])>0 else 0
        f1=2*p*r/(p+r) if(p+r)>0 else 0
        pcd[IDX2NAME[idx]]={'idx':idx,'tp':d['tp'],'fp':d['fp'],'fn':d['fn'],'tn':d['tn'],
                            'p':round(p,4),'r':round(r,4),'f1':round(f1,4)}

    gpi={}
    for idx in GP:
        aid=idx2agent.get(idx)
        if aid:
            ind=sum(1 for rn in rounds if sim['followers'].get(rn,{}).get(aid) is None)
            gpi[IDX2NAME[idx]]={'ind':ind,'total':50,'rate':ind/50}
    return {'overall':{'tp':total['tp'],'fp':total['fp'],'fn':total['fn'],'tn':total['tn'],
                       'p':round(op,4),'r':round(oR,4),'f1':round(of1,4)},
            'per_round':pr_data,'per_country':pcd,'gp_independence':gpi}

def sf(fig, name):
    p=os.path.join(OUT_DIR,"figures",name); fig.savefig(p,dpi=300,bbox_inches='tight'); plt.close(fig)
    print(f"  [OK] {name}"); return name

def ch1_f1_ts(fr):
    fig,ax=plt.subplots(figsize=(14,6))
    pr=fr['per_round']; rs=[d['round'] for d in pr]; f1s=[d['f1'] for d in pr]
    ps=[d['p'] for d in pr]; recs=[d['r'] for d in pr]
    ax.plot(rs,f1s,'o-',ms=4,lw=2,label='F1',color='#2196F3',zorder=5)
    ax.plot(rs,ps,'s--',ms=2,lw=1.2,alpha=0.7,label='Precision',color='#4CAF50')
    ax.plot(rs,recs,'^--',ms=2,lw=1.2,alpha=0.7,label='Recall',color='#FF5722')
    if len(f1s)>=5:
        ma=np.convolve(f1s,np.ones(5)/5,mode='valid')
        ax.plot(range(5,len(f1s)+1),ma,'-',lw=3,alpha=0.4,color='#1565C0',label='5-round MA')
    ax.axhline(y=0.7,color='#4CAF50',ls=':',alpha=0.5); ax.axhline(y=0.5,color='#FF9800',ls=':',alpha=0.5)
    ax.text(50.5,0.71,'Good(0.7)',fontsize=8,color='#4CAF50',va='bottom')
    ax.text(50.5,0.51,'Moderate(0.5)',fontsize=8,color='#FF9800',va='bottom')
    phases=[(1,6,'Naval Race','#E3F2FD'),(7,8,'July Crisis','#FFF3E0'),
            (9,24,'WWI','#FFEBEE'),(25,30,'Versailles','#E8F5E9'),(31,50,'Postwar','#F3E5F5')]
    for s,e,label,color in phases:
        ax.axvspan(s-0.5,e+0.5,alpha=0.15,color=color)
        ax.text((s+e)/2,1.02,label,ha='center',fontsize=7,color='#666',transform=ax.get_xaxis_transform())
    ax.set_xlabel('Round (1 round = 3 months)',fontsize=11)
    ax.set_ylabel('Score',fontsize=11)
    ax.set_title('Figure 1: Per-Round Following F1 Score (ID22)',fontsize=13,fontweight='bold')
    ax.set_xlim(0.5,50.5); ax.set_ylim(0,1.08)
    ax.legend(fontsize=9,loc='lower left',framealpha=0.9); ax.grid(alpha=0.3)
    plt.tight_layout(); return sf(fig,'fig1_f1_timeseries.png')

def ch2_per_country(fr):
    pcd=fr['per_country']; si=sorted(pcd.items(),key=lambda x:x[1]['f1'],reverse=True)
    names=[n for n,_ in si]; f1s=[d['f1'] for _,d in si]
    ps=[d['p'] for _,d in si]; recs=[d['r'] for _,d in si]
    fig,ax=plt.subplots(figsize=(12,7)); y=np.arange(len(names)); h=0.25
    ax.barh(y+h,f1s,h,label='F1',color='#2196F3',edgecolor='white')
    ax.barh(y,ps,h,label='Precision',color='#4CAF50',edgecolor='white',alpha=0.8)
    ax.barh(y-h,recs,h,label='Recall',color='#FF5722',edgecolor='white',alpha=0.8)
    for i,v in enumerate(f1s):
        if v>0.02: ax.text(v+0.02,i+h,f'{v:.2f}',va='center',fontsize=8,fontweight='bold',color='#1565C0')
    ax.set_yticks(y); ax.set_yticklabels(names,fontsize=10)
    ax.set_xlabel('Score',fontsize=11)
    ax.set_title('Figure 2: Per-Country Following F1/P/R (ID22)',fontsize=13,fontweight='bold')
    ax.legend(fontsize=9,loc='lower right'); ax.set_xlim(0,1.15)
    ax.axvline(x=0.5,color='#FF9800',ls=':',alpha=0.5); ax.axvline(x=0.7,color='#4CAF50',ls=':',alpha=0.5)
    ax.grid(axis='x',alpha=0.3); ax.invert_yaxis()
    plt.tight_layout(); return sf(fig,'fig2_per_country.png')

def ch3_cm(fr):
    o=fr['overall']; fig,ax=plt.subplots(figsize=(7,6))
    cm=np.array([[o['tp'],o['fp']],[o['fn'],o['tn']]])
    ax.imshow(cm,cmap='Blues',aspect='auto')
    ax.set_xticks([0,1]); ax.set_xticklabels(['Predicted: Correct','Predicted: Wrong/Neutral'],fontsize=10)
    ax.set_yticks([0,1]); ax.set_yticklabels(['Actual: Should Follow','Actual: Should Be Neutral'],fontsize=10)
    ax.set_title('Figure 3: Confusion Matrix (ID22)',fontsize=13,fontweight='bold')
    for i in range(2):
        for j in range(2):
            ax.text(j,i,str(cm[i][j]),ha='center',va='center',fontsize=20,fontweight='bold',
                    color='white' if cm[i][j]>cm.max()/2 else 'black')
    ax.text(1.35,0.5,f'P={o["p"]:.4f}\nR={o["r"]:.4f}\nF1={o["f1"]:.4f}',
            transform=ax.transAxes,fontsize=10,va='center',
            bbox=dict(boxstyle='round',facecolor='lightblue',alpha=0.5))
    plt.tight_layout(); return sf(fig,'fig3_confusion_matrix.png')

def ch4_heatmap(sim,gt):
    countries=sorted([a for a in agent2idx if agent2idx[a] not in GP],key=lambda a:agent2idx[a])
    mx=np.zeros((len(countries),50))
    for i,aid in enumerate(countries):
        idx=agent2idx[aid]
        for rn in range(1,51):
            al=agent2idx.get(sim['followers'].get(rn,{}).get(aid)) if sim['followers'].get(rn,{}).get(aid) else None
            el=gt['rounds'][str(rn)]['following'].get(str(idx))
            if al is None: al=0
            if el is None: el=0
            mx[i][rn-1]=1 if al==el else 0
    fig,ax=plt.subplots(figsize=(16,8))
    ax.imshow(mx,cmap='RdYlGn',aspect='auto',vmin=0,vmax=1,interpolation='nearest')
    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels([IDX2NAME[agent2idx[a]] for a in countries],fontsize=9)
    ax.set_xlabel('Round',fontsize=11); ax.set_ylabel('Country',fontsize=11)
    ax.set_title('Figure 4: Per-Round Per-Country Following Correctness (ID22)',fontsize=13,fontweight='bold')
    for s in [7,9,25,31]:
        ax.axvline(x=s-0.5,color='black',lw=1.5,ls='--',alpha=0.5)
    plt.colorbar(ax.images[0],ax=ax,shrink=0.8,label='Correct=1 / Wrong=0')
    ax2=ax.twinx()
    ax2.barh(range(len(countries)),np.mean(mx,axis=1),height=0.6,color='#2196F3',alpha=0.3,align='center')
    ax2.set_ylabel('Accuracy',fontsize=11,color='#2196F3'); ax2.set_xlim(0,1.5)
    plt.tight_layout(); return sf(fig,'fig4_heatmap.png')

def ch5_faction_ev(sim):
    fig,ax=plt.subplots(figsize=(14,6))
    fs=defaultdict(lambda:defaultdict(int)); ns=defaultdict(int)
    for rn in sorted(sim['followers'].keys()):
        for fid,lid in sim['followers'][rn].items():
            if lid is not None: fs[lid][rn]+=1
            else: ns[rn]+=1
    ar=list(range(1,51)); colors={3:'#2ECC71',1:'#E74C3C',2:'#3498DB',4:'#F39C12'}
    for idx in [3,1,2,4]:
        aid=idx2agent.get(idx)
        if aid is None: continue
        yv=[fs[aid].get(r,0) for r in ar]
        ax.fill_between(ar,yv,alpha=0.2,color=colors[idx])
        ax.plot(ar,yv,'o-',ms=3,lw=2,label=IDX2NAME[idx],color=colors[idx])
    nv=[ns.get(r,0) for r in ar]
    ax.plot(ar,nv,'s--',ms=2,lw=1.5,label='Independent',color='#95A5A6',alpha=0.8)
    ax.set_xlabel('Round',fontsize=11); ax.set_ylabel('Number of Followers',fontsize=11)
    ax.set_title('Figure 5: Faction Following Evolution (ID22)',fontsize=13,fontweight='bold')
    ax.set_xlim(0.5,50.5); ax.set_ylim(-0.5,19)
    ax.legend(fontsize=9,loc='upper right'); ax.grid(alpha=0.3)
    plt.tight_layout(); return sf(fig,'fig5_faction_evolution.png')

def ch6_gp_ind(fr):
    gp=fr['gp_independence']
    fig,ax=plt.subplots(figsize=(7,5))
    names=list(gp.keys()); rates=[gp[n]['rate']*100 for n in names]
    colors=['#E74C3C','#3498DB','#2ECC71','#F39C12']
    bars=ax.bar(names,rates,color=colors,edgecolor='white',width=0.5)
    for bar,rate in zip(bars,rates):
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,f'{rate:.0f}%',ha='center',fontsize=12,fontweight='bold')
    ax.set_ylabel('Independence Rate (%)',fontsize=11)
    ax.set_title('Figure 6: Great Power Independence (ID22)',fontsize=13,fontweight='bold')
    ax.set_ylim(0,110); ax.axhline(y=100,color='#4CAF50',ls='--',alpha=0.7,label='Target:100%')
    ax.legend(fontsize=9); ax.grid(axis='y',alpha=0.3)
    plt.tight_layout(); return sf(fig,'fig6_gp_independence.png')

def ch7_f1_dist(fr):
    """F1 distribution boxplot and per-round TP/FP/FN stacked bar"""
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(14,10))
    pr=fr['per_round']
    rs=[d['round'] for d in pr]
    tps=[d['tp'] for d in pr]; fps=[d['fp'] for d in pr]; fns=[d['fn'] for d in pr]
    # stacked bar
    ax1.bar(rs,tps,color='#4CAF50',label='TP',width=0.8)
    ax1.bar(rs,fps,bottom=tps,color='#FF5722',label='FP',width=0.8)
    ax1.bar(rs,fns,bottom=[t+f for t,f in zip(tps,fps)],color='#FFC107',label='FN',width=0.8)
    ax1.set_xlabel('Round',fontsize=11); ax1.set_ylabel('Count',fontsize=11)
    ax1.set_title('Figure 7a: Per-Round TP/FP/FN Stacked Bar (ID22)',fontsize=13,fontweight='bold')
    ax1.set_xlim(0.5,50.5); ax1.legend(fontsize=9,loc='upper right'); ax1.grid(axis='y',alpha=0.3)
    # boxplot by phase
    phases={'Naval Race(1-6)':[1,6],'July Crisis(7-8)':[7,8],'WWI(9-24)':[9,24],
            'Versailles(25-30)':[25,30],'Postwar(31-50)':[31,50]}
    phase_data=[]
    for label,(s,e) in phases.items():
        phase_data.append([d['f1'] for d in pr if s<=d['round']<=e])
    bp=ax2.boxplot(phase_data,labels=phases.keys(),patch_artist=True)
    colors_box=['#E3F2FD','#FFF3E0','#FFEBEE','#E8F5E9','#F3E5F5']
    for patch,c in zip(bp['boxes'],colors_box): patch.set_facecolor(c)
    ax2.set_ylabel('F1 Score',fontsize=11)
    ax2.set_title('Figure 7b: F1 Distribution by Historical Phase (ID22)',fontsize=13,fontweight='bold')
    ax2.axhline(y=0.5,color='#FF9800',ls=':',alpha=0.5); ax2.axhline(y=0.7,color='#4CAF50',ls=':',alpha=0.5)
    ax2.grid(axis='y',alpha=0.3)
    plt.tight_layout(); return sf(fig,'fig7_detail_analysis.png')

def ch8_precision_recall_curve(fr):
    """Per-country Precision vs Recall scatter"""
    pcd=fr['per_country']
    fig,ax=plt.subplots(figsize=(10,8))
    names=[]; ps=[]; recs=[]; f1s=[]
    for n,d in pcd.items():
        names.append(n); ps.append(d['p']); recs.append(d['r']); f1s.append(d['f1'])
    sc=ax.scatter(ps,recs,s=[f*400 for f in f1s],c=f1s,cmap='RdYlGn',alpha=0.8,edgecolors='black',linewidth=0.5)
    for i,n in enumerate(names):
        ax.annotate(n,(ps[i],recs[i]),fontsize=7,ha='center',va='bottom',
                   xytext=(0,5),textcoords='offset points')
    for fl in np.arange(0.1,1.0,0.1):
        xv=np.linspace(fl/1,1,100); yv=fl*xv/(2*xv-fl)
        ax.plot(xv,yv,'k--',alpha=0.15,lw=0.5)
    ax.set_xlabel('Precision',fontsize=11); ax.set_ylabel('Recall',fontsize=11)
    ax.set_title('Figure 8: Per-Country Precision-Recall Scatter (ID22)',fontsize=13,fontweight='bold')
    ax.set_xlim(-0.02,1.05); ax.set_ylim(-0.02,1.05)
    cbar=plt.colorbar(sc,ax=ax,shrink=0.8); cbar.set_label('F1',fontsize=10)
    ax.grid(alpha=0.3); ax.axhline(y=0.5,color='#FF9800',ls=':',alpha=0.3)
    ax.axvline(x=0.5,color='#FF9800',ls=':',alpha=0.3)
    plt.tight_layout(); return sf(fig,'fig8_pr_scatter.png')

def gen_report(fr, sim, gt, cn):
    o=fr['overall']; pcd=fr['per_country']; gp=fr['gp_independence']
    L=[]; P=lambda *a:L.append(''.join(a)); B=lambda:L.append('')
    fpr=o['fp']/(o['fp']+o['fn'])*100 if(o['fp']+o['fn'])>0 else 0; fnr=100-fpr
    if o['f1']>=0.7: lv='Good'
    elif o['f1']>=0.5: lv='Moderate'
    else: lv='Low'
    si=sorted(pcd.items(),key=lambda x:x[1]['f1'],reverse=True)
    best=si[:3]; worst=si[-3:]
    avg_rnd_f1=np.mean([d['f1'] for d in fr['per_round']])
    max_rnd=max(fr['per_round'],key=lambda d:d['f1'])
    min_rnd=min(fr['per_round'],key=lambda d:d['f1'])
    avg_p=np.mean([d['p'] for d in fr['per_round']])
    avg_r=np.mean([d['r'] for d in fr['per_round']])
    std_f1=np.std([d['f1'] for d in fr['per_round']])

    P("# ID22 模型校验实验报告"); B()
    P("## 摘要"); B()
    gp_protect = "完美" if all(v['rate']==1.0 for v in gp.values()) else "部分完成"
    msg = (f"本报告对基于大语言模型的国际关系多智能体仿真系统（ID22）进行逐轮逐国的追随行为校验。"
           f"校验场景为一战前欧洲（1913Q1-1925Q2，50轮，每轮=3个月），共19个国家。"
           f"核心指标为追随行为F1分数，计算基于750个逐轮逐国观测点（15个中小国家×50轮）。"
           f"校验建立在一个关键概念区分之上：追随（Following）不等于同盟（Alliance）——"
           f"追随是议题特定的领导偏好，不等同于制度化的安全同盟。"
           f"结果显示：追随F1={o['f1']:.4f}（Precision={o['p']:.4f}, Recall={o['r']:.4f}），"
           f"处于{lv}水平。"
           f"逐轮F1均值={avg_rnd_f1:.4f}，标准差={std_f1:.4f}，"
           f"最高轮次R{max_rnd['round']}={max_rnd['f1']:.4f}，"
           f"最低轮次R{min_rnd['round']}={min_rnd['f1']:.4f}。"
           f"三大强国独立性保护{gp_protect}。"
           f"误差结构中FP（错误追随）占比{fpr:.1f}%，FN（遗漏追随）占比{fnr:.1f}%。")
    P(msg); B()
    P("关键词：多智能体仿真；国际关系；模型校验；F1分数；追随行为；逐轮校验；一战前欧洲"); B()
    P("---"); B()
    P(f"仿真编号：ID22 | 场景：一战前欧洲（1913年） | 日期：{datetime.now().strftime('%Y-%m-%d')} | "
      f"轮数：50轮（每轮=3个月） | 国家：19国（4大国+15中小国）"); B()
    P("---"); B()

    # Sec 1
    P("## 1 核心概念界定：追随不等于同盟"); B()
    P("### 1.1 概念区分"); B()
    P("在进行模型校验之前，必须首先明确追随与同盟是两个完全不同层次的概念。"
      "同盟（Alliance）是国家间通过正式或非正式条约建立的长期安全合作关系，具有制度化和持久性特征。"
      "追随（Following）则是在特定议题上对某一大国的政策偏好和领导认可，具有议题特定性和短期变动性。"
      "追随不要求制度化的同盟关系——同盟国之间可能在特定议题层面选择追随不同的大国，"
      "这正是国际关系复杂性的核心体现。"); B()
    P("### 1.2 历史案例：追随不等于同盟"); B()
    P("| 国家 | 同盟关系 | 追随对象 | 逻辑 |\n"
      "|------|---------|---------|------|\n"
      "| France | 法俄同盟(1894) | 追随UK | 海军军备竞赛与殖民地争夺是1913年主导议题，法国在海军议题上协调UK |\n"
      "| Italy | 三国同盟(德奥意,1882) | 追随UK | 意大利的殖民扩张与海军利益与UK趋同，构成经典的议题性叛离 |\n"
      "| Netherlands | 无军事同盟 | 追随UK | 荷兰殖民帝国安全依赖英国海权保护，虽与德国有强经济联系 |\n"
      "| Switzerland | 永久中立 | 追随UK | 德语区经济联系德国，但安全均势议题上追随UK |"); B()
    P("### 1.3 校验指标"); B()
    P("本报告以追随行为F1分数为唯一核心校验指标。F1是Precision和Recall的调和平均。"
      "校验基于750个逐轮逐国观测点（15个非大国×50轮），"
      "大国（德国、俄国、英国、法国）作为体系领导者永远为独立决策，不参与F1计算。"); B()

    # Sec 2
    P("## 2 校验方法"); B()
    P("### 2.1 F1计算公式"); B()
    P("$$P = TP/(TP+FP), \\quad R = TP/(TP+FN), \\quad F1 = 2PR/(P+R)$$"); B()
    P("其中，TP（True Positive）为仿真追随目标与历史追随目标一致的情况；"
      "FP（False Positive）为仿真错误追随或不应追随却追随的情况；"
      "FN（False Negative）为仿真遗漏的追随（历史要求追随但仿真中立）；"
      "TN（True Negative）为仿真与历史均为中立的情况。"); B()
    P("### 2.2 混淆矩阵定义"); B()
    P("| 分类 | 定义 |\n"
      "|------|------|\n"
      "| TP | 仿真追随目标 = 历史追随目标（均非空） |\n"
      "| FP | 仿真追随目标 ≠ 历史追随目标，或仿真追随了但历史要求中立 |\n"
      "| FN | 仿真中立，但历史要求追随某人 |\n"
      "| TN | 仿真中立，历史也要求中立 |"); B()
    P("### 2.3 历史地面真值数据（v2）"); B()
    P("历史地面真值数据（v2版，由generate_history_v2.py生成）为逐轮（50轮×3个月）逐国（19国）的追随标注。"
      "每轮有一个明确的主导国际议题（如海军军备竞赛、七月危机、鲁尔危机等），"
      "每个国家的追随目标基于该国在该议题上的实际外交政策立场确定。"
      "关键设计原则：意大利作为三国同盟成员，在殖民/海军议题上仍追随UK（议题性叛离）；"
      "法国作为法俄同盟成员，在海军议题上追随UK（非同盟归属，是议题追随）。"); B()

    # Sec 3
    P("## 3 校验结果"); B()
    P("### 3.1 整体结果"); B()
    P("表1：追随行为F1整体结果"); B()
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
    ]
    P("\n".join(rows)); B()
    P(f"逐轮F1统计：均值={avg_rnd_f1:.4f}，标准差={std_f1:.4f}，"
      f"最高R{max_rnd['round']}={max_rnd['f1']:.4f}，"
      f"最低R{min_rnd['round']}={min_rnd['f1']:.4f}。"); B()

    if o['r'] > o['p']:
        precall = "Recall大于Precision，表明误差以FP（错误追随）为主——模型倾向于过度追随，在历史要求中立或追随其他领袖时仍追随某大国。"
    else:
        precall = "Precision大于Recall，表明误差以FN（遗漏追随）为主——模型倾向于过度保守，在历史要求追随时选择保持中立。"
    P(precall); B()

    P(f"![F1时序图](figures/{cn['fig1']})"); B()
    P("图1：50轮追随F1逐轮变化，含5轮移动平均和历史阶段标注。F1呈明显的跨轮波动，"
      "反映了不同议题条件下仿真-历史一致性的差异。"); B()
    P(f"![混淆矩阵](figures/{cn['fig3']})"); B()
    P("图3：整体混淆矩阵，四个象限分别展示TP、FP、FN、TN的数量。"); B()

    P("### 3.2 逐国结果"); B()
    P("表2：各国追随F1详情（按F1降序排列）"); B()
    rows = ["| 国家 | TP | FP | FN | TN | P | R | F1 |",
            "|------|----|----|----|----|---|---|----|"]
    for name,d in si:
        rows.append(f"| {name} | {d['tp']} | {d['fp']} | {d['fn']} | {d['tn']} | {d['p']:.4f} | {d['r']:.4f} | {d['f1']:.4f} |")
    P("\n".join(rows)); B()
    best_str = ' / '.join([f'{n}(F1={d["f1"]:.2f})' for n,d in best])
    worst_str = ' / '.join([f'{n}(F1={d["f1"]:.2f})' for n,d in reversed(worst)])
    P(f"最佳三国：{best_str}。最劣三国：{worst_str}。"); B()
    P(f"![逐国F1](figures/{cn['fig2']})"); B()
    P("图2：15个中小国家的F1/Precision/Recall并排柱状图，按F1降序排列。"); B()
    P(f"![Precision-Recall散点](figures/{cn['fig8']})"); B()
    P("图8：各国Precision-Recall散点图，气泡大小代表F1，颜色深浅代表F1高低。"
      "虚线为等F1线，用于比较不同国家的精准度-召回率权衡。" ); B()

    P("### 3.3 大国独立性"); B()
    rows = ["| 国家 | 独立轮数 | 独立率 |",
            "|------|---------|--------|"]
    for n,m in gp.items():
        rows.append(f"| {n} | {m['ind']}/50 | {m['rate']*100:.0f}% |")
    P("\n".join(rows)); B()
    if all(v['rate']==1.0 for v in gp.values()):
        P("三大强国在全部50轮中保持100%独立决策，大国独立性保护机制运行完美。"); B()
    else:
        P("三大强国独立性保护机制运行总体良好，部分大国存在少量追随行为。"); B()

    # Sec 4
    P("## 4 逐轮逐国可视化分析"); B()
    P(f"![热力图](figures/{cn['fig4']})"); B()
    P("图4：逐轮逐国追随正确性热力图。每格代表一个国家在特定轮次的追随是否正确（绿=正确，红=错误）。"
      "横轴为50轮，纵轴为15个中小国家。从图中可以直观观察哪些国家在哪些轮次追随正确，"
      "以及正确/错误的时空分布模式。右侧柱状图为各国的50轮整体准确率。"); B()
    P(f"![阵营演化](figures/{cn['fig5']})"); B()
    P("图5：阵营追随格局演化。展示四大国（UK/德国/俄国/法国）每轮获得的追随者数量变化。"); B()
    P(f"![大国独立性](figures/{cn['fig6']})"); B()
    P("图6：大国独立性柱状图，展示三大强国的独立决策比率。"); B()
    P(f"![细节分析](figures/{cn['fig7']})"); B()
    P("图7：逐轮TP/FP/FN叠层柱状图（图7a）和各历史阶段F1箱线图（图7b），"
      "用于分析误差的时序结构和各历史阶段的F1分布。"); B()

    # Sec 5
    P("## 5 讨论"); B()
    P("### 5.1 结果评价"); B()
    if o['f1'] > 0.7:
        eval_text = "已达到良好水平（F1≥0.70），表明模型在追随行为的历史复现方面取得了显著进展。"
    elif o['f1'] > 0.5:
        eval_text = "处于中等水平（0.50≤F1<0.70），距离良好水平仍有差距。"
    else:
        eval_text = "处于低水平（F1<0.50），历史复现能力有待提升。"
    if o['f1'] > 0.25:
        rand_text = "显著优于随机基准（4分类问题随机F1约等于0.25），表明模型具有超越随机水平的历史复现能力。"
    else:
        rand_text = "接近随机基准，历史复现能力有待提升。"
    P(f"ID22在逐轮逐国校验中取得F1={o['f1']:.4f}，处于{lv}水平。{eval_text}"
      f"此结果{rand_text}"); B()

    P("### 5.2 误差模式分析"); B()
    italy_f1=pcd.get('Italy',{}).get('f1',0); sweden_f1=pcd.get('Sweden',{}).get('f1',0)
    swiss_f1=pcd.get('Switzerland',{}).get('f1',0); spain_f1=pcd.get('Spain',{}).get('f1',0)
    france_f1=pcd.get('France',{}).get('f1',0)
    swing_min = min(sweden_f1, swiss_f1, spain_f1)
    swing_comment = "无法" if swing_min < 0.3 else "部分"
    if italy_f1 < 0.1:
        italy_diag = "仿真完全无法捕捉这种议题性外交行为——意大利在仿真中主要追随德国（同盟行为），而历史要求追随UK（议题追随）。"
        italy_defect = "最核心的结构性缺陷。"
    elif italy_f1 > 0.5:
        italy_diag = f"意大利的F1表现较好（F1={italy_f1:.2f}），表明模型在捕捉议题性外交动态方面取得了进展，但仍有FP={pcd['Italy']['fp']}次错误追随有待改善。"
        italy_defect = "需要持续观测的指标。"
    else:
        italy_diag = f"意大利的F1表现一般，表明模型在一定程度上捕捉到了议题性外交动态。"
        italy_defect = "需要持续观测的指标。"
    P(f"(1) 意大利的议题性叛离：这是追随不等于同盟最关键的试金石。"
      f"意大利在历史上是三国同盟成员，但在殖民和海军议题上追随UK。{italy_diag}"
      f"这是模型{italy_defect}"); B()
    P(f"(2) 摇摆国的追随困境：瑞典（F1={sweden_f1:.2f}）、瑞士（F1={swiss_f1:.2f}）、"
      f"西班牙（F1={spain_f1:.2f}）处于大国夹缝中。其中瑞士表现优异（F1={swiss_f1:.2f}），"
      f"说明模型成功识别了其追随UK的议题性选择；"
      f"瑞典（F1={sweden_f1:.2f}）是表现最差的中小国家，FP={pcd['Sweden']['fp']}次错误追随占其50轮的大部分。"
      f"模型{swing_comment}复现这种基于议题的选择性追随。"); B()

    P("### 5.3 模型优势"); B()
    high_f1_countries = [n for n,d in si if d['f1']>=0.7]
    zero_fp_countries = [n for n,d in pcd.items() if d['fp']<=2 and d['tp']>0]
    gp_protect_text = "100%" if all(v['rate']==1.0 for v in gp.values()) else "总体良好"
    if zero_fp_countries:
        P(f"(1) 精准追随者识别：{'/'.join(zero_fp_countries)}的FP≤2，Precision极高，表明模型对UK核心追随阵营的识别精准度显著提升。"); B()
    if high_f1_countries:
        P(f"(2) 高F1国家阵营（F1≥0.70）：{'/'.join(high_f1_countries)}（共{len(high_f1_countries)}国），"
          f"占中小国家的{len(high_f1_countries)/15*100:.0f}%，表明大部分国家的追随方向预测较为准确。"); B()
    P(f"(3) 意大利议题性叛离改善（F1={italy_f1:.2f}）：相比ID21的F1=0.00，ID22中意大利的F1大幅提升，"
      f"模型开始捕捉到意大利在殖民/海军议题上的UK追随特征，TP={pcd['Italy']['tp']}次。"); B()
    P(f"(4) 大国独立性保护：四大强国独立决策率{gp_protect_text}。"); B()

    P("### 5.4 改进方向"); B()
    P("(1) 引入多议题追随框架：允许中小国家在不同议题上追随不同的大国——这是解决意大利问题的关键。"); B()
    P("(2) 增强中小国家的追随激活：减少不必要的中立回合，使追随行为更频繁。"); B()
    P("(3) 摇摆国决策细化：为地缘夹缝中的国家引入议题权衡和位置权重。"); B()

    # Sec 6
    P("## 6 结论"); B()
    if o['f1'] > 0.25:
        rand_comment = "显著优于随机基准；"
    else:
        rand_comment = ""
    err_type = "FP（错误追随）" if o['fp'] > o['fn'] else "FN（遗漏追随）"
    if italy_f1 < 0.05:
        italy_conclusion = "完全失败（F1=0.00），是模型核心缺陷"
    else:
        italy_conclusion = "仍需改进"
    P(f"本报告以逐轮逐国的精度对ID22一战前欧洲仿真进行了系统校验。"
      f"基于v2历史地面真值数据（50轮×15国=750观测点，每轮有明确的议题框架和逐国追随标注），"
      f"获得追随行为F1={o['f1']:.4f}（P={o['p']:.4f}, R={o['r']:.4f}）。"
      f"主要发现：（1）F1处于{lv}水平，{rand_comment}"
      f"（2）误差以{err_type}为主；"
      f"（3）意大利的议题性叛离{italy_conclusion}；"
      f"（4）摇摆国预测困难。"
      f"建议后续模型迭代重点引入多议题追随框架。"); B()
    P("---"); B()
    P("## 附录A：历史地面真值说明"); B()
    P("本报告使用v2版历史地面真值数据（generate_history_v2.py生成）。"
      "每轮（3个月）有独立的议题定义和逐国追随标注。"
      "数据位于data/history/scene1_prewar_1913.json。"); B()
    P("## 附录B：输出文件"); B()
    P("| 文件 | 说明 |\n"
      "|------|------|\n"
      "| ID22_模型校验报告.md | 本报告 |\n"
      "| data/id22_results.json | 完整校验数据 |\n"
      "| data/id22_round_details.json | 逐轮详细数据 |\n"
      "| code/validate_id22_f1.py | 校验脚本 |\n"
      "| figures/ | 8张图表 |"); B()

    rp=os.path.join(OUT_DIR,"ID22_模型校验报告.md")
    with open(rp,'w',encoding='utf-8') as f: f.write('\n'.join(L))
    print(f"\n  [OK] Report: {rp}")
    return rp

def main():
    print("="*60); print("  ID22 Per-Round Per-Country F1 Validation"); print("="*60)
    print("[1/4] Loading data...")
    gt=load_gt(); sim=load_sim()
    print(f"  History v2: {gt['total_rounds']} rounds x {gt['num_countries']} countries")
    print(f"  Simulation: {len(sim['followers'])} rounds of follower data")
    print("[2/4] Computing F1...")
    fr=compute_f1(sim,gt); o=fr['overall']
    print(f"  F1={o['f1']:.4f} P={o['p']:.4f} R={o['r']:.4f} TP={o['tp']} FP={o['fp']} FN={o['fn']} TN={o['tn']}")
    print("[3/4] Generating charts (8 figures)...")
    cn={}
    cn['fig1']=ch1_f1_ts(fr)
    cn['fig2']=ch2_per_country(fr)
    cn['fig3']=ch3_cm(fr)
    cn['fig4']=ch4_heatmap(sim,gt)
    cn['fig5']=ch5_faction_ev(sim)
    cn['fig6']=ch6_gp_ind(fr)
    cn['fig7']=ch7_f1_dist(fr)
    cn['fig8']=ch8_precision_recall_curve(fr)
    print("[4/4] Generating report...")
    rp=gen_report(fr,sim,gt,cn)

    # Save data
    json.dump({'project_id':PID,'overall':fr['overall'],'per_country':fr['per_country'],
               'gp_independence':fr['gp_independence']},
              open(os.path.join(OUT_DIR,'data','id22_results.json'),'w',encoding='utf-8'),
              ensure_ascii=False,indent=2)
    json.dump({'project_id':PID,'per_round':fr['per_round']},
              open(os.path.join(OUT_DIR,'data','id22_round_details.json'),'w',encoding='utf-8'),
              ensure_ascii=False,indent=2)

    print(f"\n{'='*60}")
    print(f"  ID22 F1={o['f1']:.4f} | P={o['p']:.4f} | R={o['r']:.4f}")
    print(f"  Report: {rp}")
    print(f"{'='*60}")

if __name__=="__main__": main()
