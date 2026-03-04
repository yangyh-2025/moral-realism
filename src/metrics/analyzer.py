"""
Metrics analyzer for moral realism ABM system.

This module provides MetricsAnalyzer for analyzing trends,
detecting patterns, and computing correlations in metric data.
"""

import math
import statistics
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.models.capability import CapabilityTier


@dataclass
class TrendAnalysis:
    """Result of trend analysis."""

    metric_name: str
    start_round: int
    end_round: int
    start_value: float
    end_value: float
    direction: str  # "increasing", "decreasing", "stable", "volatile"
    magnitude: float
    significance: str  # "high", "medium", "low"
    confidence: float
    rate_of_change: float  # Change per round
    std_dev: float  # Standard deviation

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "start_round": self.start_round,
            "end_round": self.end_round,
            "start_value": self.start_value,
            "end_value": self.end_value,
            "direction": self.direction,
            "magnitude": self.magnitude,
            "significance": self.significance,
            "confidence": self.confidence,
            "rate_of_change": self.rate_of_change,
            "std_dev": self.std_dev,
        }


@dataclass
class PowerTransition:
    """Detected power transition between capability tiers."""

    transition_type: str  # "rise", "decline", "overtake"
    agent_id: str
    from_tier: str
    to_tier: str
    round: int
    significance: float  # 0-1 scale

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transition_type": self.transition_type,
            "agent_id": self.agent_id,
            "from_tier": self.from_tier,
            "to_tier": self.to_tier,
            "round": self.round,
            "significance": self.significance,
        }


