"""Congestion impact estimator - compute impact of illegal parking"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class CongestionEstimator:
    """Estimate congestion impact of illegal parking"""
    
    # BPR (Bureau of Public Roads) coefficients
    BPR_A = 0.15
    BPR_B = 4
    
    def estimate_impact(
        self,
        vehicle_width: float,  # in meters
        total_width: float,    # total road width in meters
        num_lanes: int,
        signal_cycle: int = 90  # seconds
    ) -> Dict:
        """
        Estimate congestion impact of a parked vehicle
        
        Args:
            vehicle_width: Width of parked vehicle (meters)
            total_width: Total road width (meters)
            num_lanes: Number of lanes
            signal_cycle: Traffic signal cycle (seconds)
        
        Returns:
            Dict with impact metrics:
                - blocked_width: Width blocked (meters)
                - lanes_lost: Effective lanes lost
                - occupancy_percent: Road occupancy %
                - delay_increase_percent: Estimated delay increase
        """
        
        # Safety buffer (assume 0.5m buffer)
        safety_buffer = 0.5
        blocked_width = vehicle_width + safety_buffer
        
        # Lanes lost (proportional)
        lane_width = total_width / num_lanes
        lanes_lost = blocked_width / lane_width
        effective_lanes = max(num_lanes - lanes_lost, 1)
        
        # Occupancy percentage
        occupancy_percent = (blocked_width / total_width) * 100
        
        # Estimated capacity reduction
        capacity_reduction_factor = effective_lanes / num_lanes
        
        # Predicted delay using BPR formula
        # t = t0 * (1 + a * (V/C)^b)
        # Assuming normal flow V/C = 0.8
        # Congested flow V/C = 0.8 / capacity_reduction_factor
        
        volume_capacity_ratio_normal = 0.8
        volume_capacity_ratio_congested = volume_capacity_ratio_normal / capacity_reduction_factor
        
        delay_multiplier_normal = 1 + self.BPR_A * (volume_capacity_ratio_normal ** self.BPR_B)
        delay_multiplier_congested = 1 + self.BPR_A * (volume_capacity_ratio_congested ** self.BPR_B)
        
        delay_increase_percent = ((delay_multiplier_congested - delay_multiplier_normal) / delay_multiplier_normal) * 100
        
        return {
            "blocked_width_m": round(blocked_width, 2),
            "lanes_lost": round(lanes_lost, 2),
            "effective_lanes": round(effective_lanes, 2),
            "occupancy_percent": round(occupancy_percent, 1),
            "delay_increase_percent": round(max(delay_increase_percent, 0), 1),
            "severity": self._get_severity(occupancy_percent, lanes_lost),
        }
    
    def _get_severity(self, occupancy_percent: float, lanes_lost: float) -> str:
        """Determine severity of parking violation"""
        if occupancy_percent > 50 or lanes_lost > 0.5:
            return "CRITICAL"
        elif occupancy_percent > 30 or lanes_lost > 0.3:
            return "HIGH"
        elif occupancy_percent > 15:
            return "MEDIUM"
        else:
            return "LOW"
