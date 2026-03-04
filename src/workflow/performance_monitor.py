"""
Performance monitor for moral realism ABM system.

This module provides PerformanceMonitor class which tracks
timing statistics, memory usage, and resource utilization
during simulation execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import time
import logging
import platform
import psutil

logger = logging.getLogger(__name__)


@dataclass
class RoundTiming:
    """Timing information for a single simulation round."""

    round_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None

    # Phase timings (in seconds)
    event_generation_time: float = 0.0
    event_distribution_time: float = 0.0
    decision_making_time: float = 0.0
    interaction_execution_time: float = 0.0
    rule_application_time: float = 0.0
    metrics_calculation_time: float = 0.0

    # Agent decision times
    agent_decision_times: Dict[str, float] = field(default_factory=dict)

    # Memory at start and end (in MB)
    memory_start_mb: Optional[float] = None
    memory_end_mb: Optional[float] = None
    memory_peak_mb: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert timing to dictionary."""
        return {
            "round_number": self.round_number,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration": self.total_duration,
            "event_generation_time": self.event_generation_time,
            "event_distribution_time": self.event_distribution_time,
            "decision_making_time": self.decision_making_time,
            "interaction_execution_time": self.interaction_execution_time,
            "rule_application_time": self.rule_application_time,
            "metrics_calculation_time": self.metrics_calculation_time,
            "agent_decision_times": self.agent_decision_times,
            "memory_start_mb": self.memory_start_mb,
            "memory_end_mb": self.memory_end_mb,
            "memory_peak_mb": self.memory_peak_mb,
        }


@dataclass
class PerformanceStats:
    """Summary statistics for simulation performance."""

    total_rounds: int = 0
    total_time: float = 0.0
    avg_round_time: float = 0.0
    min_round_time: Optional[float] = None
    max_round_time: Optional[float] = None

    # Phase statistics
    avg_event_generation_time: float = 0.0
    avg_event_distribution_time: float = 0.0
    avg_decision_making_time: float = 0.0
    avg_interaction_execution_time: float = 0.0
    avg_rule_application_time: float = 0.0
    avg_metrics_calculation_time: float = 0.0

    # Memory statistics
    memory_usage_mb: float = 0.0
    peak_memory_mb: float = 0.0
    avg_memory_usage_mb: float = 0.0

    # System info
    platform_info: str = ""
    python_version: str = ""

    # Timing breakdown by percentage
    timing_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_rounds": self.total_rounds,
            "total_time": round(self.total_time, 3),
            "avg_round_time": round(self.avg_round_time, 3),
            "min_round_time": round(self.min_round_time, 3)
            if self.min_round_time else None,
            "max_round_time": round(self.max_round_time, 3)
            if self.max_round_time else None,
            "avg_event_generation_time": round(self.avg_event_generation_time, 3),
            "avg_event_distribution_time": round(self.avg_event_distribution_time, 3),
            "avg_decision_making_time": round(self.avg_decision_making_time, 3),
            "avg_interaction_execution_time": round(
                self.avg_interaction_execution_time, 3
            ),
            "avg_rule_application_time": round(self.avg_rule_application_time, 3),
            "avg_metrics_calculation_time": round(self.avg_metrics_calculation_time, 3),
            "memory_usage_mb": round(self.memory_usage_mb, 2),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "avg_memory_usage_mb": round(self.avg_memory_usage_mb, 2),
            "platform_info": self.platform_info,
            "python_version": self.python_version,
            "timing_breakdown": self.timing_breakdown,
        }


