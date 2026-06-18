"""Risk scoring engine - compute 0-100 risk score with explainability"""

import numpy as np
import logging
from typing import Dict, Tuple
from app.core.constants import RISK_WEIGHTS, VIOLATION_SEVERITY, ViolationType, RiskBand

logger = logging.getLogger(__name__)


class RiskEngine:
    """Compute 0-100 risk score for violations"""
    
    def __init__(self, weights: Dict = None):
        """
        Initialize risk engine
        
        Args:
            weights: Optional custom weights for risk factors
        """
        self.weights = weights or RISK_WEIGHTS
        self.severity_map = VIOLATION_SEVERITY
    
    def compute_risk_score(
        self,
        violation_types: list,
        context: Dict
    ) -> Tuple[int, str, Dict]:
        """
        Compute 0-100 risk score
        
        Args:
            violation_types: List of detected violations
            context: Context features dict with keys:
                - speed_kmph: Vehicle speed
                - ped_count: Number of pedestrians
                - traffic_density: 0-1 traffic density
                - zones: List of zone tags
                - hour: Hour of day (0-23)
        
        Returns:
            (risk_score, risk_band, factor_breakdown)
        """
        
        if not violation_types:
            return 0, RiskBand.LOW, {}
        
        # Base severity (max of all violations)
        violation_severity = max(
            [self.severity_map.get(v, 0.5) for v in violation_types]
        )
        
        # Normalize context features to [0, 1]
        speed_norm = min(context.get('speed_kmph', 0) / 100, 1.0)
        ped_norm = min(context.get('ped_count', 0) / 20, 1.0)
        density_norm = context.get('traffic_density', 0.5)
        
        # Zone bonuses
        school_zone_bonus = 1.0 if 'SCHOOL_ZONE' in context.get('zones', []) else 0.0
        junction_bonus = 1.0 if 'JUNCTION' in context.get('zones', []) else 0.0
        
        # Time-of-day weight
        hour = context.get('hour', 12)
        time_weight = 1.5 if 8 <= hour <= 18 else 1.0
        
        # Weighted sum
        raw_score = (
            self.weights['severity'] * violation_severity +
            self.weights['pedestrians'] * ped_norm +
            self.weights['speed'] * speed_norm +
            self.weights['school_zone'] * school_zone_bonus +
            self.weights['density'] * density_norm +
            self.weights['junction'] * junction_bonus +
            self.weights['time'] * (time_weight / 1.5)  # Normalize
        )
        
        # Sigmoid squash to 0-100
        sigmoid = 1 / (1 + np.exp(-raw_score * 5))  # Scale for better curve
        risk_score = int(sigmoid * 100)
        
        # Get risk band
        risk_band = self._get_risk_band(risk_score)
        
        # Factor breakdown for explainability
        factor_breakdown = {
            'severity': round(violation_severity * 100),
            'pedestrians': round(ped_norm * 100),
            'speed': round(speed_norm * 100),
            'school_zone': round(school_zone_bonus * 100),
            'traffic_density': round(density_norm * 100),
            'junction': round(junction_bonus * 100),
            'time_weight': round((time_weight / 1.5) * 100),
        }
        
        logger.info(f"Risk score: {risk_score}/{risk_band}")
        
        return risk_score, risk_band, factor_breakdown
    
    def _get_risk_band(self, score: int) -> str:
        """Get risk band from score"""
        if score >= 80:
            return RiskBand.CRITICAL
        elif score >= 60:
            return RiskBand.HIGH
        elif score >= 40:
            return RiskBand.MEDIUM
        else:
            return RiskBand.LOW
