"""Model loader - singleton for YOLO and other models"""

import os
# Set PaddlePaddle environment flags to disable PIR API and oneDNN/MKLDNN on CPU
os.environ["FLAGS_use_onednn"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["FLAGS_enable_pir_in_executor"] = "0"

import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global model instances
_yolo_model = None
_helmet_model = None
_plate_model = None
_ocr_model = None


def load_models():
    """Load all AI models at startup"""
    global _yolo_model, _helmet_model, _plate_model, _ocr_model
    from ultralytics import YOLO
    
    # 1. Load General YOLO (yolov8n.pt)
    try:
        yolo_path = settings.model_path if os.path.exists(settings.model_path) else "models/yolov8n.pt"
        if _yolo_model is None:
            logger.info(f"Loading general YOLO from {yolo_path}")
            _yolo_model = YOLO(yolo_path)
            _yolo_model.to(settings.device)
            logger.info("✅ General YOLO loaded")
    except Exception as e:
        logger.error(f"Failed to load general YOLO: {e}")

    # 2. Load Helmet Model (helmet_best.pt)
    try:
        helmet_path = "models/helmet_best.pt"
        if _helmet_model is None:
            logger.info(f"Loading custom helmet model from {helmet_path}")
            _helmet_model = YOLO(helmet_path)
            _helmet_model.to(settings.device)
            logger.info("✅ Helmet model loaded")
    except Exception as e:
        logger.error(f"Failed to load helmet model: {e}")

    # 3. Load Plate Detector (plate_best.pt)
    try:
        plate_model_path = "models/plate_best.pt"
        if _plate_model is None:
            logger.info(f"Loading custom Plate Detector from {plate_model_path}")
            _plate_model = YOLO(plate_model_path)
            _plate_model.to(settings.device)
            logger.info("✅ Plate Detector loaded")
    except Exception as e:
        logger.error(f"Failed to load Plate Detector: {e}")
    
    # 4. Load OCR
    try:
        if _ocr_model is None:
            from paddleocr import PaddleOCR
            logger.info("Loading PaddleOCR")
            _ocr_model = PaddleOCR(use_textline_orientation=True, lang='en')
            logger.info("✅ PaddleOCR loaded")
    except Exception as e:
        logger.error(f"Failed to load OCR: {e}")


def get_yolo_model():
    """Get general YOLO detector instance"""
    global _yolo_model
    if _yolo_model is None:
        load_models()
    return _yolo_model


def get_helmet_model():
    """Get custom helmet model instance"""
    global _helmet_model
    if _helmet_model is None:
        load_models()
    return _helmet_model


def get_violation_model():
    """Get custom violation model instance (mapped to helmet model)"""
    return get_helmet_model()


def get_plate_model():
    """Get Plate detector model instance"""
    global _plate_model
    if _plate_model is None:
        load_models()
    return _plate_model


def get_ocr_model():
    """Get OCR model instance"""
    global _ocr_model
    if _ocr_model is None:
        load_models()
    return _ocr_model


def get_seatbelt_model():
    """Removed seatbelt model getter"""
    return None


def get_wrongside_model():
    """Removed wrongside model getter"""
    return None


def get_parking_model():
    """Removed parking model getter"""
    return None
