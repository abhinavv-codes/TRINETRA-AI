"""Model loader - singleton for YOLO and other models"""

import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global model instances
_yolo_model = None
_ocr_model = None


def load_models():
    """Load all AI models at startup"""
    global _yolo_model, _ocr_model
    
    try:
        # Load YOLO
        from ultralytics import YOLO
        logger.info(f"Loading YOLO from {settings.model_path}")
        _yolo_model = YOLO(settings.model_path)
        _yolo_model.to(settings.device)
        logger.info("✅ YOLO loaded")
    except Exception as e:
        logger.error(f"Failed to load YOLO: {e}")
    
    try:
        # Load OCR
        from paddleocr import PaddleOCR
        logger.info("Loading PaddleOCR")
        _ocr_model = PaddleOCR(use_angle_cls=True, lang='en')
        logger.info("✅ PaddleOCR loaded")
    except Exception as e:
        logger.error(f"Failed to load OCR: {e}")


def get_yolo_model():
    """Get YOLO model instance"""
    if _yolo_model is None:
        load_models()
    return _yolo_model


def get_ocr_model():
    """Get OCR model instance"""
    if _ocr_model is None:
        load_models()
    return _ocr_model
