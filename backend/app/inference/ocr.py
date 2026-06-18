"""OCR - License plate recognition"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class OCRReader:
    """Wrapper for license plate OCR"""
    
    def __init__(self, model):
        self.model = model
    
    def read_plate(self, image_crop) -> Tuple[str, float]:
        """
        Read license plate text
        
        Returns:
            (plate_text, confidence)
        """
        try:
            result = self.model.ocr(image_crop, cls=True)
            
            if result and result[0]:
                # Get best result
                texts = [line[1][0] for line in result[0]]
                confidences = [line[1][1] for line in result[0]]
                
                plate_text = ''.join(texts)
                avg_conf = sum(confidences) / len(confidences)
                
                return plate_text, avg_conf
            
            return "", 0.0
        
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return "", 0.0