class PerformanceMonitor:
    """
    Monitor and track simulation performance metrics.

    Tracks:
    - Round execution times
    - Phase-level timing (event generation, decisions, interactions, etc.)
    - Memory usage over time
    - System resource utilization
    """

    def __init__(
        self,
        enable_memory_tracking: bool = True,
        track_agent_times: bool = True,
    ) -> None:
        """
        Initialize performance monitor.

        Args:
            enable_memory_tracking: Whether to track memory usage.
            track_agent_times: Whether to track individual agent times.
        """
        self._enable_memory_tracking = enable_memory_tracking
        self._track_agent_times = track_agent_times

        self._round_timings: List[RoundTiming] = []
        self._current_round: Optional[RoundTiming] = None
        self._phase_timer: Optional[float] = None

        # Accumulated phase times for current round
        self._current_phase_times: Dict[str, float] = {}

        # System info
        self._platform_info = self._get_platform_info()

    def start_round(self, round_number: int) -> None:
        """
        Start timing a new round.

        Args:
            round_number: The round number.
        """
        if self._current_round is not None:
            logger.warning(
                f"Starting round {round_number} while round "
                f"{self._current_round.round_number} is still active"
            )

        self._current_round = RoundTiming(
            round_number=round_number,
            start_time=datetime.now(),
        )

        # Capture initial memory
        if self._enable_memory_tracking:
            self._current_round.memory_start_mb = self._get_memory_usage()

        self._current_phase_times = {}

        logger.debug(f"Started timing for round {round_number}")

    def end_round(self) -> Optional[RoundTiming]:
        """
        End timing for current round.

        Returns:
            The completed round timing, or None if no round was active.
        """
        if self._current_round is None:
            logger.warning("Attempting to end round with no active round")
            return None

        self._current_round.end_time = datetime.now()
        self._current_round.total_duration = (
            self._current_round.end_time - self._current_round.start_time
        ).total_seconds()

        # Capture final memory
        if self._enable_memory_tracking:
            self._current_round.memory_end_mb = self._get_memory_usage()

        # Store timing
        self._round_timings.append(self._current_round)

        logger.debug(
            f"Round {self._current_round.round_number} completed in "
            f"{self._current_round.total_duration:.3f}s"
        )

        completed_round = self._current_round
        self._current_round = None

        return completed_round

    def start_phase(self, phase_name: str) -> None:
        """
        Start timing a specific phase within a round.

        Args:
            phase_name: Name of the phase (e.g., "event_generation").
        """
        self._phase_timer = time.time()
        logger.debug(f"Started phase: {phase_name}")

    def end_phase(self, phase_name: str) -> None:
        """
        End timing for a specific phase.

        Args:
            phase_name: Name of the phase.
        """
        if self._phase_timer is None:
            logger.warning(f"Ending phase {phase_name} with no active phase timer")
            return

        duration = time.time() - self._phase_timer
        self._current_round.memory_peak_mb = (
            max(
                self._current_round.memory_peak_mb or 0.0,
                self._get_memory_usage(),
            )
            if self._enable_memory_tracking
            else None
        )

        # Record phase time to current round
        if self._current_round is not None:
            phase_attribute = f"{phase_name}_time"
            if hasattr(self._current_round, phase_attribute):
                setattr(self._current_round, phase_attribute, duration)

        self._current_phase_times[phase_name] = duration
        self._phase_timer = None

        logger.debug(f"Ended phase {phase_name}: {duration:.3f}s")

    def record_agent_decision_time(self, agent_id: str, duration: float) -> None:
        """
        Record timing for a single agent's decision.

        Args:
            agent_id: The agent ID.
            duration: Decision time in seconds.
        """
        if self._current_round is not None and self._track_agent_times:
            self._current_round.agent_decision_times[agent_id] = duration

    def get_current_round_timing(self) -> Optional[RoundTiming]:
        """
        Get timing for current round (in-progress).

        Returns:
            Current round timing, or None if no round is active.
        """
        return self._current_round

    def get_round_timing(self, round_number: int) -> Optional[RoundTiming]:
        """
        Get timing for a specific completed round.

        Args:
            round_number: The round number.

        Returns:
            RoundTiming if found, None otherwise.
        """
        for timing in self._round_timings:
            if timing.round_number == round_number:
                return timing
        return None

    def get_stats(self) -> PerformanceStats:
        """
        Get performance statistics summary.

        Returns:
            PerformanceStats with aggregated statistics.
        """
        if not self._round_timings:
            return PerformanceStats(
                platform_info=self._platform_info,
                python_version=self._get_python_version(),
            )

        # Calculate timing statistics
        total_rounds = len(self._round_timings)
        total_time = sum(t.total_duration for t in self._round_timings)
        avg_round_time = total_time / total_rounds
        round_times = [t.total_duration for t in self._round_timings]
        min_round_time = min(round_times)
        max_round_time = max(round_times)

        # Calculate phase averages
        avg_event_gen = self._avg_phase("event_generation_time")
        avg_event_dist = self._avg_phase("event_distribution_time")
        avg_decision = self._avg_phase("decision_making_time")
        avg_interaction = self._avg_phase("interaction_execution_time")
        avg_rule = self._avg_phase("rule_application_time")
        avg_metrics = self._avg_phase("metrics_calculation_time")

        # Calculate memory statistics
        memory_values = [
            t.memory_end_mb for t in self._round_timings
            if t.memory_end_mb is not None
        ]
        memory_usage = memory_values[-1] if memory_values else 0.0
        peak_memory = max(memory_values) if memory_values else 0.0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0.0

        # Calculate timing breakdown
        if total_time > 0:
            breakdown = {
                "event_generation": avg_event_gen / avg_round_time * 100,
                "event_distribution": avg_event_dist / avg_round_time * 100,
                "decision_making": avg_decision / avg_round_time * 100,
                "interaction_execution": avg_interaction / avg_round_time * 100,
                "rule_application": avg_rule / avg_round_time * 100,
                "metrics_calculation": avg_metrics / avg_round_time * 100,
            }
        else:
            breakdown = {}

        return PerformanceStats(
            total_rounds=total_rounds,
            total_time=total_time,
            avg_round_time=avg_round_time,
            min_round_time=min_round_time,
            max_round_time=max_round_time,
            avg_event_generation_time=avg_event_gen,
            avg_event_distribution_time=avg_event_dist,
            avg_decision_making_time=avg_decision,
            avg_interaction_execution_time=avg_interaction,
            avg_rule_application_time=avg_rule,
            avg_metrics_calculation_time=avg_metrics,
            memory_usage_mb=memory_usage,
            peak_memory_mb=peak_memory,
            avg_memory_usage_mb=avg_memory,
            platform_info=self._platform_info,
            python_version=self._get_python_version(),
            timing_breakdown=breakdown,
        )

    def get_timing_summary(self, n_rounds: int = 10) -> List[Dict[str, Any]]:
        """
        Get timing summary for recent rounds.

        Args:
            n_rounds: Number of recent rounds to include.

        Returns:
            List of timing dictionaries.
        """
        recent = self._round_timings[-n_rounds:]
        return [t.to_dict() for t in reversed(recent)]

    def log_summary(self, level: str = "INFO") -> None:
        """
        Log performance summary.

        Args:
            level: Logging level (INFO, DEBUG, WARNING).
        """
        stats = self.get_stats()
        summary = (
            f"\n=== Performance Summary ===\n"
            f"Total rounds: {stats.total_rounds}\n"
            f"Total time: {stats.total_time:.2f}s\n"
            f"Average round time: {stats.avg_round_time:.3f}s\n"
            f"Min/Max round time: {stats.min_round_time:.3f}s / "
            f"{stats.max_round_time:.3f}s\n"
            f"Memory usage: {stats.memory_usage_mb:.2f} MB "
            f"(peak: {stats.peak_memory_mb:.2f} MB)\n"
            f"Platform: {stats.platform_info}\n"
        )

        log_func = getattr(logger, level.lower(), logger.info)
        log_func(summary)

        if stats.timing_breakdown:
            breakdown = "Timing breakdown:\n"
            for phase, percentage in stats.timing_breakdown.items():
                breakdown += f"  {phase}: {percentage:.1f}%\n"
            log_func(breakdown)

    def reset(self) -> None:
        """Reset all performance tracking."""
        self._round_timings.clear()
        self._current_round = None
        self._phase_timer = None
        self._current_phase_times.clear()
        logger.info("Performance monitor reset")

    def get_memory_usage_mb(self) -> float:
        """
        Get current memory usage in MB.

        Returns:
            Memory usage in megabytes, or 0 if tracking disabled.
        """
        if not self._enable_memory_tracking:
            return 0.0
        return self._get_memory_usage()

    # Private helper methods

    def _avg_phase(self, phase_attribute: str) -> float:
        """Calculate average time for a phase."""
        values = []
        for timing in self._round_timings:
            if hasattr(timing, phase_attribute):
                value = getattr(timing, phase_attribute)
                values.append(value)
        return sum(values) / len(values) if values else 0.0

    def _get_memory_usage(self) -> float:
        """Get current process memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            # Fallback if psutil unavailable
            return 0.0

    def _get_platform_info(self) -> str:
        """Get platform information string."""
        return f"{platform.system()} {platform.release()}"

    def _get_python_version(self) -> str:
        """Get Python version string."""
        return platform.python_version()
