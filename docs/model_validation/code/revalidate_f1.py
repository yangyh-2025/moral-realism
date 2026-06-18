#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Re-validate ID22/ID25/ID26 with updated configs:
  ID22: Great powers = {1,2,3,4} (FRN added), 15 non-GP × 50 = 750 obs
  ID25: Truncated to 32 rounds, 25 non-GP × 32 = 800 obs
  ID26: Unchanged (23 non-GP × 50 = 1150 obs), re-run for consistency
"""
import json, os, sqlite3
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))  # up to python/
DB_PATH = os.path.join(BASE_DIR, "data", "abm_simulation.db")

# ─── Config ──────────────────────────────────────────────────────────
SCENES = {
    "ID22": {
        "pid": 22,
        "history": "data/history/scene1_prewar_1913.json",
        "ccode2idx": {255:1,365:2,200:3,220:4,300:5,325:6,640:7,355:8,230:9,211:10,
                      350:11,380:12,210:13,360:14,235:15,390:16,225:17,345:18,385:19},
        "gp": {1,2,3,4},  # GMY, RUS, UKG, FRN
        "total_rounds": 50,
    },
    "ID25": {
        "pid": 25,
        "history": "data/history/scene2_prewar_1938.json",
        "ccode2idx": {365:1,255:2,200:3,220:4,325:5,290:6,230:7,315:8,211:9,360:10,
                      640:11,345:12,380:13,210:14,310:15,350:16,235:17,212:18,390:19,
                      375:20,225:21,355:22,385:23,366:24,368:25,205:26,369:27,339:28},
        "gp": {1,2,3},  # RUS, GMY, UKG
        "total_rounds": 32,  # truncated from 40
    },
    "ID26": {
        "pid": 26,
        "history": "data/history/scene3_prewar_1946.json",
        "ccode2idx": {365:1,200:2,220:3,325:4,290:5,230:6,640:7,315:8,211:9,210:10,
                      380:11,345:12,360:13,310:14,350:15,355:16,235:17,212:18,390:19,
                      225:20,385:21,375:22,205:23,339:24,395:25},
        "gp": {1,2},  # RUS, UKG
        "total_rounds": 50,
    },
}

def load_gt(path):
    with open(os.path.join(BASE_DIR, path), 'r', encoding='utf-8') as f:
        return json.load(f)

def load_sim_data(pid, total_rounds, ccode2idx):
    """Load follower_relation and agent_config from DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # agent: map DB agent_id → (idx, cc_found)
    c.execute("SELECT agent_id, country_code FROM agent_config WHERE project_id=?", (pid,))
    agent_rows = c.fetchall()
    agent2idx = {}
    idx2agent = {}
    cc_found = set()
    for aid, cc in agent_rows:
        if cc and cc in ccode2idx:
            ix = ccode2idx[cc]
            agent2idx[aid] = ix
            idx2agent[ix] = aid
            cc_found.add(cc)
    if not agent2idx:
        # fallback: index-based (IDs may not match country_code)
        for aid, cc in agent_rows:
            if aid in ccode2idx:
                agent2idx[aid] = ccode2idx[aid]
                idx2agent[ccode2idx[aid]] = aid
        if not agent2idx:
            # last resort: assign by order
            c.execute("SELECT agent_id FROM agent_config WHERE project_id=? ORDER BY agent_id", (pid,))
            aids = [r[0] for r in c.fetchall()]
            for i, aid in enumerate(aids, 1):
                agent2idx[aid] = i
                idx2agent[i] = aid

    # follower data
    c.execute("""SELECT fr.round_num, fr.follower_agent_id, fr.leader_agent_id
                 FROM follower_relation fr
                 WHERE fr.project_id=? ORDER BY fr.round_num""", (pid,))
    sim_following = defaultdict(dict)  # round_num → {follower_idx → leader_idx}
    for rn, fa, la in c.fetchall():
        if rn > total_rounds:
            continue
        fi = agent2idx.get(fa)
        li = agent2idx.get(la) if la else None
        if fi is not None:
            sim_following[rn][fi] = li  # key by index, value is leader index

    conn.close()
    return sim_following, agent2idx, idx2agent

