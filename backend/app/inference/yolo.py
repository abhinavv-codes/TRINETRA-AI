"""YOLO object detector wrapper"""

import logging
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__)


class YOLODetector:
    """Wrapper for YOLO object detection"""
    
    def __init__(self, model):
        self.model = model
    
    def detect(self, image: np.ndarray, conf: float = 0.5) -> Dict:
        """
        Run YOLO detection on image
        
        Returns:
            Dict with:
                - boxes: List of detections [x1, y1, x2, y2, conf, class]
                - classes: Class names
                - confidences: Confidence scores
        """
        if self.model is None:
            logger.warning("YOLO model is not loaded, returning empty detections")
            return {
                "boxes": np.array([]),
                "classes": np.array([]),
                "confidences": np.array([]),
                "class_names": {},
            }
            
        results = self.model(image, conf=conf)
        detections = results[0]
        
        return {
            "boxes": detections.boxes.xyxy.cpu().numpy(),
            "classes": detections.boxes.cls.cpu().numpy(),
            "confidences": detections.boxes.conf.cpu().numpy(),
            "class_names": detections.names,
        }
