"""
数据存储引擎 - 管理仿真数据存储

Git提交提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class StorageEngine:
    """
    数据存储引擎

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _initialize_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 智能体状态表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    round INTEGER,
                    agent_id TEXT,
                    agent_type TEXT,
                    state_data TEXT,
                    timestamp TEXT
                )
            """)

            # 决策记录表（增强版，包含决策理由）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    round INTEGER,
                    agent_id TEXT,
                    function_name TEXT,
                    function_args TEXT,
                    validation_result TEXT,
                    reasoning TEXT,
                    situation_analysis TEXT,
                    strategic_consideration TEXT,
                    expected_outcome TEXT,
                    alternatives TEXT,
                    full_reasoning TEXT,
                    timestamp TEXT
                )
            """)

            # 互动记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    round INTEGER,
                    initiator_id TEXT,
                    target_id TEXT,
                    interaction_type TEXT,
                    interaction_data TEXT,
                    outcome TEXT,
                    reasoning TEXT,
                    impact_assessment TEXT,
                    timestamp TEXT
                )
            """)

            # 发言记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS speeches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    round INTEGER,
                    agent_id TEXT,
                    speech_type TEXT,
                    target_id TEXT,
                    content TEXT,
                    reasoning TEXT,
                    audience TEXT,
                    reception TEXT,
                    timestamp TEXT
                )
            """)

            # 指标数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    round INTEGER,
                    metric_type TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    metadata TEXT,
                    timestamp TEXT
                )
            """)

            # 仿真元数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    config TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    total_rounds INTEGER,
                    status TEXT
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_simulation_round
                ON agent_states(simulation_id, round)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_decision_round
                ON decisions(simulation_id, round)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metric_round
                ON metrics(simulation_id, round)
            """)

            conn.commit()

    def save_simulation_start(self, simulation_id: str, config: Dict) -> None:
        """保存仿真开始记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO simulations
                (simulation_id, config, start_time, status)
                VALUES (?, ?, ?, ?)
            """, (
                simulation_id,
                json.dumps(config),
                datetime.now().isoformat(),
                "running"
            ))
            conn.commit()

    def save_decision(
        self,
        simulation_id: str,
        round: int,
        agent_id: str,
        function_name: str,
        function_args: Dict,
        validation_result: Dict,
        reasoning: Optional[Dict] = None
    ) -> None:
        """
        保存决策记录（包含决策理由）

        Args:
            simulation_id: 仿真ID
            round: 轮次
            agent_id: 智能体ID
            function_name: 函数名
            function_args: 函数参数
            validation_result: 验证结果
            reasoning: 决策理由（字典格式）
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO decisions
                (simulation_id, round, agent_id, function_name,
                 function_args, validation_result, reasoning,
                 situation_analysis, strategic_consideration,
                 expected_outcome, alternatives, full_reasoning, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                simulation_id,
                round,
                agent_id,
                function_name,
                json.dumps(function_args),
                json.dumps(validation_result),
                json.dumps(reasoning) if reasoning else None,
                reasoning.get('situation_analysis') if reasoning else None,
                reasoning.get('strategic_consideration') if reasoning else None,
                reasoning.get('expected_outcome') if reasoning else None,
                json.dumps(reasoning.get('alternatives')) if reasoning and 'alternatives' in reasoning else None,
                reasoning.get('full_reasoning') if reasoning else None,
                datetime.now().isoformat()
            ))
            conn.commit()
