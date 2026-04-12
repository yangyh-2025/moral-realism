"""
LLM JSONL 日志回填脚本

将 logs/{project_id}/ 目录下的 4 类 LLM 日志文件逐行解析后批量插入数据库。
幂等:已回填的项目会跳过。

用法:
    python -m app.scripts.backfill_llm_logs --all          # 回填所有项目
    python -m app.scripts.backfill_llm_logs --project-id 5 # 仅回填项目 5
    BACKFILL_LLM_ON_START=1 python start.py                # 启动时自动回填
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from sqlalchemy import func, insert, select

# 确保项目根目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config.database import db_config  # noqa: E402
from app.models.llm_call_log import LLMCallLog  # noqa: E402

LLM_CATEGORIES = [
    "interaction",
    "following",
    "goal_evaluation",
    "relationship_evolution",
]

LOGS_DIR = Path("logs")
BATCH_SIZE = 500


def _parse_timestamp(ts_str: str) -> Optional[datetime]:
    """解析 ISO 格式时间戳"""
    if not ts_str:
        return None
    try:
        # 处理含 Z 的情况
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


def _extract_response_text(resp: Any) -> str:
    """将 response 转为字符串"""
    if isinstance(resp, str):
        return resp
    try:
        return json.dumps(resp, ensure_ascii=False)
    except Exception:
        return str(resp)


async def _should_skip_project(session, project_id: int) -> bool:
    """检查项目是否已有 LLM 记录（幂等）"""
    result = await session.execute(
        select(func.count())
        .select_from(LLMCallLog)
        .where(LLMCallLog.project_id == project_id)
    )
    count = result.scalar() or 0
    return count > 0


async def _backfill_project(project_id: int) -> int:
    """回填单个项目的所有 JSONL 日志，返回插入条数"""
    inserted = 0
    total_lines = 0
    async for session in db_config.get_session():
        if await _should_skip_project(session, project_id):
            logger.info(f"项目 {project_id}: 已有 LLM 记录，跳过")
            return 0

    for category in LLM_CATEGORIES:
        log_file = LOGS_DIR / str(project_id) / f"llm_{category}.log"
        if not log_file.exists():
            continue

        batch: List[Dict[str, Any]] = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_lines += 1

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning(f"项目 {project_id} 解析失败: {log_file.name} 第 {total_lines} 行")
                    continue

                ts = _parse_timestamp(data.get("timestamp", ""))
                latency = data.get("latency_ms")

                batch.append({
                    "project_id": project_id,
                    "round_num": data.get("round_num"),
                    "call_type": f"llm_{category}",
                    "phase": data.get("phase") or data.get("decision_type"),
                    "agent_id": data.get("agent_id"),
                    "target_agent_id": data.get("target_agent_id"),
                    "model_name": data.get("model_name"),
                    "prompt_full": data.get("full_prompt", ""),
                    "response_full": _extract_response_text(data.get("full_response", "")),
                    "response_parsed": None,  # 历史数据不存解析结果
                    "prompt_tokens": data.get("prompt_tokens"),
                    "completion_tokens": data.get("completion_tokens"),
                    "latency_ms": int(latency) if latency else None,
                    "status": "success" if data.get("success", True) else "failed",
                    "error_message": data.get("error_message"),
                    "created_at": ts if ts else datetime.utcnow(),
                })

                if len(batch) >= BATCH_SIZE:
                    await _insert_batch(batch)
                    inserted += len(batch)
                    batch = []

        if batch:
            await _insert_batch(batch)
            inserted += len(batch)

    logger.info(f"项目 {project_id}: 解析 {total_lines} 行，插入 {inserted} 条记录")
    return inserted


async def _insert_batch(batch: List[Dict[str, Any]]) -> None:
    """批量插入一批记录"""
    if not batch:
        return
    async for session in db_config.get_session():
        await session.execute(insert(LLMCallLog), batch)
        await session.commit()


async def main() -> None:
    parser = argparse.ArgumentParser(description="回填 LLM JSONL 日志到数据库")
    parser.add_argument("--all", action="store_true", help="回填所有项目")
    parser.add_argument("--project-id", type=int, help="指定项目 ID")
    args = parser.parse_args()

    if not args.all and args.project_id is None:
        parser.print_help()
        sys.exit(1)

    project_ids: List[int] = []
    if args.project_id is not None:
        project_ids = [args.project_id]
    else:
        # 扫描 logs/ 下所有数字命名的子目录
        if LOGS_DIR.exists():
            for d in sorted(LOGS_DIR.iterdir(), key=lambda x: int(x.name) if x.name.isdigit() else 0):
                if d.is_dir() and d.name.isdigit():
                    project_ids.append(int(d.name))

    if not project_ids:
        logger.info("未找到任何项目日志目录")
        return

    total_inserted = 0
    for pid in project_ids:
        try:
            count = await _backfill_project(pid)
            total_inserted += count
        except Exception as e:
            logger.error(f"项目 {pid} 回填失败: {e}")

    logger.info(f"回填完成，共插入 {total_inserted} 条记录")


if __name__ == "__main__":
    asyncio.run(main())


# lifespan 启动钩子使用的入口函数
async def backfill_all_on_start() -> None:
    """启动时自动回填所有项目（由 main.py lifespan 调用）"""
    env_flag = os.environ.get("BACKFILL_LLM_ON_START", "")
    if env_flag not in ("1", "true", "True", "yes", "YES"):
        return

    logger.info("BACKFILL_LLM_ON_START=1, 开始自动回填 LLM 日志...")
    project_ids: List[int] = []
    if LOGS_DIR.exists():
        for d in sorted(LOGS_DIR.iterdir(), key=lambda x: int(x.name) if x.name.isdigit() else 0):
            if d.is_dir() and d.name.isdigit():
                project_ids.append(int(d.name))

    total_inserted = 0
    for pid in project_ids:
        try:
            count = await _backfill_project(pid)
            total_inserted += count
        except Exception as e:
            logger.error(f"项目 {pid} 回填失败: {e}")

    logger.info(f"启动回填完成，共插入 {total_inserted} 条记录")
