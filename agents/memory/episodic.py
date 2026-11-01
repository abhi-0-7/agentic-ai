"""
agents.memory.episodic
======================
Episodic Memory Architecture.
Course: AI373TA — Unit IV (Episodic Memory & Interaction History).

Logs and persists chronological episodes of agent perceptions, decisions,
inter-agent negotiations, tool executions, and post-action evaluations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

logger = logging.getLogger("agents.memory.episodic")


@dataclass
class Episode:
    """A single discrete intervention episode in the life of the agent system."""
    episode_id: str = field(default_factory=lambda: f"EP_{uuid.uuid4().hex[:8].upper()}")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trigger_type: str = "CONGESTION_SPIKE"  # CONGESTION_SPIKE | SURGE_DEMAND | SENSOR_FAULT | CRITICAL_GRIDLOCK
    lot_id: str = "LOT_MG_ROAD_01"
    participating_agents: List[str] = field(default_factory=list)
    proposed_actions: Dict[str, Any] = field(default_factory=dict)
    negotiated_resolution: Optional[Dict[str, Any]] = None
    executed_action: Dict[str, Any] = field(default_factory=dict)
    initial_metrics: Dict[str, float] = field(default_factory=dict)  # e.g. {"occupancy_pct": 94.2, "entry_vel": 12.0}
    post_action_metrics: Optional[Dict[str, float]] = None          # populated by reflection loop
    reflection_score: Optional[float] = None                        # +1.0 (success), 0.0 (neutral), -1.0 (failure)
    reflection_summary: Optional[str] = None
    status: str = "PENDING_EVALUATION"                              # PENDING_EVALUATION | EVALUATED | CLOSED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Episode:
        return cls(**data)


class EpisodicMemory:
    """Persistent episodic log for retrospective learning, auditing, and reflection."""

    def __init__(self, persistence_path: str | Path = "data/episodic_memory.jsonl") -> None:
        self.file_path = Path(persistence_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.episodes: List[Episode] = []
        self._load_existing()

    def _load_existing(self) -> None:
        """Load past episodes from local storage if file exists."""
        if not self.file_path.is_file():
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.episodes.append(Episode.from_dict(json.loads(line)))
            logger.info("Loaded %d historical episodes from %s", len(self.episodes), self.file_path)
        except Exception as e:
            logger.warning("Could not read episodic memory file: %s", e)

    def record_episode(self, episode: Episode) -> None:
        """Record and persist an interaction episode."""
        self.episodes.append(episode)
        self._append_to_file(episode)

    def _append_to_file(self, episode: Episode) -> None:
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(episode.to_dict()) + "\n")
        except Exception as e:
            logger.error("Failed to append episode to disk: %s", e)

    def update_episode(self, episode: Episode) -> None:
        """Update an existing episode (e.g. after reflection evaluation) and persist."""
        for idx, ep in enumerate(self.episodes):
            if ep.episode_id == episode.episode_id:
                self.episodes[idx] = episode
                break
        self._rewrite_all()

    def _rewrite_all(self) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                for ep in self.episodes:
                    f.write(json.dumps(ep.to_dict()) + "\n")
        except Exception as e:
            logger.error("Failed to rewrite episodic memory: %s", e)

    def get_pending_episodes(self) -> List[Episode]:
        """Return episodes waiting for post-action reflection evaluation."""
        return [ep for ep in self.episodes if ep.status == "PENDING_EVALUATION"]

    def find_similar_episodes(self, lot_id: str, trigger_type: str, limit: int = 5) -> List[Episode]:
        """Retrieve historical episodes matching lot and trigger to inform new decisions."""
        matches = [
            ep for ep in self.episodes
            if ep.lot_id == lot_id and ep.trigger_type == trigger_type and ep.status == "EVALUATED"
        ]
        return matches[-limit:]