def compute_f1(gt, sim_following, gp, total_rounds, ccode2idx, agent2idx, idx2agent):
    """Compute F1 — matches original validate_idXX_f1.py logic precisely."""
    all_gp_idx = gp  # set of indices that are great powers

    tp = fp = fn = tn = 0
    per_round = {}
    per_country = defaultdict(lambda: {'tp':0,'fp':0,'fn':0,'tn':0})

    for rn in range(1, total_rounds + 1):
        rk = str(rn)
        rd = gt['rounds'].get(rk, {})
        gt_fw = rd.get('following', {})
        rtp = rfp = rfn = rtn = 0

        for aid, idx in agent2idx.items():
            if idx in all_gp_idx:
                continue  # skip great powers

            # GT leader for this country (by index key)
            gt_leader = gt_fw.get(str(idx))
            # Simulation leader: sim_following is keyed by INDEX, not agent_id
            sim_leader_idx = sim_following.get(rn, {}).get(idx)

            if gt_leader is not None:
                if sim_leader_idx is not None:
                    if sim_leader_idx == gt_leader:
                        rtp += 1; per_country[idx]['tp'] += 1
                    else:
                        rfp += 1; per_country[idx]['fp'] += 1
                else:
                    rfn += 1; per_country[idx]['fn'] += 1
            else:
                if sim_leader_idx is not None:
                    rfp += 1; per_country[idx]['fp'] += 1
                else:
                    rtn += 1; per_country[idx]['tn'] += 1

        tp += rtp; fp += rfp; fn += rfn; tn += rtn
        p_val = rtp / (rtp + rfp) if (rtp + rfp) > 0 else 0
        r_val = rtp / (rtp + rfn) if (rtp + rfn) > 0 else 0
        f1_val = 2 * p_val * r_val / (p_val + r_val) if (p_val + r_val) > 0 else 0
        per_round[rn] = {'tp': rtp, 'fp': rfp, 'fn': rfn, 'tn': rtn,
                         'total': rtp+rfp+rfn+rtn, 'f1': f1_val, 'p': p_val, 'r': r_val}

    # Overall + per-country
    overall_p = tp / (tp + fp) if (tp + fp) > 0 else 0
    overall_r = tp / (tp + fn) if (tp + fn) > 0 else 0
    overall_f1 = 2 * overall_p * overall_r / (overall_p + overall_r) if (overall_p + overall_r) > 0 else 0

    per_country_out = {}
    for idx in sorted(per_country.keys()):
        d = per_country[idx]
        p_val = d['tp'] / (d['tp'] + d['fp']) if (d['tp'] + d['fp']) > 0 else 0
        r_val = d['tp'] / (d['tp'] + d['fn']) if (d['tp'] + d['fn']) > 0 else 0
        f1_val = 2 * p_val * r_val / (p_val + r_val) if (p_val + r_val) > 0 else 0
        per_country_out[idx] = {'tp': d['tp'], 'fp': d['fp'], 'fn': d['fn'], 'tn': d['tn'],
                                'f1': f1_val, 'p': p_val, 'r': r_val}

    # GP independence — check by index in sim_following
    gp_ind = {}
    for idx in gp:
        ind_count = sum(1 for rn in range(1, total_rounds + 1)
                       if sim_following.get(rn, {}).get(idx) is None)
        gp_ind[idx] = {'independent': ind_count, 'total': total_rounds, 'rate': ind_count / total_rounds}

    return {'f1': overall_f1, 'p': overall_p, 'r': overall_r,
            'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'total_obs': tp + fp + fn + tn,
            'per_round': per_round, 'per_country': per_country_out, 'gp_independence': gp_ind}

def main():
    results = {}
    for tag, cfg in SCENES.items():
        print(f"\n{'='*60}")
        print(f"Processing {tag} (PID={cfg['pid']}, rounds={cfg['total_rounds']}, GP={cfg['gp']})")

        gt = load_gt(cfg['history'])
        sim_following, agent2idx, idx2agent = load_sim_data(cfg['pid'], cfg['total_rounds'], cfg['ccode2idx'])
        print(f"  Loaded {len(agent2idx)} agents, {sum(len(v) for v in sim_following.values())} follower records")

        r = compute_f1(gt, sim_following, cfg['gp'], cfg['total_rounds'], cfg['ccode2idx'], agent2idx, idx2agent)

        print(f"  F1={r['f1']:.4f}  P={r['p']:.4f}  R={r['r']:.4f}")
        print(f"  TP={r['tp']} FP={r['fp']} FN={r['fn']} TN={r['tn']}  Obs={r['total_obs']}")

        # Per-round stats
        f1s = [v['f1'] for v in r['per_round'].values()]
        import statistics
        print(f"  Per-round F1: mean={statistics.mean(f1s):.4f} stdev={statistics.stdev(f1s):.4f} min={min(f1s):.4f} max={max(f1s):.4f}")

        # Per-country
        f1_zero = []
        for idx, pc in sorted(r['per_country'].items()):
            if pc['f1'] == 0:
                f1_zero.append(idx)
        print(f"  F1=0 countries (idx): {f1_zero}")

        results[tag] = r

    # ─── Cross-scene summary ──────────────────────────────────────────
    print(f"\n{'='*60}")
    print("CROSS-SCENE SUMMARY")
    print(f"{'Metric':<18} {'ID22':>10} {'ID25':>10} {'ID26':>10}")
    for k in ['f1', 'p', 'r']:
        vals = '  '.join(f"{results[t][k]:.4f}" for t in ['ID22','ID25','ID26'] if t in results)
        print(f"{k:<18} {vals}")
    for k in ['tp', 'fp', 'fn', 'tn', 'total_obs']:
        vals = '  '.join(f"{results[t][k]:>10}" for t in ['ID22','ID25','ID26'] if t in results)
        print(f"{k:<18} {vals}")

    # ─── Save results ─────────────────────────────────────────────────
    out = {}
    for tag, r in results.items():
        out[tag] = {
            'f1': r['f1'], 'precision': r['p'], 'recall': r['r'],
            'tp': r['tp'], 'fp': r['fp'], 'fn': r['fn'], 'tn': r['tn'],
            'total_obs': r['total_obs'],
            'per_round_f1_mean': sum(v['f1'] for v in r['per_round'].values())/len(r['per_round']),
            'per_round_f1_stdev': (lambda vs: (sum((x-sum(vs)/len(vs))**2 for x in vs)/(len(vs)-1))**0.5)([v['f1'] for v in r['per_round'].values()]),
        }
    out_path = os.path.join(BASE_DIR, 'docs', 'model_validation', 'updated_f1_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {out_path}")

if __name__ == '__main__':
    main()
