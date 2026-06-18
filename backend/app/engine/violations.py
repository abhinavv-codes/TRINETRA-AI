"""Violation detection engine - rules for 7+ violation types"""

import logging
from typing import List, Dict
from dataclasses import dataclass
from app.core.constants import ViolationType

logger = logging.getLogger(__name__)


@dataclass
class ViolationEvent:
    """Detected violation event"""
    violations: List[ViolationType]
    frame_id: int
    timestamp: str
    camera_id: str
    speed_kmph: float = 0.0
    ped_count: int = 0
    zone_tags: List[str] = None
    signal_state: str = "GREEN"
    
    def __post_init__(self):
        if self.zone_tags is None:
            self.zone_tags = []


class ViolationEngine:
    """Rule-based violation detection"""
    
    def __init__(self):
        self.rules = {
            ViolationType.NO_HELMET: self._check_no_helmet,
            ViolationType.TRIPLE_RIDING: self._check_triple_riding,
            ViolationType.RED_LIGHT: self._check_red_light,
            ViolationType.WRONG_SIDE: self._check_wrong_side,
            ViolationType.ILLEGAL_PARKING: self._check_illegal_parking,
        }
    
    def detect_violations(self, detections: Dict) -> List[ViolationType]:
        """
        Detect violations from YOLO detections
        
        Args:
            detections: Dict with boxes, classes, confidences
        
        Returns:
            List of detected violations
        """
        violations = []
        
        # Check each rule
        for violation_type, rule_func in self.rules.items():
            if rule_func(detections):
                violations.append(violation_type)
        
        return violations
    
    def _check_no_helmet(self, detections: Dict) -> bool:
        """Check for riders without helmet"""
        # TODO: Check if helmet is present in detections
        return False
    
    def _check_triple_riding(self, detections: Dict) -> bool:
        """Check for 3+ persons on a two-wheeler"""
        # TODO: Count persons associated with motorcycle
        return False
    
    def _check_red_light(self, detections: Dict) -> bool:
        """Check if vehicle crosses during red light"""
        # TODO: Check signal state and vehicle position
        return False
    
    def _check_wrong_side(self, detections: Dict) -> bool:
        """Check for wrong-side driving"""
        # TODO: Check vehicle direction vs lane direction
        return False
    
    def _check_illegal_parking(self, detections: Dict) -> bool:
        """Check for illegal parking"""
        # TODO: Check if vehicle is stationary in no-parking zone
        return False
