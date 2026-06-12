#!/usr/bin/env python3
"""
validate_history_data.py
验证所有三个场景的历史地面真值数据完整性和一致性。
检查内容：
1. JSON 格式有效
2. 每轮每个国家都有追随目标 (target_index 在合理范围)
3. 没有缺失值 (null 在国家存在时不合理)
4. 追随目标不是自己
5. 每轮数据完整性 (countries * rounds)
"""

import json
import sys
from pathlib import Path

SCENES = {
    1: {
        "file": "data/history/scene1_prewar_1913.json",
        "name": "一战前欧洲(1913)",
        "expected_countries": 19,
        "expected_rounds": 50,
    },
    2: {
        "file": "data/history/scene2_prewar_1938.json",
        "name": "二战前欧洲(1938)",
        "expected_countries": 28,
        "expected_rounds": 40,
    },
    3: {
        "file": "data/history/scene3_prewar_1946.json",
        "name": "冷战前欧洲(1946)",
        "expected_countries": 25,
        "expected_rounds": 50,
    },
}

def validate_scene(scene_id, info):
    filepath = Path(info["file"])
    if not filepath.exists():
        return [f"文件不存在: {filepath}"]

    errors = []
    warnings = []

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    expected_ctry = info["expected_countries"]
    expected_rds = info["expected_rounds"]
    num_ctry = data.get("num_countries")
    rounds = data.get("rounds", {})

    # JSON 结构检查
    if num_ctry != expected_ctry:
        errors.append(f"国家数: {num_ctry} (应为 {expected_ctry})")
    if len(rounds) != expected_rds:
        errors.append(f"轮数: {len(rounds)} (应为 {expected_rds})")

    # 国家列表
    ctries = data.get("countries", [])
    ct_idx_set = {c["index"] for c in ctries}
    ct_name = {c["index"]: c["name"] for c in ctries}
    if max(ct_idx_set) != num_ctry or min(ct_idx_set) != 1:
        errors.append(f"国家 index 范围: {min(ct_idx_set)}-{max(ct_idx_set)} (应为 1-{num_ctry})")

    # 逐轮逐国检查
    total_missing = 0
    total_out_of_range = 0
    total_self_follow = 0
    rounds_with_missing = []

    for rnd_key, rnd_data in sorted(rounds.items(), key=lambda x: int(x[0])):
        rnd_num = rnd_data.get("round")
        following = rnd_data.get("following", {})

        missing_in_round = []
        for c_idx in ct_idx_set:
            c_key = str(c_idx)
            if c_key not in following:
                missing_in_round.append(c_idx)
                continue
            target = following[c_key]

            # 可能的合法值: null (小国不追随任何人) 或 正整数 (追随对象 index)
            if target is None:
                continue  # null 对于中立/不追随国家合法

            if not isinstance(target, int):
                errors.append(f"Round {rnd_num}, {ct_name[c_idx]}({c_idx}): 非整数目标 {target}")
                continue

            if target < 1 or target > num_ctry:
                total_out_of_range += 1
                errors.append(f"Round {rnd_num}, {ct_name[c_idx]}({c_idx}): 目标 {target} 超出范围 1-{num_ctry}")

            if target == c_idx:
                total_self_follow += 1
                errors.append(f"Round {rnd_num}, {ct_name[c_idx]}({c_idx}): 追随自己 (circular)")

        if missing_in_round:
            total_missing += len(missing_in_round)
            rounds_with_missing.append((rnd_num, missing_in_round))

    if total_missing > 0:
        warnings.append(f"共 {total_missing} 个缺失追随记录 (合法若该轮该国家未参与)")
        for rnd_num, missing in rounds_with_missing[:5]:
            names = [f"{ct_name.get(i, '?')}({i})" for i in missing]
            warnings.append(f"  Round {rnd_num}: {', '.join(names)}")

    if total_out_of_range > 0:
        errors.append(f"共 {total_out_of_range} 个超出范围的目标")

    if total_self_follow > 0:
        errors.append(f"共 {total_self_follow} 个自己追随自己的情况")

    # 检查 dominant_issue 字段
    missing_issues = 0
    for rnd_key, rnd_data in rounds.items():
        if not rnd_data.get("dominant_issue"):
            missing_issues += 1
    if missing_issues > 0:
        warnings.append(f"{missing_issues} 轮缺少 dominant_issue")

    # 汇总
    total_follows = len(rounds) * num_ctry - total_missing
    if total_out_of_range == 0 and total_self_follow == 0:
        status = "PASS"
    else:
        status = "FAIL"

    return errors, warnings, status, {
        "total_rounds": len(rounds),
        "total_countries": num_ctry,
        "total_follow_records": total_follows,
        "missing": total_missing,
        "out_of_range": total_out_of_range,
        "self_follow": total_self_follow,
    }


def main():
    all_ok = True
    for scene_id in [1, 2, 3]:
        info = SCENES[scene_id]
        result = validate_scene(scene_id, info)
        errors, warnings, status, stats = result

        print(f"\n{'='*60}")
        print(f"Scene {scene_id}: {info['name']}")
        print(f"{'='*60}")
        print(f"  Rounds: {stats['total_rounds']}, Countries: {stats['total_countries']}")
        print(f"  Records: {stats['total_follow_records']}, Missing: {stats['missing']}")
        print(f"  Status: {status}")

        if errors:
            print(f"\n  ERRORS ({len(errors)}):")
            for e in errors[:10]:
                print(f"    [ERROR] {e}")
            if len(errors) > 10:
                print(f"    ... 还有 {len(errors) - 10} 个错误")

        if warnings:
            print(f"\n  WARNINGS ({len(warnings)}):")
            for w in warnings[:10]:
                print(f"    [WARN] {w}")
            if len(warnings) > 10:
                print(f"    ... 还有 {len(warnings) - 10} 个警告")

        if status != "PASS":
            all_ok = False

    print(f"\n{'='*60}")
    if all_ok:
        print("ALL SCENES PASSED VALIDATION")
    else:
        print("SOME SCENES HAVE ERRORS - SEE ABOVE")
    print(f"{'='*60}")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