class MetricsAnalyzer:
    """
    Analyze metrics data for trends and patterns.

    Provides methods for trend analysis, power transition detection,
    correlation calculation, and summary statistics.
    """

    def __init__(self) -> None:
        """Initialize metrics analyzer."""
        self._threshold_volatile = 15.0  # Threshold for volatile classification
        self._threshold_significant = 5.0  # Threshold for significant change

    def analyze_capability_trends(
        self,
        agent_history: List[Dict[str, Any]],
        start_round: int,
        end_round: int,
    ) -> TrendAnalysis:
        """
        Analyze capability index trends for an agent.

        Args:
            agent_history: Agent metric history from storage.
            start_round: Starting round for analysis.
            end_round: Ending round for analysis.

        Returns:
            TrendAnalysis instance.
        """
        # Extract capability index values
        values = self._extract_metric_values(
            agent_history,
            "capability_index",
            start_round,
            end_round,
        )

        if len(values) < 2:
            # Not enough data points
            return TrendAnalysis(
                metric_name="capability_index",
                start_round=start_round,
                end_round=end_round,
                start_value=values[0] if values else 0.0,
                end_value=values[-1] if values else 0.0,
                direction="stable",
                magnitude=0.0,
                significance="low",
                confidence=0.0,
                rate_of_change=0.0,
                std_dev=0.0,
            )

        start_value = values[0]
        end_value = values[-1]

        # Calculate trend direction and magnitude
        direction, magnitude = self._determine_trend(values)

        # Determine significance
        if len(values) > 1:
            calculated_std_dev = statistics.stdev(values)
        else:
            calculated_std_dev = 0.0
        significance = self._determine_significance(magnitude, calculated_std_dev)

        # Calculate rate of change
        rounds = len(values)
        rate_of_change = (end_value - start_value) / rounds if rounds > 1 else 0.0

        # Confidence based on data points
        confidence = min(1.0, len(values) / 10.0)

        return TrendAnalysis(
            metric_name="capability_index",
            start_round=start_round,
            end_round=end_round,
            start_value=start_value,
            end_value=end_value,
            direction=direction,
            magnitude=magnitude,
            significance=significance,
            confidence=confidence,
            rate_of_change=rate_of_change,
            std_dev=statistics.stdev(values) if len(values) > 1 else 0.0,
        )

    def analyze_moral_trends(
        self,
        agent_history: List[Dict[str, Any]],
        start_round: int,
        end_round: int,
    ) -> TrendAnalysis:
        """
        Analyze moral index trends for an agent.

        Args:
            agent_history: Agent metric history from storage.
            start_round: Starting round for analysis.
            end_round: Ending round for analysis.

        Returns:
            TrendAnalysis instance.
        """
        # Extract moral index values
        values = self._extract_metric_values(
            agent_history,
            "moral_index",
            start_round,
            end_round,
        )

        if len(values) < 2:
            return TrendAnalysis(
                metric_name="moral_index",
                start_round=start_round,
                end_round=end_round,
                start_value=values[0] if values else 0.0,
                end_value=values[-1] if values else 0.0,
                direction="stable",
                magnitude=0.0,
                significance="low",
                confidence=0.0,
                rate_of_change=0.0,
                std_dev=0.0,
            )

        start_value = values[0]
        end_value = values[-1]

        direction, magnitude = self._determine_trend(values)
        if len(values) > 1:
            calculated_std_dev = statistics.stdev(values)
        else:
            calculated_std_dev = 0.0
        significance = self._determine_significance(magnitude, calculated_std_dev)

        rounds = len(values)
        rate_of_change = (end_value - start_value) / rounds if rounds > 1 else 0.0
        confidence = min(1.0, len(values) / 10.0)

        return TrendAnalysis(
            metric_name="moral_index",
            start_round=start_round,
            end_round=end_round,
            start_value=start_value,
            end_value=end_value,
            direction=direction,
            magnitude=magnitude,
            significance=significance,
            confidence=confidence,
            rate_of_change=rate_of_change,
            std_dev=statistics.stdev(values) if len(values) > 1 else 0.0,
        )

    def detect_power_transitions(
        self,
        agent_history: List[Dict[str, Any]],
        start_round: int,
        end_round: int,
    ) -> List[PowerTransition]:
        """
        Detect power tier transitions for an agent.

        Args:
            agent_history: Agent metric history from storage.
            start_round: Starting round to search.
            end_round: Ending round to search.

        Returns:
            List of PowerTransition instances.
        """
        transitions = []

        # Track previous tier
        prev_tier = None
        prev_round = None

        for entry in agent_history:
            round_num = entry.get("round", 0)
            if round_num < start_round or round_num > end_round:
                continue

            # Get tier - either from capability_metrics or data sub-dict
            tier = entry.get("tier")
            if tier is None:
                data = entry.get("data", {})
                if isinstance(data, dict):
                    cap_metrics = data.get("capability_metrics", {})
                    tier = cap_metrics.get("tier")

            if tier is None:
                continue

            if prev_tier is not None and tier != prev_tier:
                # Tier transition detected
                transition_type = self._determine_transition_type(
                    prev_tier, tier
                )

                # Calculate significance based on tier difference
                significance = self._calculate_transition_significance(
                    prev_tier, tier
                )

                agent_id = entry.get("agent_id", "unknown")

                transitions.append(
                    PowerTransition(
                        transition_type=transition_type,
                        agent_id=agent_id,
                        from_tier=prev_tier,
                        to_tier=tier,
                        round=round_num,
                        significance=significance,
                    )
                )

            prev_tier = tier
            prev_round = round_num

        return transitions

    def _determine_transition_type(self, from_tier: str, to_tier: str) -> str:
        """
        Determine the type of tier transition.

        Args:
            from_tier: Original tier.
            to_tier: New tier.

        Returns:
            Transition type: "rise", "decline", or "overtake".
        """
        tier_order = [
            CapabilityTier.T4_SMALL.value,
            CapabilityTier.T3_MEDIUM.value,
            CapabilityTier.T2_REGIONAL.value,
            CapabilityTier.T1_GREAT_POWER.value,
            CapabilityTier.T0_SUPERPOWER.value,
        ]

        try:
            from_idx = tier_order.index(from_tier)
            to_idx = tier_order.index(to_tier)

            if to_idx > from_idx:
                return "rise"
            elif to_idx < from_idx:
                return "decline"
            else:
                return "overtake"  # Same tier level

        except ValueError:
            # Unknown tier
            return "overtake"

    def _calculate_transition_significance(self, from_tier: str, to_tier: str) -> float:
        """
        Calculate significance of tier transition.

        Args:
            from_tier: Original tier.
            to_tier: New tier.

        Returns:
            Significance score (0-1).
        """
        tier_order = [
            CapabilityTier.T4_SMALL.value,
            CapabilityTier.T3_MEDIUM.value,
            CapabilityTier.T2_REGIONAL.value,
            CapabilityTier.T1_GREAT_POWER.value,
            CapabilityTier.T0_SUPERPOWER.value,
        ]

        try:
            from_idx = tier_order.index(from_tier)
            to_idx = tier_order.index(to_tier)

            # Larger tier jumps are more significant
            difference = abs(to_idx - from_idx)
            significance = min(1.0, difference / 4.0)

            return significance

        except ValueError:
            return 0.5

    def analyze_order_evolution(
        self,
        system_trends: Dict[str, List[Dict[str, Any]]],
        start_round: int,
        end_round: int,
    ) -> Dict[str, Any]:
        """
        Analyze international order evolution over time.

        Args:
            system_trends: System trends from storage.
            start_round: Starting round.
            end_round: Ending round.

        Returns:
            Dictionary with order evolution analysis.
        """
        # Extract order type sequence
        order_type_data = system_trends.get("order_type", [])
        order_sequence = [
            d["value"] for d in order_type_data
            if start_round <= d.get("round", 0) <= end_round
        ]

        # Count occurrences of each order type
        order_counts = {}
        for order_type in order_sequence:
            order_counts[order_type] = order_counts.get(order_type, 0) + 1

        # Count transitions
        transitions = 0
        for i in range(len(order_sequence) - 1):
            if order_sequence[i] != order_sequence[i + 1]:
                transitions += 1

        # Determine dominant order type
        dominant_order = None
        max_count = 0
        for order_type, count in order_counts.items():
            if count > max_count:
                max_count = count
                dominant_order = order_type

        # Calculate stability (low transitions = stable)
        total_rounds = len(order_sequence)
        transition_rate = transitions / total_rounds if total_rounds > 1 else 0
        stability_score = 1.0 - transition_rate

        return {
            "start_round": start_round,
            "end_round": end_round,
            "total_rounds": total_rounds,
            "order_type_counts": order_counts,
            "dominant_order": dominant_order,
            "transitions": transitions,
            "transition_rate": transition_rate,
            "stability_score": stability_score,
            "order_sequence": order_sequence,
        }

    def compare_leadership_types(
        self,
        metrics_by_leadership: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Compare metrics across different leadership types.

        Args:
            metrics_by_leadership: Dictionary mapping leadership types to
                                    agent metric lists.

        Returns:
            Dictionary with comparison results.
        """
        comparison = {}

        for leadership_type, agent_metrics in metrics_by_leadership.items():
            if not agent_metrics:
                continue

            # Calculate averages for key metrics
            capability_values = []
            moral_values = []
            success_rates = []

            for metrics in agent_metrics:
                capability = metrics.get("capability_index", 0)
                moral = metrics.get("moral_index", 0)

                if capability:
                    capability_values.append(capability)
                if moral:
                    moral_values.append(moral)

                success = metrics.get("success_rate", 0)
                if success:
                    success_rates.append(success)

            comparison[leadership_type] = {
                "agent_count": len(agent_metrics),
                "avg_capability": (
                    statistics.mean(capability_values) if capability_values else 0
                ),
                "avg_moral_index": (
                    statistics.mean(moral_values) if moral_values else 0
                ),
                "avg_success_rate": (
                    statistics.mean(success_rates) if success_rates else 0
                ),
                "capability_std_dev": (
                    statistics.stdev(capability_values) if len(capability_values) > 1 else 0
                ),
                "moral_std_dev": (
                    statistics.stdev(moral_values) if len(moral_values) > 1 else 0
                ),
            }

        return comparison

    def calculate_correlation(
        self,
        metric1_values: List[float],
        metric2_values: List[float],
    ) -> float:
        """
        Calculate Pearson correlation coefficient between two metrics.

        Args:
            metric1_values: Values from first metric.
            metric2_values: Values from second metric.

        Returns:
            Correlation coefficient (-1 to 1).
        """
        if len(metric1_values) != len(metric2_values):
            raise ValueError("Metric value lists must have same length")

        if len(metric1_values) < 2:
            return 0.0

        try:
            # Remove any None or NaN values
            pairs = [(x, y) for x, y in zip(metric1_values, metric2_values) if x is not None and y is not None]

            if len(pairs) < 2:
                return 0.0

            x_values = [x for x, _ in pairs]
            y_values = [y for _, y in pairs]

            # Calculate means
            mean_x = statistics.mean(x_values)
            mean_y = statistics.mean(y_values)

            # Calculate covariance and standard deviations
            n = len(pairs)
            covariance = sum((x - mean_x) * (y - mean_y) for x, y in pairs) / n
            std_x = math.sqrt(sum((x - mean_x) ** 2 for x in x_values) / n) if n > 0 else 0
            std_y = math.sqrt(sum((y - mean_y) ** 2 for y in y_values) / n) if n > 0 else 0

            # Correlation
            if std_x * std_y == 0:
                return 0.0

            return covariance / (std_x * std_y)

        except (statistics.StatisticsError, ZeroDivisionError):
            return 0.0

    def predict_trend(
        self,
        metric_name: str,
        current_history: List[Dict[str, Any]],
        lookahead: int = 5,
    ) -> Dict[str, Any]:
        """
        Predict future trend based on historical data.

        Args:
            metric_name: Name of metric to predict.
            current_history: Historical metric values.
            lookahead: Number of rounds to predict.

        Returns:
            Dictionary with prediction results.
        """
        # Extract values
        values = [d.get("value", 0) for d in current_history if "value" in d]

        if len(values) < 3:
            # Not enough data for prediction
            return {
                "metric_name": metric_name,
                "lookahead": lookahead,
                "predicted_values": [values[-1]] * lookahead if values else [0] * lookahead,
                "confidence": 0.0,
                "method": "insufficient_data",
            }

        # Simple linear trend prediction
        # Use last few values to determine trend
        recent_values = values[-min(10, len(values)):]
        slope = self._calculate_slope(recent_values)
        last_value = values[-1]

        # Predict future values
        predicted_values = []
        for i in range(1, lookahead + 1):
            predicted = last_value + (slope * i)
            predicted_values.append(max(0.0, min(100.0, predicted)))  # Clamp to 0-100

        # Confidence based on stability of recent values
        std_dev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
        confidence = max(0.0, min(1.0, 1.0 - (std_dev / 50.0)))

        return {
            "metric_name": metric_name,
            "lookahead": lookahead,
            "predicted_values": predicted_values,
            "confidence": confidence,
            "method": "linear_trend",
            "trend_slope": slope,
            "base_value": last_value,
        }

    def _calculate_slope(self, values: List[float]) -> float:
        """
        Calculate linear trend slope from values.

        Args:
            values: List of numeric values.

        Returns:
            Slope (change per unit).
        """
        if len(values) < 2:
            return 0.0

        try:
            # Simple linear regression: y = mx + b
            n = len(values)
            x_values = list(range(n))

            sum_x = sum(x_values)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(x_values, values))
            sum_x2 = sum(x * x for x in x_values)

            # Calculate slope (m)
            denominator = n * sum_x2 - sum_x ** 2
            if denominator == 0:
                return 0.0

            slope = (n * sum_xy - sum_x * sum_y) / denominator
            return slope

        except (ZeroDivisionError, ValueError):
            return 0.0

    def get_summary_statistics(
        self,
        values: List[float],
    ) -> Dict[str, float]:
        """
        Calculate summary statistics for a set of values.

        Args:
            values: List of numeric values.

        Returns:
            Dictionary with statistics.
        """
        if not values:
            return {
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "range": 0.0,
            }

        try:
            return {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values),
                "range": max(values) - min(values),
            }
        except statistics.StatisticsError:
            return {
                "count": len(values),
                "mean": sum(values) / len(values),
                "median": 0.0,
                "std_dev": 0.0,
                "min": min(values),
                "max": max(values),
                "range": max(values) - min(values),
            }

    def identify_critical_events(
        self,
        metrics_history: List[Dict[str, Any]],
        threshold: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """
        Identify critical events (significant metric changes).

        Args:
            metrics_history: Historical metrics data.
            threshold: Standard deviation multiplier for event detection.

        Returns:
            List of critical events with metadata.
        """
        critical_events = []

        # Analyze system metrics
        power_conc_values = []
        order_stability_values = []
        norm_consensus_values = []

        for entry in metrics_history:
            system = entry.get("system_metrics", {})
            if system:
                power_conc_values.append(system.get("power_concentration", 0))
                order_stability_values.append(system.get("order_stability", 0))
                norm_consensus_values.append(system.get("norm_consensus", 0))

        # Detect significant changes
        if len(power_conc_values) > 1:
            power_events = self._detect_significant_changes(
                "power_concentration",
                power_conc_values,
                threshold,
            )
            critical_events.extend(power_events)

        if len(order_stability_values) > 1:
            stability_events = self._detect_significant_changes(
                "order_stability",
                order_stability_values,
                threshold,
            )
            critical_events.extend(stability_events)

        if len(norm_consensus_values) > 1:
            norm_events = self._detect_significant_changes(
                "norm_consensus",
                norm_consensus_values,
                threshold,
            )
            critical_events.extend(norm_events)

        return critical_events

    def _detect_significant_changes(
        self,
        metric_name: str,
        values: List[float],
        threshold: float,
    ) -> List[Dict[str, Any]]:
        """
        Detect statistically significant changes in a metric series.

        Args:
            metric_name: Name of the metric.
            values: List of metric values.
            threshold: Standard deviation multiplier.

        Returns:
            List of change events.
        """
        events = []

        if len(values) < 3:
            return events

        # Calculate mean and standard deviation
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        if std_dev == 0:
            return events

        # Detect values that deviate significantly from mean
        for i, value in enumerate(values):
            z_score = abs(value - mean_val) / std_dev

            if z_score >= threshold:
                events.append({
                    "round": i,
                    "metric_name": metric_name,
                    "value": value,
                    "mean": mean_val,
                    "z_score": z_score,
                    "change_type": "increase" if value > mean_val else "decrease",
                })

        return events

    def _extract_metric_values(
        self,
        history: List[Dict[str, Any]],
        metric_name: str,
        start_round: int,
        end_round: int,
    ) -> List[float]:
        """
        Extract metric values for specified round range.

        Args:
            history: Historical metric data.
            metric_name: Name of metric to extract.
            start_round: Starting round.
            end_round: Ending round.

        Returns:
            List of metric values in order.
        """
        values = []

        for entry in history:
            round_num = entry.get("round", 0)
            if round_num < start_round or round_num > end_round:
                continue

            # Try to get value from entry or nested data
            value = entry.get(metric_name)
            if value is None:
                data = entry.get("data", {})
                if isinstance(data, dict) and metric_name in data:
                    value = data[metric_name]
                else:
                    # Try capability_metrics or moral_metrics
                    cap_metrics = data.get("capability_metrics", {}) if isinstance(data, dict) else {}
                    moral_metrics = data.get("moral_metrics", {}) if isinstance(data, dict) else {}

                    if metric_name in cap_metrics:
                        value = cap_metrics[metric_name]
                    elif metric_name in moral_metrics:
                        value = moral_metrics[metric_name]

            if value is not None and isinstance(value, (int, float)):
                values.append(float(value))

        return values

    def _determine_trend(self, values: List[float]) -> tuple:
        """
        Determine trend direction and magnitude.

        Args:
            values: List of metric values.

        Returns:
            Tuple of (direction, magnitude).
        """
        if len(values) < 2:
            return "stable", 0.0

        start_value = values[0]
        end_value = values[-1]
        magnitude = end_value - start_value

        # Calculate volatility (standard deviation)
        if len(values) > 1:
            std_dev = statistics.stdev(values)
        else:
            std_dev = 0.0

        # Determine direction based on magnitude and volatility
        if std_dev > self._threshold_volatile:
            return "volatile", magnitude

        if abs(magnitude) < self._threshold_significant:
            return "stable", magnitude

        if magnitude > 0:
            return "increasing", magnitude
        else:
            return "decreasing", magnitude

    def _determine_significance(self, magnitude: float, std_dev: float) -> str:
        """
        Determine significance level of a change.

        Args:
            magnitude: Magnitude of change.
            std_dev: Standard deviation of values.

        Returns:
            Significance level: "high", "medium", or "low".
        """
        # Use normalized change (magnitude relative to std_dev)
        if std_dev == 0:
            normalized_change = abs(magnitude)
        else:
            normalized_change = abs(magnitude) / std_dev

        if normalized_change > 2.0:
            return "high"
        elif normalized_change > 1.0:
            return "medium"
        else:
            return "low"
