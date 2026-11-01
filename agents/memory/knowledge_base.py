"""
agents.memory.knowledge_base
============================
Long-Term Memory & Domain Knowledge Base.
Course: AI373TA — Unit IV (Long-Term Memory & Knowledge Representation).

Stores:
- Static municipal parking regulations (BBMP bylaws).
- Spatial distance and connectivity graph between Bengaluru parking lots.
- Diurnal rush hour demand profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class LotSpatialNode:
    lot_id: str
    name: str
    zone: str
    latitude: float
    longitude: float
    capacity: int
    base_tariff_inr: float = 50.0


class ParkingKnowledgeBase:
    """Long-term domain knowledge representation for Bengaluru Parking."""

    def __init__(self) -> None:
        # Bengaluru 8 canonical parking facilities
        self.lots: Dict[str, LotSpatialNode] = {
            "LOT_MG_ROAD_01": LotSpatialNode("LOT_MG_ROAD_01", "MG Road Central", "CENTRAL", 12.9756, 77.6066, 150),
            "LOT_INDIRANAGAR_01": LotSpatialNode("LOT_INDIRANAGAR_01", "Indiranagar 100ft Rd", "EAST", 12.9784, 77.6408, 120),
            "LOT_KORAMANGALA_01": LotSpatialNode("LOT_KORAMANGALA_01", "Koramangala 80ft Rd", "SOUTH_EAST", 12.9352, 77.6245, 180),
            "LOT_WHITEFIELD_01": LotSpatialNode("LOT_WHITEFIELD_01", "Whitefield ITPL", "EAST_SUBURBAN", 12.9856, 77.7315, 200),
            "LOT_HEBBAL_01": LotSpatialNode("LOT_HEBBAL_01", "Hebbal Flyover Bay", "NORTH", 13.0358, 77.5970, 100),
            "LOT_JAYANAGAR_01": LotSpatialNode("LOT_JAYANAGAR_01", "Jayanagar 4th Block", "SOUTH", 12.9299, 77.5824, 110),
            "LOT_ECITY_01": LotSpatialNode("LOT_ECITY_01", "Electronic City Phase 1", "SOUTH_SUBURBAN", 12.8452, 77.6602, 80),
            "LOT_YELAHANKA_01": LotSpatialNode("LOT_YELAHANKA_01", "Yelahanka New Town", "NORTH_SUBURBAN", 13.1007, 77.5963, 60),
        }

        # Spatial Distance Matrix (road distance in km, transit time in minutes)
        # Format: (lot_a, lot_b): (distance_km, transit_time_mins)
        self.distance_matrix: Dict[Tuple[str, str], Tuple[float, int]] = {
            ("LOT_MG_ROAD_01", "LOT_INDIRANAGAR_01"): (3.8, 12),
            ("LOT_MG_ROAD_01", "LOT_KORAMANGALA_01"): (5.2, 16),
            ("LOT_MG_ROAD_01", "LOT_JAYANAGAR_01"): (6.0, 18),
            ("LOT_INDIRANAGAR_01", "LOT_KORAMANGALA_01"): (4.5, 14),
            ("LOT_INDIRANAGAR_01", "LOT_WHITEFIELD_01"): (11.0, 26),
            ("LOT_KORAMANGALA_01", "LOT_JAYANAGAR_01"): (4.0, 12),
            ("LOT_KORAMANGALA_01", "LOT_ECITY_01"): (12.5, 28),
            ("LOT_HEBBAL_01", "LOT_YELAHANKA_01"): (7.2, 15),
            ("LOT_HEBBAL_01", "LOT_MG_ROAD_01"): (8.5, 22),
        }

        # BBMP Municipal Parking Bylaws & Policy Constraints
        self.regulatory_rules: Dict[str, Any] = {
            "city": "Bengaluru",
            "authority": "BBMP Directorate of Urban Land Transport (DULT)",
            "min_hourly_tariff_inr": 30.0,
            "max_surge_cap_inr": 150.0,
            "max_surge_multiplier": 2.5,
            "max_continuous_parking_hours": 4.0,
            "grace_period_minutes": 10.0,
            "emergency_corridor_lots": ["LOT_MG_ROAD_01", "LOT_HEBBAL_01"],
            "peak_hour_windows": [
                {"name": "Morning Rush", "start_hour": 8, "end_hour": 11, "surge_allowed": True},
                {"name": "Evening Rush", "start_hour": 17, "end_hour": 21, "surge_allowed": True},
            ],
        }

    def get_distance(self, lot_a: str, lot_b: str) -> Optional[Tuple[float, int]]:
        """Return (distance_km, transit_mins) between two lots if available."""
        if lot_a == lot_b:
            return (0.0, 0)
        pair = (lot_a, lot_b)
        rev_pair = (lot_b, lot_a)
        return self.distance_matrix.get(pair, self.distance_matrix.get(rev_pair))

    def find_nearest_available_lots(self, source_lot: str, max_distance_km: float = 8.0) -> List[Dict[str, Any]]:
        """Find adjacent lots within search radius, sorted by physical distance."""
        neighbors = []
        for other_lot_id, node in self.lots.items():
            if other_lot_id == source_lot:
                continue
            dist_info = self.get_distance(source_lot, other_lot_id)
            if dist_info and dist_info[0] <= max_distance_km:
                neighbors.append({
                    "lot_id": other_lot_id,
                    "name": node.name,
                    "distance_km": dist_info[0],
                    "transit_time_mins": dist_info[1],
                    "capacity": node.capacity,
                })
        return sorted(neighbors, key=lambda x: x["distance_km"])

    def validate_tariff(self, proposed_rate_inr: float) -> Tuple[bool, str]:
        """Validate if a proposed tariff adheres to BBMP statutory caps."""
        min_rate = self.regulatory_rules["min_hourly_tariff_inr"]
        max_rate = self.regulatory_rules["max_surge_cap_inr"]
        if proposed_rate_inr < min_rate:
            return False, f"Tariff {proposed_rate_inr} INR is below legal minimum of {min_rate} INR"
        if proposed_rate_inr > max_rate:
            return False, f"Tariff {proposed_rate_inr} INR exceeds BBMP statutory ceiling of {max_rate} INR"
        return True, "Valid statutory tariff"
