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
        if self.model is None:
            logger.warning("OCR model is not loaded, returning empty text")
            return "", 0.0
            
        try:
            result = self.model.ocr(image_crop)
            
            if not result:
                return "", 0.0
                
            # Handle list-of-dicts format (PaddleOCR v3.7 / PaddleX)
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                texts = result[0].get('rec_texts', [])
                confidences = result[0].get('rec_scores', [])
                if texts:
                    plate_text = ''.join(texts)
                    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
                    return plate_text, avg_conf
                return "", 0.0
                
            # Handle legacy list-of-lists format
            if isinstance(result, list) and len(result) > 0 and result[0]:
                texts = [line[1][0] for line in result[0] if line and len(line) > 1 and line[1]]
                confidences = [line[1][1] for line in result[0] if line and len(line) > 1 and line[1]]
                if texts:
                    plate_text = ''.join(texts)
                    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
                    return plate_text, avg_conf
                    
            return "", 0.0
        
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return "", 0.0
