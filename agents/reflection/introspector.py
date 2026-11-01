"""
agents.reflection.introspector
==============================
Introspection and Retrospective Learning Loop.
Course: AI373TA — Unit II & CO2 (Reflection, Introspection & Evaluative Learning).

Academic Role:
Validates whether past autonomous agent actions achieved their intended cyber-physical
objective. Evaluates before vs. after streaming metrics, assigns an empirical outcome
score, and records lessons learned into Episodic Memory.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from agents.memory.episodic import Episode, EpisodicMemory
from agents.memory.short_term import WorkingMemory

logger = logging.getLogger("agents.reflection")


class Introspector:
    """Evaluates agent intervention effectiveness against subsequent stream metrics."""

    def __init__(
        self,
        working_memory: WorkingMemory,
        episodic_memory: EpisodicMemory,
        success_occupancy_reduction_pct: float = 4.0,
        deceleration_velocity_threshold: float = 3.0,
    ) -> None:
        self.wm = working_memory
        self.em = episodic_memory
        self.min_reduction = success_occupancy_reduction_pct
        self.min_decel = deceleration_velocity_threshold

    def evaluate_pending_episodes(self) -> List[Dict[str, Any]]:
        """
        Scan all pending episodes in episodic memory, inspect current stream metrics,
        and perform retrospective reflection.
        """
        pending = self.em.get_pending_episodes()
        evaluated_reports = []

        for episode in pending:
            report = self.evaluate_single_episode(episode)
            if report:
                evaluated_reports.append(report)

        return evaluated_reports

    def evaluate_single_episode(self, episode: Episode) -> Optional[Dict[str, Any]]:
        """Evaluate a single episode against current working memory state."""
        lot_id = episode.lot_id
        current_state = self.wm.get_lot_state(lot_id)

        if not current_state:
            # If no streaming update received yet for this lot, defer evaluation
            return None

        # Pre-action metrics
        pre_occ = episode.initial_metrics.get("occupancy_percentage", 0.0)
        pre_vel = episode.initial_metrics.get("entry_velocity_per_min", 0.0)

        # Post-action metrics
        post_occ = current_state.occupancy_percentage
        post_vel = current_state.entry_velocity_per_min

        occ_delta = round(pre_occ - post_occ, 2)  # positive means reduction (good)
        vel_delta = round(pre_vel - post_vel, 2)  # positive means deceleration (good)

        # Diagnostic/quarantine episodes evaluate differently
        if episode.trigger_type in ("SENSOR_FAULT", "DLQ_ANOMALY"):
            score = 1.0
            summary = f"Sensor fault successfully isolated. Quarantine verified in working memory for {lot_id}."
        elif occ_delta >= self.min_reduction or vel_delta >= self.min_decel:
            score = 1.0
            summary = (
                f"Autonomous intervention SUCCEEDED for {lot_id}: Occupancy changed by -{occ_delta}% "
                f"(from {pre_occ}% to {post_occ}%); velocity adjusted by -{vel_delta}/min."
            )
        elif occ_delta >= 0.0:
            score = 0.5
            summary = (
                f"Autonomous intervention STABILIZED {lot_id}: Occupancy plateaued at {post_occ}% "
                f"(preventing critical overflow)."
            )
        else:
            score = -0.5
            summary = (
                f"Autonomous intervention INSUFFICIENT for {lot_id}: Occupancy increased by {-occ_delta}% "
                f"(from {pre_occ}% to {post_occ}%). Higher surge or broader reroute recommended."
            )

        # Update episode
        episode.post_action_metrics = {
            "occupancy_percentage": post_occ,
            "entry_velocity_per_min": post_vel,
            "occupancy_reduction_pct": occ_delta,
            "velocity_deceleration": vel_delta,
        }
        episode.reflection_score = score
        episode.reflection_summary = summary
        episode.status = "EVALUATED"

        self.em.update_episode(episode)
        logger.info("[Reflection] Episode %s Evaluated | Score: %.1f | %s", episode.episode_id, score, summary)

        return {
            "episode_id": episode.episode_id,
            "lot_id": lot_id,
            "score": score,
            "summary": summary,
            "metrics_delta": {"occupancy_delta": occ_delta, "velocity_delta": vel_delta},
        }
