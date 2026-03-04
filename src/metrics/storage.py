"""
Data storage for metrics in moral realism ABM system.

This module provides DataStorage class for persisting simulation data
including metrics, checkpoints, and exports to various formats.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataStorage:
    """
    Simulation data persistence storage.

    Handles saving and loading metrics, checkpoints, and
    exporting data to various formats (JSON, CSV).
    """

    def __init__(self, base_dir: Optional[str] = None, storage_format: str = "json") -> None:
        """
        Initialize data storage.

        Args:
            base_dir: Base directory for storing data. Defaults to "data/".
            storage_format: Default format for storing metrics ("json" or "csv").
        """
        if base_dir is None:
            self.base_dir = Path("data")
        else:
            self.base_dir = Path(base_dir)

        self.storage_format = storage_format
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.base_dir / "checkpoints",
            self.base_dir / "outputs",
            self.base_dir / "exports",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def save_metrics(
        self,
        metrics_dict: Dict[str, Any],
        round_id: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Save metrics for a simulation round.

        Args:
            metrics_dict: Dictionary containing all metrics.
            round_id: Round identifier.
            metadata: Optional metadata to include.

        Returns:
            Path to saved file, or None if save failed.
        """
        try:
            # Add metadata
            save_data = {
                **metrics_dict,
                "metadata": metadata or {},
                "save_timestamp": datetime.now().isoformat(),
            }

            if self.storage_format == "json":
                filepath = self.base_dir / "outputs" / f"round_{round_id}.json"
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                return str(filepath)

            elif self.storage_format == "csv":
                # For CSV, we append to existing files
                self._append_metrics_to_csv(save_data, round_id)
                return str(self.base_dir / "exports")

            else:
                raise ValueError(f"Unsupported storage format: {self.storage_format}")

        except Exception as e:
            print(f"Error saving metrics for round {round_id}: {e}")
            return None

    def _append_metrics_to_csv(self, metrics_dict: Dict[str, Any], round_id: int) -> None:
        """
        Append metrics to CSV files.

        Args:
            metrics_dict: Metrics dictionary.
            round_id: Round identifier.
        """
        exports_dir = self.base_dir / "exports"

        # System metrics CSV
        self._write_csv_row(
            exports_dir / "system_metrics.csv",
            self._get_system_metrics_row(metrics_dict, round_id),
            self._get_system_metrics_headers(),
        )

        # Agent metrics CSV
        agent_metrics = metrics_dict.get("agent_metrics", {})
        for agent_id, agent_data in agent_metrics.items():
            self._write_csv_row(
                exports_dir / "agents_capability.csv",
                self._get_agent_capability_row(agent_data, round_id),
                self._get_agent_capability_headers(),
            )
            self._write_csv_row(
                exports_dir / "agents_moral.csv",
                self._get_agent_moral_row(agent_data, round_id),
                self._get_agent_moral_headers(),
            )
            self._write_csv_row(
                exports_dir / "agents_success.csv",
                self._get_agent_success_row(agent_data, round_id),
                self._get_agent_success_headers(),
            )

    def _write_csv_row(
        self,
        filepath: Path,
        row: Dict[str, Any],
        headers: List[str],
    ) -> None:
        """
        Write a row to CSV file.

        Args:
            filepath: Path to CSV file.
            row: Dictionary of values to write.
            headers: List of headers.
        """
        file_exists = filepath.exists()

        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")

            # Write headers if new file
            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

    def _get_system_metrics_row(self, metrics: Dict[str, Any], round_id: int) -> Dict[str, Any]:
        """Get system metrics row for CSV."""
        system = metrics.get("system_metrics", {})
        return {
            "round": round_id,
            "timestamp": metrics.get("timestamp", ""),
            "pattern_type": metrics.get("pattern_type", ""),
            "agent_count": metrics.get("agent_count", 0),
            "power_concentration": system.get("power_concentration", 0),
            "order_stability": system.get("order_stability", 0),
            "norm_consensus": system.get("norm_consensus", 0),
            "public_goods_level": system.get("public_goods_level", 0),
            "order_type": system.get("order_type", ""),
        }

    def _get_system_metrics_headers(self) -> List[str]:
        """Get system metrics CSV headers."""
        return [
            "round",
            "timestamp",
            "pattern_type",
            "agent_count",
            "power_concentration",
            "order_stability",
            "norm_consensus",
            "public_goods_level",
            "order_type",
        ]

    def _get_agent_capability_row(self, agent_data: Dict[str, Any], round_id: int) -> Dict[str, Any]:
        """Get agent capability row for CSV."""
        cap = agent_data.get("capability_metrics", {})
        hard = cap.get("hard_power_details", {})
        soft = cap.get("soft_power_details", {})
        return {
            "round": round_id,
            "agent_id": agent_data.get("agent_id", ""),
            "name": agent_data.get("name", ""),
            "leadership_type": agent_data.get("leadership_type", ""),
            "hard_power_index": cap.get("hard_power_index", 0),
            "soft_power_index": cap.get("soft_power_index", 0),
            "capability_index": cap.get("capability_index", 0),
            "tier": cap.get("tier", ""),
            "military_capability": hard.get("military_capability", 0),
            "nuclear_capability": hard.get("nuclear_capability", 0),
            "conventional_forces": hard.get("conventional_forces", 0),
            "force_projection": hard.get("force_projection", 0),
            "gdp_share": hard.get("gdp_share", 0),
            "economic_growth": hard.get("economic_growth", 0),
            "trade_volume": hard.get("trade_volume", 0),
            "financial_influence": hard.get("financial_influence", 0),
            "technology_level": hard.get("technology_level", 0),
            "military_technology": hard.get("military_technology", 0),
            "innovation_capacity": hard.get("innovation_capacity", 0),
            "discourse_power": soft.get("discourse_power", 0),
            "narrative_control": soft.get("narrative_control", 0),
            "media_influence": soft.get("media_influence", 0),
            "allies_count": soft.get("allies_count", 0),
            "ally_strength": soft.get("ally_strength", 0),
            "network_position": soft.get("network_position", 0),
            "diplomatic_support": soft.get("diplomatic_support", 0),
            "moral_legitimacy": soft.get("moral_legitimacy", 0),
            "cultural_influence": soft.get("cultural_influence", 0),
            "un_influence": soft.get("un_influence", 0),
            "institutional_leadership": soft.get("institutional_leadership", 0),
        }

    def _get_agent_capability_headers(self) -> List[str]:
        """Get agent capability CSV headers."""
        return [
            "round",
            "agent_id",
            "name",
            "leadership_type",
            "hard_power_index",
            "soft_power_index",
            "capability_index",
            "tier",
            "military_capability",
            "nuclear_capability",
            "conventional_forces",
            "force_projection",
            "gdp_share",
            "economic_growth",
            "trade_volume",
            "financial_influence",
            "technology_level",
            "military_technology",
            "innovation_capacity",
            "discourse_power",
            "narrative_control",
            "media_influence",
            "allies_count",
            "ally_strength",
            "network_position",
            "diplomatic_support",
            "moral_legitimacy",
            "cultural_influence",
            "un_influence",
            "institutional_leadership",
        ]

    def _get_agent_moral_row(self, agent_data: Dict[str, Any], round_id: int) -> Dict[str, Any]:
        """Get agent moral row for CSV."""
        moral = agent_data.get("moral_metrics", {})
        return {
            "round": round_id,
            "agent_id": agent_data.get("agent_id", ""),
            "name": agent_data.get("name", ""),
            "leadership_type": agent_data.get("leadership_type", ""),
            "moral_index": moral.get("moral_index", 0),
            "respect_for_norms": moral.get("respect_for_norms", 0),
            "humanitarian_concern": moral.get("humanitarian_concern", 0),
            "peaceful_resolution": moral.get("peaceful_resolution", 0),
            "international_cooperation": moral.get("international_cooperation", 0),
            "justice_and_fairness": moral.get("justice_and_fairness", 0),
        }

    def _get_agent_moral_headers(self) -> List[str]:
        """Get agent moral CSV headers."""
        return [
            "round",
            "agent_id",
            "name",
            "leadership_type",
            "moral_index",
            "respect_for_norms",
            "humanitarian_concern",
            "peaceful_resolution",
            "international_cooperation",
            "justice_and_fairness",
        ]

    def _get_agent_success_row(self, agent_data: Dict[str, Any], round_id: int) -> Dict[str, Any]:
        """Get agent success row for CSV."""
        success = agent_data.get("success_metrics", {})
        return {
            "round": round_id,
            "agent_id": agent_data.get("agent_id", ""),
            "name": agent_data.get("name", ""),
            "leadership_type": agent_data.get("leadership_type", ""),
            "success_rate": success.get("success_rate", 0),
            "total_actions": success.get("total_actions", 0),
            "successful_actions": success.get("successful_actions", 0),
            "avg_relationship": success.get("avg_relationship", 0),
            "friendly_relations": success.get("friendly_relations", 0),
            "hostile_relations": success.get("hostile_relations", 0),
            "neutral_relations": success.get("neutral_relations", 0),
        }

    def _get_agent_success_headers(self) -> List[str]:
        """Get() agent success CSV headers."""
        return [
            "round",
            "agent_id",
            "name",
            "leadership_type",
            "success_rate",
            "total_actions",
            "successful_actions",
            "avg_relationship",
            "friendly_relations",
            "hostile_relations",
            "neutral_relations",
        ]

    def save_checkpoint(
        self,
        simulation_state: Dict[str, Any],
        checkpoint_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Save a simulation checkpoint.

        Args:
            simulation_state: Full simulation state to save.
            checkpoint_id: Optional checkpoint ID. Auto-generated if not provided.

        Returns:
            Path to saved checkpoint file.
        """
        if checkpoint_id is None:
            checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            filepath = self.base_dir / "checkpoints" / f"{checkpoint_id}.json"
            save_data = {
                "checkpoint_id": checkpoint_id,
                "timestamp": datetime.now().isoformat(),
                "state": simulation_state,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            return str(filepath)

        except Exception as e:
            print(f"Error saving checkpoint {checkpoint_id}: {e}")
            return None

    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a simulation checkpoint.

        Args:
            checkpoint_id: Checkpoint ID (with or without .json extension).

        Returns:
            Checkpoint data dictionary, or None if not found.
        """
        # Add .json extension if not present
        if not checkpoint_id.endswith(".json"):
            checkpoint_id = f"{checkpoint_id}.json"

        filepath = self.base_dir / "checkpoints" / checkpoint_id

        try:
            if not filepath.exists():
                print(f"Checkpoint not found: {filepath}")
                return None

            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            print(f"Error loading checkpoint {checkpoint_id}: {e}")
            return None

    def export_to_csv(
        self,
        data_type: str,
        filepath: str,
        start_round: int = 0,
        end_round: Optional[int] = None,
    ) -> Optional[str]:
        """
        Export metrics to CSV file.

        Args:
            data_type: Type of data to export ("agents_capability", "agents_moral",
                       "agents_success", or "system_metrics").
            filepath: Destination file path.
            start_round: Starting round to include.
            end_round: Ending round to include (inclusive). None for all.

        Returns:
            Path to exported file, or None if export failed.
        """
        source_file = self.base_dir / "exports" / f"{data_type}.csv"

        if not source_file.exists():
            print(f"Source file not found: {source_file}")
            return None

        try:
            # Read source file
            rows = []
            with open(source_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []

                for row in reader:
                    try:
                        round_num = int(row.get("round", 0))
                        if round_num >= start_round:
                            if end_round is None or round_num <= end_round:
                                rows.append(row)
                    except (ValueError, TypeError):
                        # Skip rows with invalid round numbers
                        continue

            # Write destination file
            dest_path = Path(filepath)
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            with open(dest_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)

            return str(dest_path)

        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return None

    def export_time_series(self, metric_name: str, filepath: str) -> Optional[str]:
        """
        Export a specific metric as a time series.

        Args:
            metric_name: Name of metric to export.
            filepath: Destination file path.

        Returns:
            Path to exported file, or None if export failed.
        """
        try:
            # Collect time series data from all round outputs
            time_series = []

            outputs_dir = self.base_dir / "outputs"
            if not outputs_dir.exists():
                print("Outputs directory not found")
                return None

            for json_file in sorted(outputs_dir.glob("round_*.json")):
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    round_num = data.get("round", 0)
                    timestamp = data.get("timestamp", "")

                    # Extract metric value (nested path support)
                    value = self._extract_metric_value(data, metric_name)

                    time_series.append({
                        "round": round_num,
                        "timestamp": timestamp,
                        "metric_name": metric_name,
                        "value": value,
                    })

            # Write to CSV
            dest_path = Path(filepath)
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            with open(dest_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["round", "timestamp", "metric_name", "value"])
                writer.writeheader()
                writer.writerows(time_series)

            return str(dest_path)

        except Exception as e:
            print(f"Error exporting time series: {e}")
            return None

    def _extract_metric_value(self, data: Dict[str, Any], metric_name: str) -> Any:
        """
        Extract a metric value from nested data.

        Args:
            data: Data dictionary.
            metric_name: Metric name (supports dot notation for nested keys).

).

        Returns:
            Metric value, or None if not found.
        """
        keys = metric_name.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value

    def get_latest_checkpoint(self) -> Optional[str]:
        """
        Get most recent checkpoint ID.

        Returns:
            Checkpoint ID (without extension), or None if no checkpoints exist.
        """
        checkpoints_dir = self.base_dir / "checkpoints"

        if not checkpoints_dir.exists():
            return None

        checkpoint_files = list(checkpoints_dir.glob("checkpoint_*.json"))
        if not checkpoint_files:
            return None

        # Get most recent by modification time
        latest = max(checkpoint_files, key=lambda f: f.stat().st_mtime)
        return latest.stem

    def list_checkpoints(self) -> List[str]:
        """
        List all available checkpoints.

        Returns:
            List of checkpoint IDs (without extensions).
        """
        checkpoints_dir = self.base_dir / "checkpoints"

        if not checkpoints_dir.exists():
            return []

        checkpoint_files = sorted(checkpoints_dir.glob("checkpoint_*.json"))
        return [f.stem for f in checkpoint_files]

    def get_round_metrics(self, round_id: int) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific round.

        Args:
            round_id: Round identifier.

        Returns:
            Metrics dictionary, or None if not found.
        """
        filepath = self.base_dir / "outputs" / f"round_{round_id}.json"

        try:
            if not filepath.exists():
                return None

            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            print(f"Error loading metrics for round {round_id}: {e}")
            return None

    def get_agent_history(
        self,
        agent_id: str,
        metric_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get metric history for a specific agent.

        Args:
            agent_id: Agent identifier.
            metric_type: Optional filter for specific metric type ("capability",
                        "moral", "success", or None for all).

        Returns:
            List of metric entries for agent.
        """
        history = []
        outputs_dir = self.base_dir / "outputs"

        if not outputs_dir.exists():
            return []

        for json_file in sorted(outputs_dir.glob("round_*.json")):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                round_num = data.get("round", 0)
                agent_metrics = data.get("agent_metrics", {})

                if agent_id not in agent_metrics:
                    continue

                agent_data = agent_metrics[agent_id]

                if metric_type is None:
                    history.append({
                        "round": round_num,
                        "timestamp": data.get("timestamp", ""),
                        "agent_id": agent_id,
                        "data": agent_data,
                    })
                elif metric_type == "capability":
                    history.append({
                        "round": round_num,
                        "timestamp": data.get("timestamp", ""),
                        "agent_id": agent_id,
                        **agent_data.get("capability_metrics", {}),
                    })
                elif metric_type == "moral":
                    history.append({
                        "round": round_num,
                        "timestamp": data.get("timestamp", ""),
                        "agent_id": agent_id,
                        **agent_data.get("moral_metrics", {}),
                    })
                elif metric_type == "success":
                    history.append({
                        "round": round_num,
                        "timestamp": data.get("timestamp", ""),
                        "agent_id": agent_id,
                        **agent_data.get("success_metrics", {}),
                    })

        return history

    def get_system_trends(
        self,
        start_round: int,
        end_round: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get system-level metric trends over rounds.

        Args:
            start_round: Starting round.
            end_round: Ending round (inclusive). None for all from start.

        Returns:
            Dictionary mapping metric names to trend data.
        """
        trends = {
            "power_concentration": [],
            "order_stability": [],
            "norm_consensus": [],
            "public_goods_level": [],
            "order_type": [],
        }

        outputs_dir = self.base_dir / "outputs"

        if not outputs_dir.exists():
            return trends

        for json_file in sorted(outputs_dir.glob("round_*.json")):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                round_num = data.get("round", 0)

                if round_num < start_round:
                    continue
                if end_round is not None and round_num > end_round:
                    continue

                system = data.get("system_metrics", {})
                trends["power_concentration"].append({
                    "round": round_num,
                    "value": system.get("power_concentration", 0),
                })
                trends["order_stability"].append({
                    "round": round_num,
                    "value": system.get("order_stability", 0),
                })
                trends["norm_consensus"].append({
                    "round": round_num,
                    "value": system.get("norm_consensus", 0),
                })
                trends["public_goods_level"].append({
                    "round": round_num,
                    "value": system.get("public_goods_level", 0),
                })
                trends["order_type"].append({
                    "round": round_num,
                    "value": system.get("order_type", ""),
                })

        return trends

    def clear_outputs(self) -> None:
        """Clear all output files (but keep checkpoints)."""
        outputs_dir = self.base_dir / "outputs"
        exports_dir = self.base_dir / "exports"

        for directory in [outputs_dir, exports_dir]:
            if directory.exists():
                for file in directory.glob("*"):
                    try:
                        if file.is_file():
                            file.unlink()
                    except Exception as e:
                        print(f"Error deleting {file}: {e}")
