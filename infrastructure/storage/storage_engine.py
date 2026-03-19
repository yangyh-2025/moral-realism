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

            # 额外的性能优化索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_id
                ON agent_states(agent_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_simulation_id
                ON agent_states(simulation_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_decision_agent
                ON decisions(agent_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_interaction_round
                ON interactions(simulation_id, round)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_speech_round
                ON speeches(simulation_id, round)
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

    def save_simulation_end(
        self,
        simulation_id: str,
        total_rounds: int,
        status: str = "completed"
    ) -> None:
        """保存仿真结束记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE simulations
                SET end_time = ?, total_rounds = ?, status = ?
                WHERE simulation_id = ?
            """, (
                datetime.now().isoformat(),
                total_rounds,
                status,
                simulation_id
            ))
            conn.commit()

    def batch_save_decisions(self, decisions: List[Dict]) -> None:
        """
        批量保存决策记录（性能优化）

        Args:
            decisions: 决策记录列表
        """
        if not decisions:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for decision in decisions:
                reasoning = decision.get('reasoning')
                cursor.execute("""
                    INSERT INTO decisions
                    (simulation_id, round, agent_id, function_name,
                     function_args, validation_result, reasoning,
                     situation_analysis, strategic_consideration,
                     expected_outcome, alternatives, full_reasoning, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    decision['simulation_id'],
                    decision['round'],
                    decision['agent_id'],
                    decision['function_name'],
                    json.dumps(decision['function_args']),
                    json.dumps(decision['validation_result']),
                    json.dumps(reasoning) if reasoning else None,
                    reasoning.get('situation_analysis') if reasoning else None,
                    reasoning.get('strategic_consideration') if reasoning else None,
                    reasoning.get('expected_outcome') if reasoning else None,
                    json.dumps(reasoning.get('alternatives')) if reasoning and 'alternatives' in reasoning else None,
                    reasoning.get('full_reasoning') if reasoning else None,
                    datetime.now().isoformat()
                ))

            conn.commit()

    def get_agent_states_paginated(
        self,
        simulation_id: str,
        page: int = 1,
        page_size: int = 100,
        round: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        分页查询智能体状态（性能优化）

        Args:
            simulation_id: 仿真ID
            page: 页码
            page_size: 每页大小
            round: 轮次（可选）

        Returns:
            分页结果
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 计算总数
            if round is not None:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM agent_states
                    WHERE simulation_id = ? AND round = ?
                """, (simulation_id, round))
            else:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM agent_states
                    WHERE simulation_id = ?
                """, (simulation_id,))
            total = cursor.fetchone()[0]

            # 计算分页
            offset = (page - 1) * page_size
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

            # 查询数据
            if round is not None:
                cursor.execute("""
                    SELECT agent_id, agent_type, state_data, round, timestamp
                    FROM agent_states
                    WHERE simulation_id = ? AND round = ?
                    ORDER BY id
                    LIMIT ? OFFSET ?
                """, (simulation_id, round, page_size, offset))
            else:
                cursor.execute("""
                    SELECT agent_id, agent_type, state_data, round, timestamp
                    FROM agent_states
                    WHERE simulation_id = ?
                    ORDER BY id
                    LIMIT ? OFFSET ?
                """, (simulation_id, page_size, offset))

            rows = cursor.fetchall()
            data = [
                {
                    "agent_id": row[0],
                    "agent_type": row[1],
                    "state_data": json.loads(row[2]),
                    "round": row[3],
                    "timestamp": row[4]
                }
                for row in rows
            ]

            return {
                "data": data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }

    def get_metrics_paginated(
        self,
        simulation_id: str,
        page: int = 1,
        page_size: int = 100,
        metric_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分页查询指标数据（性能优化）

        Args:
            simulation_id: 仿真ID
            page: 页码
            page_size: 每页大小
            metric_type: 指标类型（可选）

        Returns:
            分页结果
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 计算总数
            if metric_type is not None:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM metrics
                    WHERE simulation_id = ? AND metric_type = ?
                """, (simulation_id, metric_type))
            else:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM metrics
                    WHERE simulation_id = ?
                """, (simulation_id,))
            total = cursor.fetchone()[0]

            # 计算分页
            offset = (page - 1) * page_size
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

            # 查询数据
            if metric_type is not None:
                cursor.execute("""
                    SELECT metric_type, metric_name, metric_value, round, metadata, timestamp
                    FROM metrics
                    WHERE simulation_id = ? AND metric_type = ?
                    ORDER BY id
                    LIMIT ? OFFSET ?
                """, (simulation_id, metric_type, page_size, offset))
            else:
                cursor.execute("""
                    SELECT metric_type, metric_name, metric_value, round, metadata, timestamp
                    FROM metrics
                    WHERE simulation_id = ?
                    ORDER BY id
                    LIMIT ? OFFSET ?
                """, (simulation_id, page_size, offset))

            rows = cursor.fetchall()
            data = [
                {
                    "metric_type": row[0],
                    "metric_name": row[1],
                    "metric_value": row[2],
                    "round": row[3],
                    "metadata": json.loads(row[4]) if row[4] else None,
                    "timestamp": row[5]
                }
                for row in rows
            ]

            return {
                "data": data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }

    def save_interaction(
        self,
        simulation_id: str,
        round: int,
        initiator_id: str,
        target_id: Optional[str],
        interaction_type: str,
        interaction_data: Dict,
        outcome: Dict,
        reasoning: Optional[str] = None
    ) -> None:
        """
        保存互动记录

        Args:
            simulation_id: 仿真ID
            round: 轮次
            initiator_id: 发起者ID
            target_id: 目标ID
            interaction_type: 互动类型
            interaction_data: 互动数据
            outcome: 执行结果
            reasoning: 互动理由
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interactions
                (simulation_id, round, initiator_id, target_id,
                 interaction_type, interaction_data, outcome, reasoning, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                simulation_id,
                round,
                initiator_id,
                target_id,
                interaction_type,
                json.dumps(interaction_data),
                json.dumps(outcome),
                reasoning,
                datetime.now().isoformat()
            ))
            conn.commit()

    def save_metric(
        self,
        simulation_id: str,
        round: int,
        metric_type: str,
        metric_name: str,
        metric_value: float,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        保存指标数据

        Args:
            simulation_id: 仿真ID
            round: 轮次
            metric_type: 指标类型
            metric_name: 指标名称
            metric_value: 指标值
            metadata: 元数据
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metrics
                (simulation_id, round, metric_type, metric_name,
                 metric_value, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                simulation_id,
                round,
                metric_type,
                metric_name,
                metric_value,
                json.dumps(metadata) if metadata else None,
                datetime.now().isoformat()
            ))
            conn.commit()

    def save_round_result(
        self,
        simulation_id: str,
        round: int,
        result: Dict
    ) -> None:
        """
        保存轮次结果

        Args:
            simulation_id: 仿真ID
            round: 轮次
            result: 轮次结果
        """
        # 保存轮次决策
        if 'decisions' in result:
            for decision in result['decisions']:
                self.save_decision(
                    simulation_id=simulation_id,
                    round=round,
                    agent_id=decision.get('agent_id'),
                    function_name=decision.get('function'),
                    function_args=decision.get('arguments', {}),
                    validation_result=decision.get('validation', {}),
                    reasoning=decision.get('reasoning')
                )

        # 保存轮次互动
        if 'interactions' in result:
            for interaction in result['interactions']:
                self.save_interaction(
                    simulation_id=simulation_id,
                    round=round,
                    initiator_id=interaction.get('initiator_id'),
                    target_id=interaction.get('target_id'),
                    interaction_type=interaction.get('interaction_type'),
                    interaction_data=interaction.get('interaction_data', {}),
                    outcome=interaction.get('outcome', {}),
                    reasoning=interaction.get('reasoning')
                )

        # 保存轮次指标
        if 'metrics' in result:
            metrics = result['metrics']
            if isinstance(metrics, dict):
                for metric_name, metric_value in metrics.items():
                    metric_type = 'dependent'  # 默认类型
                    self.save_metric(
                        simulation_id=simulation_id,
                        round=round,
                        metric_type=metric_type,
                        metric_name=metric_name,
                        metric_value=float(metric_value) if isinstance(metric_value, (int, float)) else 0.0
                    )

    def save_simulation_result(self, simulation_id: str, result: Dict) -> None:
        """
        保存仿真结果

        Args:
            simulation_id: 仿真ID
            result: 仿真结果
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 更新仿真记录
            cursor.execute("""
                UPDATE simulations
                SET end_time = ?,
                    total_rounds = ?,
                    status = ?
                WHERE simulation_id = ?
            """, (
                result.get('end_time'),
                result.get('total_rounds'),
                'completed',
                simulation_id
            ))

            # 保存最终状态
            if 'final_state' in result:
                final_state = result['final_state']
                if 'agents' in final_state:
                    for agent_state in final_state['agents']:
                        cursor.execute("""
                            INSERT INTO agent_states
                            (simulation_id, round, agent_id, agent_type,
                             state_data, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            simulation_id,
                            result.get('total_rounds', 0),
                            agent_state.get('agent_id'),
                            agent_state.get('agent_id'),  # 使用agent_id作为类型
                            json.dumps(agent_state),
                            datetime.now().isoformat()
                        ))

            conn.commit()
