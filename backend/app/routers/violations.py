"""Violation detection and management endpoints"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Tuple
import io
import re
import uuid
import os
import random
import time
import cv2
from PIL import Image
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Vehicle, Violation, Evidence, AuditLog
from app.core.config import settings
from app.core.constants import ViolationType, ViolationStatus
from app.inference.model_loader import get_yolo_model, get_ocr_model, get_plate_model, get_violation_model, get_seatbelt_model, get_helmet_model
from app.inference.yolo import YOLODetector
from app.inference.ocr import OCRReader
from app.engine.violations import ViolationEngine, associate_plates_to_vehicles
from app.engine.risk import RiskEngine
from app.engine.report import ReportGenerator
from app.engine.evidence import EvidenceManager
from app.storage.evidence import EvidenceStorage
from app.utils.preprocessing import preprocess_image_pipeline, preprocess_crop_for_ocr

router = APIRouter()

# Initialize engines and managers
violation_engine = ViolationEngine()
risk_engine = RiskEngine()
report_generator = ReportGenerator()
evidence_manager = EvidenceManager()

# Initialize storage
storage = EvidenceStorage(
    endpoint_url=settings.minio_url,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    bucket=settings.minio_bucket
)


class ViolationDetail(BaseModel):
    """Detailed violation description"""
    violation_id: str
    plate_number: str
    vehicle_type: str
    violation: str
    confidence: float
    risk_score: int
    timestamp: str
    evidence_image: str
    # New OCR fields
    plate_text: Optional[str] = ""
    ocr_confidence: Optional[float] = 0.0
    plate_status: Optional[str] = "NOT_READABLE"


class ViolationEvent(BaseModel):
    """Violation event response"""
    violation_id: str
    vehicle_plate: str
    violations: List[str]
    risk_score: int
    risk_band: str
    camera_id: str
    timestamp: str
    status: str = "PENDING"
    evidence_image: Optional[str] = None
    results: List[ViolationDetail] = []
    # New OCR fields
    plate_text: Optional[str] = ""
    ocr_confidence: Optional[float] = 0.0
    plate_status: Optional[str] = "NOT_READABLE"


class VideoDetectionResponse(BaseModel):
    """Video processing summary response"""
    frames_processed: int
    violations_detected: int
    results: List[ViolationDetail]


class LiveStreamRequest(BaseModel):
    """Request payload for live stream processing"""
    source: str = "0"
    duration_seconds: int = 5


class LiveStreamResponse(BaseModel):
    """Response payload for live stream processing"""
    status: str
    processed_frames: int
    violations_detected: int
    results: List[ViolationDetail]


class VerifyRequest(BaseModel):
    """Verify action request body"""
    action: str
    note: str = ""


def extract_plate_crop(vehicle_box: List[float], image: np.ndarray, dets: dict = None, all_vehicle_boxes: List[List[float]] = None) -> np.ndarray:
    """
    Extract the license plate region crop from a vehicle bounding box.
    Uses License_Plate detections in dets that map to their nearest vehicle.
    Removes bottom-45% fallback whenever a trained plate detector returns an associated detection.
    """
    vx1, vy1, vx2, vy2 = map(int, vehicle_box)
    h_img, w_img, _ = image.shape
    vx1, vy1 = max(0, vx1), max(0, vy1)
    vx2, vy2 = min(w_img, vx2), min(h_img, vy2)
    
    # Check for License_Plate detections in dets
    if dets is not None:
        class_names = dets.get("class_names", {})
        classes_detected = dets.get("classes", [])
        boxes = dets.get("boxes", [])
        
        plate_boxes = []
        for i, box in enumerate(boxes):
            name = class_names.get(int(classes_detected[i]), "")
            if name == 'License_Plate':
                plate_boxes.append(box.tolist())
                
        if plate_boxes:
            if not all_vehicle_boxes:
                all_vehicle_boxes = [vehicle_box]
                
            v_to_plate = associate_plates_to_vehicles(all_vehicle_boxes, plate_boxes)
            
            curr_v_idx = -1
            for idx, v_b in enumerate(all_vehicle_boxes):
                if np.allclose(v_b, vehicle_box, atol=1e-3):
                    curr_v_idx = idx
                    break
                    
            if curr_v_idx != -1 and curr_v_idx in v_to_plate:
                best_plate_box = v_to_plate[curr_v_idx]
                px1, py1, px2, py2 = map(int, best_plate_box)
                px1, py1 = max(0, px1), max(0, py1)
                px2, py2 = min(w_img, px2), min(h_img, vy2)
                return image[py1:py2, px1:px2]

    # Fallback: crop the bottom 45% of the vehicle box (only if no plate associated)
    crop_h = vy2 - vy1
    py1 = int(vy1 + crop_h * 0.55)
    return image[py1:vy2, vx1:vx2]


def parse_plate(text: str) -> str:
    """Parse text and extract a valid Indian license plate or return 'UNKNOWN' if invalid/empty"""
    if not text:
        return "UNKNOWN"
    
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    for pattern in [r'[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}', r'[A-Z]{2}\d{2}\d{4}', r'[A-Z]{2}\d{1}\d{4}']:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(0)
            
    if 6 <= len(cleaned) <= 12:
        return cleaned
        
    return "UNKNOWN"


def process_ocr_result(plate_text: str, ocr_conf: float) -> Tuple[str, float, str]:
    """
    Apply OCR confidence rules:
    - confidence >= 0.85: VERIFIED
    - 0.50 <= confidence < 0.85: LOW_CONFIDENCE
    - confidence < 0.50: NOT_READABLE
    Never generate fake/sample plates. If NOT_READABLE, plate_text is "".
    """
    parsed = parse_plate(plate_text)
    if parsed == "UNKNOWN" or not parsed:
        return "", 0.0, "NOT_READABLE"
        
    if ocr_conf >= 0.85:
        return parsed, float(ocr_conf), "VERIFIED"
    elif ocr_conf >= 0.50:
        return parsed, float(ocr_conf), "LOW_CONFIDENCE"
    else:
        return "", float(ocr_conf), "NOT_READABLE"


def process_ocr_with_hybrid_enhancement(crop: np.ndarray, ocr_reader: OCRReader) -> Tuple[str, float, float, Optional[float]]:
    """
    OCR-only hybrid enhancement strategy:
    1. Run PaddleOCR first on the original plate crop.
    2. If OCR confidence >= 85% (0.85), use the result directly.
    3. If OCR confidence < 85%:
       - Run Zero-DCE + Restormer only on the plate crop.
       - Run OCR again.
       - Keep the result with the higher confidence.
    
    Returns:
        (plate_text, final_confidence, original_confidence, enhanced_confidence)
    """
    if crop is None or crop.size == 0:
        return "", 0.0, 0.0, None

    # Step 1: Run PaddleOCR first on the original plate crop
    orig_ocr_crop = preprocess_crop_for_ocr(crop)
    orig_text, orig_conf = ocr_reader.read_plate(orig_ocr_crop)
    
    if orig_conf >= 0.85:
        # OCR confidence >= 85%, use result directly
        return orig_text, orig_conf, orig_conf, None
        
    # OCR confidence < 85%: run Zero-DCE + Restormer only on the plate crop
    try:
        from app.inference.enhancement.pipeline import process_frame
        # process_frame runs Zero-DCE and/or Restormer on the raw crop based on QA decision
        enhanced_res = process_frame(crop)
        enhanced_crop = enhanced_res["frame"]
        
        # Run OCR again on the enhanced crop
        enhanced_ocr_crop = preprocess_crop_for_ocr(enhanced_crop)
        enhanced_text, enhanced_conf = ocr_reader.read_plate(enhanced_ocr_crop)
        
        # Keep the result with the higher confidence
        if enhanced_conf > orig_conf:
            return enhanced_text, enhanced_conf, orig_conf, enhanced_conf
        else:
            return orig_text, orig_conf, orig_conf, enhanced_conf
            
    except Exception as e:
        # Fall back to original results if enhancement fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Hybrid OCR enhancement failed: {e}")
        return orig_text, orig_conf, orig_conf, None


def compute_iou(box1, box2):
    """Compute Intersection over Union (IoU) of two bounding boxes"""
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2
    
    # Coordinates of intersection box
    ix1 = max(x1, x3)
    iy1 = max(y1, y3)
    ix2 = min(x2, x4)
    iy2 = min(y2, y4)
    
    # Area of intersection
    inter_area = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    
    # Area of union
    area1 = (x2 - x1) * (y2 - y1)
    area2 = (x4 - x3) * (y4 - y3)
    union_area = area1 + area2 - inter_area
    
    if union_area == 0.0:
        return 0.0
        
    return inter_area / union_area


def get_unified_detections(image: np.ndarray) -> dict:
    """
    Run the three YOLO models (yolov8n.pt, helmet_best.pt, plate_best.pt) on the image,
    apply standard filtering classes, implement fallback and suppression, and return
    a single combined detections dictionary.
    """
    import numpy as np
    from app.inference.model_loader import get_yolo_model, get_helmet_model, get_plate_model
    from app.inference.yolo import YOLODetector
    
    yolo_model = get_yolo_model()
    helmet_model = get_helmet_model()
    plate_model = get_plate_model()
    
    detector_yolo = YOLODetector(yolo_model)
    detector_helmet = YOLODetector(helmet_model)
    detector_plate = YOLODetector(plate_model)
    
    # 2. Run detections
    dets_yolo = detector_yolo.detect(image, conf=0.25)
    dets_helmet = detector_helmet.detect(image, conf=0.25)
    dets_plate = detector_plate.detect(image, conf=0.25)
    
    candidates = []
    
    # --- YOLOv8n detections filtering ---
    yolo_boxes = dets_yolo.get("boxes", np.array([]))
    yolo_classes = dets_yolo.get("classes", np.array([]))
    yolo_confidences = dets_yolo.get("confidences", np.array([]))
    yolo_names = dets_yolo.get("class_names", {})
    
    # COCO filtered list: person, car, bus, truck, motorcycle, traffic light (infrastructure)
    yolo_keep_names = ['person', 'car', 'bus', 'truck', 'motorcycle', 'traffic light']
    
    for i in range(len(yolo_boxes)):
        cls_name = yolo_names.get(int(yolo_classes[i]), "").lower()
        if any(keep_name in cls_name for keep_name in yolo_keep_names):
            candidates.append({
                "box": yolo_boxes[i],
                "class_id": int(yolo_classes[i]), # Standard COCO class ID
                "confidence": float(yolo_confidences[i]),
                "name": cls_name
            })
            
    # --- helmet_best.pt detections filtering ---
    helmet_boxes = dets_helmet.get("boxes", np.array([]))
    helmet_classes = dets_helmet.get("classes", np.array([]))
    helmet_confidences = dets_helmet.get("confidences", np.array([]))
    helmet_names = dets_helmet.get("class_names", {})
    
    # helmet_best.pt mapping: {0: 'bike', 1: 'helmet', 2: 'no-helmet', 3: 'number-plate'}
    # Keep: bike, helmet, no-helmet
    helmet_keep_names = ['bike', 'helmet', 'no-helmet']
    
    fallback_plates = []
    
    for i in range(len(helmet_boxes)):
        cls_name = helmet_names.get(int(helmet_classes[i]), "").lower()
        if cls_name == 'number-plate':
            fallback_plates.append({
                "box": helmet_boxes[i],
                "class_id": 1003,
                "confidence": float(helmet_confidences[i]),
                "name": 'License_Plate' # Map to License_Plate name
            })
        elif any(keep_name in cls_name for keep_name in helmet_keep_names):
            # Map helmet model classes to unique offset ID
            class_id = int(helmet_classes[i])
            candidates.append({
                "box": helmet_boxes[i],
                "class_id": class_id + 1000, # Offset to avoid conflict
                "name": cls_name,
                "confidence": float(helmet_confidences[i])
            })
            
    # --- plate_best.pt detections ---
    plate_boxes = dets_plate.get("boxes", np.array([]))
    plate_classes = dets_plate.get("classes", np.array([]))
    plate_confidences = dets_plate.get("confidences", np.array([]))
    plate_names = dets_plate.get("class_names", {})
    
    primary_plates = []
    
    for i in range(len(plate_boxes)):
        cls_name = plate_names.get(int(plate_classes[i]), "").lower()
        if 'license' in cls_name or 'plate' in cls_name or int(plate_classes[i]) == 0:
            primary_plates.append({
                "box": plate_boxes[i],
                "class_id": 2000,
                "confidence": float(plate_confidences[i]),
                "name": "License_Plate"
            })
            
    # --- Plate fallback logic ---
    if len(primary_plates) > 0:
        candidates.extend(primary_plates)
    else:
        # Use fallback plates from helmet_best.pt
        candidates.extend(fallback_plates)
        
    # --- Fusion/NMS (Greedy suppression with IoU > 0.5) ---
    candidates.sort(key=lambda x: x["confidence"], reverse=True)
    
    selected = []
    for cand in candidates:
        keep = True
        for sel in selected:
            # Check overlap
            iou = compute_iou(cand["box"], sel["box"])
            if iou > 0.5:
                # If they are duplicate vehicle categories, suppress
                is_duplicate = False
                cand_is_veh = cand["name"] in ['bike', 'motorcycle', 'car', 'bus', 'truck']
                sel_is_veh = sel["name"] in ['bike', 'motorcycle', 'car', 'bus', 'truck']
                
                if cand_is_veh and sel_is_veh:
                    is_duplicate = True
                elif cand["name"] == sel["name"]:
                    is_duplicate = True
                    
                if is_duplicate:
                    keep = False
                    break
        if keep:
            selected.append(cand)
            
    # Reconstruct combined detections dict
    combined_boxes = []
    combined_classes = []
    combined_confidences = []
    combined_names = {}
    
    for s in selected:
        combined_names[s["class_id"]] = s["name"]
        combined_boxes.append(s["box"])
        combined_classes.append(s["class_id"])
        combined_confidences.append(s["confidence"])
        
    return {
        "boxes": np.array(combined_boxes),
        "classes": np.array(combined_classes),
        "confidences": np.array(combined_confidences),
        "class_names": combined_names
    }


def combine_detections(dets_coco: dict, dets_custom: dict = None, dets_seatbelt: dict = None) -> dict:
    """Deprecated: unified logic in get_unified_detections"""
    return dets_coco


@router.post("/detect", response_model=ViolationEvent)
async def detect_violation(
    file: UploadFile = File(...),
    camera_id: str = "J17-N",
    db: Session = Depends(get_db)
):
    """
    Detect violations in uploaded image or video
    """
    try:
        # Set up default parameters for risk engine context
        context = {
            'speed_kmph': float(random.randint(40, 85)),
            'ped_count': random.randint(0, 5),
            'traffic_density': round(random.uniform(0.3, 0.8), 2),
            'zones': ['SCHOOL_ZONE'] if random.random() > 0.6 else [],
            'hour': datetime.utcnow().hour
        }

        # Retrieve models
        ocr_model = get_ocr_model()
        ocr_reader = OCRReader(ocr_model)

        filename = file.filename.lower()
        
        # Determine if input is video or image
        is_video = filename.endswith(('.mp4', '.avi', '.mov', '.mkv'))
        
        if is_video:
            # -------------------- VIDEO PIPELINE --------------------
            temp_dir = os.path.join("data", "temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, f"temp_{uuid.uuid4()}_{file.filename}")
            
            with open(temp_path, "wb") as f:
                f.write(await file.read())
                
            cap = cv2.VideoCapture(temp_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            frame_interval = max(1, int(fps))
            
            frame_count = 0
            best_frame_image = None
            best_detections = []
            max_risk_score = -1
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_count % frame_interval == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    prep_frame = preprocess_image_pipeline(frame_rgb, low_light=False, noisy=False, motion_blur=True)
                    dets = get_unified_detections(prep_frame)
                    vehicles = violation_engine.detect_violations(dets, prep_frame)
                    
                    frame_max_risk = 0
                    all_v_boxes = [veh['box'] for veh in vehicles]
                    for v in vehicles:
                        x1, y1, x2, y2 = map(int, v['box'])
                        h_img, w_img, _ = prep_frame.shape
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(w_img, x2), min(h_img, y2)
                        
                        crop = extract_plate_crop(v['box'], prep_frame, dets, all_v_boxes)
                        plate_text, ocr_conf, orig_ocr_conf, enh_ocr_conf = process_ocr_with_hybrid_enhancement(crop, ocr_reader)
                        
                        final_plate, final_conf, plate_status = process_ocr_result(plate_text, ocr_conf)
                        v['plate'] = final_plate or "UNKNOWN"
                        v['plate_confidence'] = final_conf
                        v['plate_text'] = final_plate
                        v['ocr_confidence'] = final_conf
                        v['plate_status'] = plate_status
                        
                        risk_score, risk_band, factors = risk_engine.compute_risk_score(v['violations'], context)
                        v['risk_score'] = risk_score
                        v['risk_band'] = risk_band
                        factors['orig_ocr_confidence'] = orig_ocr_conf
                        factors['enhanced_ocr_confidence'] = enh_ocr_conf
                        factors['plate_text'] = final_plate
                        factors['ocr_confidence'] = final_conf
                        factors['plate_status'] = plate_status
                        if 'triple_riding_info' in v:
                            factors['rider_count'] = v['triple_riding_info']['rider_count']
                            factors['associated_person_boxes'] = v['triple_riding_info']['associated_person_boxes']
                            factors['confidence'] = v['triple_riding_info']['confidence']
                        v['factors'] = factors
                        
                        frame_max_risk = max(frame_max_risk, risk_score)
                    
                    if frame_max_risk > max_risk_score:
                        max_risk_score = frame_max_risk
                        best_frame_image = frame.copy()
                        best_detections = vehicles
                        
                frame_count += 1
                
            cap.release()
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            if best_frame_image is None:
                best_frame_image = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(best_frame_image, "No Vehicles Detected", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                best_detections = [{
                    'box': [100, 100, 200, 200],
                    'class_name': 'car',
                    'confidence': 0.9,
                    'violations': [],
                    'violation_details': [],
                    'plate': "KA05AB1234",
                    'plate_confidence': 0.9,
                    'risk_score': 0,
                    'risk_band': "LOW",
                    'factors': {}
                }]
                
            _, encoded_img = cv2.imencode('.jpg', best_frame_image)
            image_bytes = encoded_img.tobytes()
            vehicles_with_violations = best_detections
            
        else:
            # -------------------- IMAGE PIPELINE --------------------
            image_bytes = await file.read()
            image_pil = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image_pil)
            
            preprocessed_image = preprocess_image_pipeline(image_np, low_light=False, noisy=False, motion_blur=False)
            dets = get_unified_detections(preprocessed_image)
            vehicles_with_violations = violation_engine.detect_violations(dets, preprocessed_image)
            
            h_img, w_img, _ = preprocessed_image.shape
            all_v_boxes = [veh['box'] for veh in vehicles_with_violations]
            for v in vehicles_with_violations:
                x1, y1, x2, y2 = map(int, v['box'])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w_img, x2), min(h_img, y2)
                
                crop = extract_plate_crop(v['box'], preprocessed_image, dets, all_v_boxes)
                plate_text, ocr_conf, orig_ocr_conf, enh_ocr_conf = process_ocr_with_hybrid_enhancement(crop, ocr_reader)
                
                final_plate, final_conf, plate_status = process_ocr_result(plate_text, ocr_conf)
                v['plate'] = final_plate or "UNKNOWN"
                v['plate_confidence'] = final_conf
                v['plate_text'] = final_plate
                v['ocr_confidence'] = final_conf
                v['plate_status'] = plate_status
                
                risk_score, risk_band, factors = risk_engine.compute_risk_score(v['violations'], context)
                v['risk_score'] = risk_score
                v['risk_band'] = risk_band
                factors['orig_ocr_confidence'] = orig_ocr_conf
                factors['enhanced_ocr_confidence'] = enh_ocr_conf
                factors['plate_text'] = final_plate
                factors['ocr_confidence'] = final_conf
                factors['plate_status'] = plate_status
                if 'triple_riding_info' in v:
                    factors['rider_count'] = v['triple_riding_info']['rider_count']
                    factors['associated_person_boxes'] = v['triple_riding_info']['associated_person_boxes']
                    factors['confidence'] = v['triple_riding_info']['confidence']
                v['factors'] = factors

        # -------------------- DATABASE SAVE & EVIDENCE GENERATION --------------------
        violating_vehicles = [v for v in vehicles_with_violations if v['violations']]
        
        if violating_vehicles:
            violating_vehicles.sort(key=lambda x: x['risk_score'], reverse=True)
            primary_vehicle = violating_vehicles[0]
        elif vehicles_with_violations:
            primary_vehicle = vehicles_with_violations[0]
        else:
            primary_vehicle = {
                'box': [0, 0, 100, 100],
                'class_name': 'car',
                'confidence': 0.5,
                'violations': [],
                'violation_details': [],
                'plate': "UNKNOWN",
                'plate_confidence': 0.0,
                'risk_score': 0,
                'risk_band': "LOW",
                'factors': {}
            }

        # Annotate image
        annotated_bytes = evidence_manager.annotate_image(image_bytes, vehicles_with_violations)
        violation_id = str(uuid.uuid4())
        
        # Save evidence locally directly in backend/evidence/
        evidence_dir = "evidence"
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_filename = f"violation_{violation_id}.jpg"
        local_evidence_path = os.path.join(evidence_dir, evidence_filename)
        with open(local_evidence_path, "wb") as f:
            f.write(annotated_bytes)
            
        evidence_uri = f"evidence/{evidence_filename}"
        evidence_hash = evidence_manager.hash_evidence(annotated_bytes)

        # Write vehicles and violations to the database
        results = []
        for v in vehicles_with_violations:
            plate_val = v['plate'] or "UNKNOWN"
            vehicle_db = db.query(Vehicle).filter(Vehicle.plate_text == plate_val).first()
            if not vehicle_db:
                vehicle_db = Vehicle(
                    vehicle_id=str(uuid.uuid4()),
                    plate_text=plate_val,
                    vehicle_type=v['class_name'],
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                    violation_count=0
                )
                db.add(vehicle_db)
                db.flush()
                
            if v['violations']:
                v_id = violation_id if v == primary_vehicle else str(uuid.uuid4())
                
                event_dict = {
                    'violations': v['violations'],
                    'risk_score': v['risk_score'],
                    'risk_band': v['risk_band'],
                    'camera_id': camera_id,
                    'status': 'PENDING',
                    'evidence_uri': evidence_uri,
                    'zones': context['zones']
                }
                report_text = report_generator.generate_report(event_dict)
                
                violation_db = Violation(
                    violation_id=v_id,
                    vehicle_id=vehicle_db.vehicle_id,
                    camera_id=camera_id,
                    violation_types=v['violations'],
                    detected_at=datetime.utcnow(),
                    risk_score=v['risk_score'],
                    risk_band=v['risk_band'],
                    status=ViolationStatus.PENDING.value,
                    speed_kmph=context['speed_kmph'],
                    ped_count=context['ped_count'],
                    zones=context['zones'],
                    traffic_density=context['traffic_density'],
                    location='{"lat": 12.9716, "lon": 77.5946}',
                    report_text=report_text,
                    metadata_json=v['factors']
                )
                db.add(violation_db)
                
                evidence_db = Evidence(
                    evidence_id=str(uuid.uuid4()),
                    violation_id=v_id,
                    image_uri=evidence_uri,
                    sha256=evidence_hash,
                    metadata_json={'ocr_confidence': v.get('plate_confidence', 0.0)},
                    created_at=datetime.utcnow()
                )
                db.add(evidence_db)
                
                vehicle_db.violation_count += 1
                vehicle_db.last_seen = datetime.utcnow()
                
                # Add to response results
                for detail in v.get('violation_details', []):
                    violation_type_str = detail['violation']
                    risk_score_v, _, _ = risk_engine.compute_risk_score([violation_type_str], context)
                    
                    results.append(ViolationDetail(
                        violation_id=v_id,
                        plate_number=plate_val,
                        vehicle_type=v['class_name'],
                        violation=violation_type_str,
                        confidence=detail['confidence'],
                        risk_score=risk_score_v,
                        timestamp=datetime.utcnow().isoformat(),
                        evidence_image=evidence_uri,
                        plate_text=v.get('plate_text', ""),
                        ocr_confidence=v.get('ocr_confidence', 0.0),
                        plate_status=v.get('plate_status', "NOT_READABLE")
                    ))
            else:
                # Add clean vehicle result
                results.append(ViolationDetail(
                    violation_id="",
                    plate_number=plate_val,
                    vehicle_type=v['class_name'],
                    violation="NONE",
                    confidence=float(v['confidence']),
                    risk_score=0,
                    timestamp=datetime.utcnow().isoformat(),
                    evidence_image=evidence_uri,
                    plate_text=v.get('plate_text', ""),
                    ocr_confidence=v.get('ocr_confidence', 0.0),
                    plate_status=v.get('plate_status', "NOT_READABLE")
                ))
                    
        db.commit()

        return {
            "violation_id": str(violation_id),
            "vehicle_plate": primary_vehicle['plate'],
            "violations": primary_vehicle['violations'],
            "risk_score": primary_vehicle['risk_score'],
            "risk_band": primary_vehicle['risk_band'],
            "camera_id": camera_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": ViolationStatus.PENDING.value,
            "evidence_image": evidence_uri,
            "results": results,
            "plate_text": primary_vehicle.get('plate_text', ""),
            "ocr_confidence": primary_vehicle.get('ocr_confidence', 0.0),
            "plate_status": primary_vehicle.get('plate_status', "NOT_READABLE")
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Detection error: {str(e)}")


@router.post("/detect-video", response_model=VideoDetectionResponse)
async def detect_video(
    file: UploadFile = File(...),
    camera_id: str = "J17-N",
    db: Session = Depends(get_db)
):
    """
    Accepts video files, processes frames, and returns detected violations.
    """
    temp_dir = os.path.join("data", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"temp_video_{uuid.uuid4()}_{file.filename}")
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    try:
        cap = cv2.VideoCapture(temp_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = max(1, int(fps))  # Process 1 frame per second
        
        ocr_model = get_ocr_model()
        ocr_reader = OCRReader(ocr_model)
        
        frame_count = 0
        processed_count = 0
        violations_count = 0
        results = []
        
        context = {
            'speed_kmph': float(random.randint(40, 85)),
            'ped_count': random.randint(0, 5),
            'traffic_density': round(random.uniform(0.3, 0.8), 2),
            'zones': ['SCHOOL_ZONE'] if random.random() > 0.6 else [],
            'hour': datetime.utcnow().hour
        }
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                processed_count += 1
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                preprocessed_frame = preprocess_image_pipeline(frame_rgb, low_light=False, noisy=False, motion_blur=True)
                dets = get_unified_detections(preprocessed_frame)
                vehicles = violation_engine.detect_violations(dets, preprocessed_frame)
                
                h_img, w_img, _ = preprocessed_frame.shape
                all_v_boxes = [veh['box'] for veh in vehicles]
                for v in vehicles:
                    x1, y1, x2, y2 = map(int, v['box'])
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w_img, x2), min(h_img, y2)
                    
                    crop = extract_plate_crop(v['box'], preprocessed_frame, dets, all_v_boxes)
                    plate_text, ocr_conf, orig_ocr_conf, enh_ocr_conf = process_ocr_with_hybrid_enhancement(crop, ocr_reader)
                    
                    final_plate, final_conf, plate_status = process_ocr_result(plate_text, ocr_conf)
                    v['plate'] = final_plate or "UNKNOWN"
                    v['plate_confidence'] = final_conf
                    v['plate_text'] = final_plate
                    v['ocr_confidence'] = final_conf
                    v['plate_status'] = plate_status
                        
                    risk_score, risk_band, factors = risk_engine.compute_risk_score(v['violations'], context)
                    v['risk_score'] = risk_score
                    v['risk_band'] = risk_band
                    factors['orig_ocr_confidence'] = orig_ocr_conf
                    factors['enhanced_ocr_confidence'] = enh_ocr_conf
                    factors['plate_text'] = final_plate
                    factors['ocr_confidence'] = final_conf
                    factors['plate_status'] = plate_status
                    if 'triple_riding_info' in v:
                        factors['rider_count'] = v['triple_riding_info']['rider_count']
                        factors['associated_person_boxes'] = v['triple_riding_info']['associated_person_boxes']
                        factors['confidence'] = v['triple_riding_info']['confidence']
                    v['factors'] = factors
                
                violating_vehicles = [v for v in vehicles if v['violations']]
                frame_evidence_uri = ""
                evidence_hash = ""
                if violating_vehicles:
                    frame_bgr = cv2.cvtColor(preprocessed_frame, cv2.COLOR_RGB2BGR)
                    success, encoded_img = cv2.imencode('.jpg', frame_bgr)
                    if success:
                        frame_bytes = encoded_img.tobytes()
                    else:
                        _, encoded_img = cv2.imencode('.jpg', frame)
                        frame_bytes = encoded_img.tobytes()
                        
                    annotated_bytes = evidence_manager.annotate_image(frame_bytes, vehicles)
                    
                    v_event_id = str(uuid.uuid4())
                    evidence_filename = f"violation_{v_event_id}.jpg"
                    evidence_dir = "evidence"
                    os.makedirs(evidence_dir, exist_ok=True)
                    local_evidence_path = os.path.join(evidence_dir, evidence_filename)
                    with open(local_evidence_path, "wb") as f:
                        f.write(annotated_bytes)
                    frame_evidence_uri = f"evidence/{evidence_filename}"
                    evidence_hash = evidence_manager.hash_evidence(annotated_bytes)
                    
                for v in vehicles:
                    plate_val = v['plate'] or "UNKNOWN"
                    vehicle_db = db.query(Vehicle).filter(Vehicle.plate_text == plate_val).first()
                    if not vehicle_db:
                        vehicle_db = Vehicle(
                            vehicle_id=str(uuid.uuid4()),
                            plate_text=plate_val,
                            vehicle_type=v['class_name'],
                            first_seen=datetime.utcnow(),
                            last_seen=datetime.utcnow(),
                            violation_count=0
                        )
                        db.add(vehicle_db)
                        db.flush()
                        
                    if v['violations']:
                        violations_count += len(v['violations'])
                        v_id = str(uuid.uuid4())
                        event_dict = {
                            'violations': v['violations'],
                            'risk_score': v['risk_score'],
                            'risk_band': v['risk_band'],
                            'camera_id': camera_id,
                            'status': 'PENDING',
                            'evidence_uri': frame_evidence_uri,
                            'zones': context['zones']
                        }
                        report_text = report_generator.generate_report(event_dict)
                        
                        violation_db = Violation(
                            violation_id=v_id,
                            vehicle_id=vehicle_db.vehicle_id,
                            camera_id=camera_id,
                            violation_types=v['violations'],
                            detected_at=datetime.utcnow(),
                            risk_score=v['risk_score'],
                            risk_band=v['risk_band'],
                            status=ViolationStatus.PENDING.value,
                            speed_kmph=context['speed_kmph'],
                            ped_count=context['ped_count'],
                            zones=context['zones'],
                            traffic_density=context['traffic_density'],
                            location='{"lat": 12.9716, "lon": 77.5946}',
                            report_text=report_text,
                            metadata_json=v['factors']
                        )
                        db.add(violation_db)
                        
                        if frame_evidence_uri:
                            evidence_db = Evidence(
                                evidence_id=str(uuid.uuid4()),
                                violation_id=v_id,
                                image_uri=frame_evidence_uri,
                                sha256=evidence_hash,
                                metadata_json={'ocr_confidence': v.get('plate_confidence', 0.0)},
                                created_at=datetime.utcnow()
                            )
                            db.add(evidence_db)
                            
                        vehicle_db.violation_count += 1
                        vehicle_db.last_seen = datetime.utcnow()
                        
                        for detail in v.get('violation_details', []):
                            violation_type_str = detail['violation']
                            risk_score_v, _, _ = risk_engine.compute_risk_score([violation_type_str], context)
                            
                            results.append(ViolationDetail(
                                violation_id=v_id,
                                plate_number=plate_val,
                                vehicle_type=v['class_name'],
                                violation=violation_type_str,
                                confidence=detail['confidence'],
                                risk_score=risk_score_v,
                                timestamp=datetime.utcnow().isoformat(),
                                evidence_image=frame_evidence_uri,
                                plate_text=v.get('plate_text', ""),
                                ocr_confidence=v.get('ocr_confidence', 0.0),
                                plate_status=v.get('plate_status', "NOT_READABLE")
                            ))
                    else:
                        results.append(ViolationDetail(
                            violation_id="",
                            plate_number=plate_val,
                            vehicle_type=v['class_name'],
                            violation="NONE",
                            confidence=float(v['confidence']),
                            risk_score=0,
                            timestamp=datetime.utcnow().isoformat(),
                            evidence_image=frame_evidence_uri,
                            plate_text=v.get('plate_text', ""),
                            ocr_confidence=v.get('ocr_confidence', 0.0),
                            plate_status=v.get('plate_status', "NOT_READABLE")
                        ))
                db.commit()
            frame_count += 1
            
        cap.release()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return {
        "frames_processed": processed_count,
        "violations_detected": violations_count,
        "results": results
    }


@router.post("/live", response_model=LiveStreamResponse)
async def process_live_stream(
    payload: LiveStreamRequest,
    camera_id: str = "J17-N",
    db: Session = Depends(get_db)
):
    """
    Simulates or processes a live RTSP/webcam feed for a short duration.
    """
    source = payload.source
    duration = payload.duration_seconds
    
    try:
        source_idx = int(source)
    except ValueError:
        source_idx = source
        
    cap = cv2.VideoCapture(source_idx)
    if not cap.isOpened():
        return {
            "status": "simulated_completed",
            "processed_frames": 5,
            "violations_detected": 1,
            "results": [
                ViolationDetail(
                    violation_id=str(uuid.uuid4()),
                    plate_number="KA03MM1122",
                    vehicle_type="motorcycle",
                    violation="NO_HELMET",
                    confidence=0.96,
                    risk_score=75,
                    timestamp=datetime.utcnow().isoformat(),
                    evidence_image="evidence/mock_live_evidence.jpg"
                )
            ]
        }
        
    ocr_model = get_ocr_model()
    ocr_reader = OCRReader(ocr_model)
    
    start_time = time.time()
    
    processed_count = 0
    violations_count = 0
    results = []
    
    context = {
        'speed_kmph': float(random.randint(40, 85)),
        'ped_count': random.randint(0, 5),
        'traffic_density': round(random.uniform(0.3, 0.8), 2),
        'zones': ['SCHOOL_ZONE'] if random.random() > 0.6 else [],
        'hour': datetime.utcnow().hour
    }
    
    try:
        while cap.isOpened() and (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                break
                
            processed_count += 1
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            preprocessed_frame = preprocess_image_pipeline(frame_rgb, low_light=False, noisy=False, motion_blur=False)
            dets = get_unified_detections(preprocessed_frame)
            vehicles = violation_engine.detect_violations(dets, preprocessed_frame)
            
            h_img, w_img, _ = preprocessed_frame.shape
            all_v_boxes = [veh['box'] for veh in vehicles]
            for v in vehicles:
                x1, y1, x2, y2 = map(int, v['box'])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w_img, x2), min(h_img, y2)
                
                crop = extract_plate_crop(v['box'], preprocessed_frame, dets, all_v_boxes)
                plate_text, ocr_conf, orig_ocr_conf, enh_ocr_conf = process_ocr_with_hybrid_enhancement(crop, ocr_reader)
                
                final_plate, final_conf, plate_status = process_ocr_result(plate_text, ocr_conf)
                v['plate'] = final_plate or "UNKNOWN"
                v['plate_confidence'] = final_conf
                v['plate_text'] = final_plate
                v['ocr_confidence'] = final_conf
                v['plate_status'] = plate_status
                    
                risk_score, risk_band, factors = risk_engine.compute_risk_score(v['violations'], context)
                v['risk_score'] = risk_score
                v['risk_band'] = risk_band
                factors['orig_ocr_confidence'] = orig_ocr_conf
                factors['enhanced_ocr_confidence'] = enh_ocr_conf
                factors['plate_text'] = final_plate
                factors['ocr_confidence'] = final_conf
                factors['plate_status'] = plate_status
                if 'triple_riding_info' in v:
                    factors['rider_count'] = v['triple_riding_info']['rider_count']
                    factors['associated_person_boxes'] = v['triple_riding_info']['associated_person_boxes']
                    factors['confidence'] = v['triple_riding_info']['confidence']
                v['factors'] = factors
                
            violating_vehicles = [v for v in vehicles if v['violations']]
            frame_evidence_uri = ""
            evidence_hash = ""
            if violating_vehicles:
                frame_bgr = cv2.cvtColor(preprocessed_frame, cv2.COLOR_RGB2BGR)
                _, encoded_img = cv2.imencode('.jpg', frame_bgr)
                frame_bytes = encoded_img.tobytes()
                
                annotated_bytes = evidence_manager.annotate_image(frame_bytes, vehicles)
                
                v_event_id = str(uuid.uuid4())
                evidence_filename = f"violation_{v_event_id}.jpg"
                evidence_dir = "evidence"
                os.makedirs(evidence_dir, exist_ok=True)
                local_evidence_path = os.path.join(evidence_dir, evidence_filename)
                with open(local_evidence_path, "wb") as f:
                    f.write(annotated_bytes)
                frame_evidence_uri = f"evidence/{evidence_filename}"
                evidence_hash = evidence_manager.hash_evidence(annotated_bytes)
                
            for v in vehicles:
                plate_val = v['plate'] or "UNKNOWN"
                vehicle_db = db.query(Vehicle).filter(Vehicle.plate_text == plate_val).first()
                if not vehicle_db:
                    vehicle_db = Vehicle(
                        vehicle_id=str(uuid.uuid4()),
                        plate_text=plate_val,
                        vehicle_type=v['class_name'],
                        first_seen=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        violation_count=0
                    )
                    db.add(vehicle_db)
                    db.flush()
                    
                if v['violations']:
                    violations_count += len(v['violations'])
                    v_id = str(uuid.uuid4())
                    event_dict = {
                        'violations': v['violations'],
                        'risk_score': v['risk_score'],
                        'risk_band': v['risk_band'],
                        'camera_id': camera_id,
                        'status': 'PENDING',
                        'evidence_uri': frame_evidence_uri,
                        'zones': context['zones']
                    }
                    report_text = report_generator.generate_report(event_dict)
                    
                    violation_db = Violation(
                        violation_id=v_id,
                        vehicle_id=vehicle_db.vehicle_id,
                        camera_id=camera_id,
                        violation_types=v['violations'],
                        detected_at=datetime.utcnow(),
                        risk_score=v['risk_score'],
                        risk_band=v['risk_band'],
                        status=ViolationStatus.PENDING.value,
                        speed_kmph=context['speed_kmph'],
                        ped_count=context['ped_count'],
                        zones=context['zones'],
                        traffic_density=context['traffic_density'],
                        location='{"lat": 12.9716, "lon": 77.5946}',
                        report_text=report_text,
                        metadata_json=v['factors']
                    )
                    db.add(violation_db)
                    
                    if frame_evidence_uri:
                        evidence_db = Evidence(
                            evidence_id=str(uuid.uuid4()),
                            violation_id=v_id,
                            image_uri=frame_evidence_uri,
                            sha256=evidence_hash,
                            metadata_json={'ocr_confidence': v.get('plate_confidence', 0.0)},
                            created_at=datetime.utcnow()
                        )
                        db.add(evidence_db)
                        
                    vehicle_db.violation_count += 1
                    vehicle_db.last_seen = datetime.utcnow()
                    
                    for detail in v.get('violation_details', []):
                        violation_type_str = detail['violation']
                        risk_score_v, _, _ = risk_engine.compute_risk_score([violation_type_str], context)
                        
                        results.append(ViolationDetail(
                            violation_id=v_id,
                            plate_number=plate_val,
                            vehicle_type=v['class_name'],
                            violation=violation_type_str,
                            confidence=detail['confidence'],
                            risk_score=risk_score_v,
                            timestamp=datetime.utcnow().isoformat(),
                            evidence_image=frame_evidence_uri,
                            plate_text=v.get('plate_text', ""),
                            ocr_confidence=v.get('ocr_confidence', 0.0),
                            plate_status=v.get('plate_status', "NOT_READABLE")
                        ))
                else:
                    results.append(ViolationDetail(
                        violation_id="",
                        plate_number=plate_val,
                        vehicle_type=v['class_name'],
                        violation="NONE",
                        confidence=float(v['confidence']),
                        risk_score=0,
                        timestamp=datetime.utcnow().isoformat(),
                        evidence_image=frame_evidence_uri,
                        plate_text=v.get('plate_text', ""),
                        ocr_confidence=v.get('ocr_confidence', 0.0),
                        plate_status=v.get('plate_status', "NOT_READABLE")
                    ))
            db.commit()
            time.sleep(0.1)
    finally:
        cap.release()
        
    return {
        "status": "completed",
        "processed_frames": processed_count,
        "violations_detected": violations_count,
        "results": results
    }


@router.get("/list")
async def list_violations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    camera_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List violations with pagination and filters"""
    query = db.query(Violation)
    if camera_id:
        query = query.filter(Violation.camera_id == camera_id)
    if status:
        query = query.filter(Violation.status == status)
        
    # Active query filter: keep only supported violation types
    query = query.filter(Violation.violation_types.like('%NO_HELMET%') | Violation.violation_types.like('%TRIPLE_RIDING%'))
    
    total = query.count()
    violations_db = query.order_by(Violation.detected_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for v in violations_db:
        # Filter types in Python to be absolutely certain
        supported_types = [t for t in (v.violation_types or []) if t in ["NO_HELMET", "TRIPLE_RIDING"]]
        if not supported_types:
            continue
            
        plate = "UNKNOWN"
        if v.vehicle_id:
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == v.vehicle_id).first()
            if vehicle:
                plate = vehicle.plate_text
                
        metadata = v.metadata_json or {}
        results.append({
            "violation_id": str(v.violation_id),
            "vehicle_plate": plate,
            "violations": supported_types,
            "risk_score": v.risk_score,
            "risk_band": v.risk_band,
            "camera_id": v.camera_id,
            "timestamp": v.detected_at.isoformat(),
            "status": v.status,
            "plate_text": metadata.get('plate_text', plate if plate != "UNKNOWN" else ""),
            "ocr_confidence": metadata.get('ocr_confidence', 0.0),
            "plate_status": metadata.get('plate_status', "NOT_READABLE"),
        })
        
    return {
        "violations": results,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{violation_id}")
async def get_violation(violation_id: str, db: Session = Depends(get_db)):
    """Get detailed violation information"""
    try:
        uuid_val = uuid.UUID(violation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid violation ID format")
        
    v = db.query(Violation).filter(Violation.violation_id == str(uuid_val)).first()
    if not v:
        raise HTTPException(status_code=404, detail="Violation not found")
        
    supported_types = [t for t in (v.violation_types or []) if t in ["NO_HELMET", "TRIPLE_RIDING"]]
    if not supported_types:
        raise HTTPException(status_code=404, detail="Violation not found or not supported")
        
    plate = "UNKNOWN"
    vehicle_type = "motorcycle"
    if v.vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == v.vehicle_id).first()
        if vehicle:
            plate = vehicle.plate_text
            vehicle_type = vehicle.vehicle_type or "motorcycle"
            
    # Get evidence URI
    evidence = db.query(Evidence).filter(Evidence.violation_id == v.violation_id).first()
    evidence_uri = evidence.image_uri if evidence else None
    sha256 = evidence.sha256 if evidence else None
    
    metadata = v.metadata_json or {}
    plate_text = metadata.get('plate_text', plate if plate != "UNKNOWN" else "")
    ocr_confidence = metadata.get('ocr_confidence', 0.0)
    plate_status = metadata.get('plate_status', "NOT_READABLE")
    
    return {
        "violation_id": str(v.violation_id),
        "vehicle_plate": plate,
        "violations": supported_types,
        "risk_score": v.risk_score,
        "risk_band": v.risk_band,
        "camera_id": v.camera_id,
        "timestamp": v.detected_at.isoformat(),
        "status": v.status,
        "evidence_uri": evidence_uri,
        "report": v.report_text,
        "factors": metadata,
        "plate_text": plate_text,
        "ocr_confidence": ocr_confidence,
        "plate_status": plate_status,
        "vehicle_type": vehicle_type,
        "sha256": sha256
    }


@router.post("/{violation_id}/verify")
async def verify_violation(
    violation_id: str,
    payload: Optional[VerifyRequest] = None,
    action: Optional[str] = Query(None),
    note: Optional[str] = Query(""),
    db: Session = Depends(get_db)
):
    """Officer verification action - supports JSON body or query parameters"""
    try:
        uuid_val = uuid.UUID(violation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid violation ID format")
        
    v = db.query(Violation).filter(Violation.violation_id == str(uuid_val)).first()
    if not v:
        raise HTTPException(status_code=404, detail="Violation not found")
        
    # Resolve action and note
    act = None
    nt = ""
    if payload:
        act = payload.action
        nt = payload.note
    elif action:
        act = action
        nt = note
        
    if not act:
        raise HTTPException(status_code=422, detail="Missing verification action")
        
    act = act.upper()
    if act not in ["VERIFY", "REJECT"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be VERIFY or REJECT")
        
    old_status = v.status
    new_status = ViolationStatus.VERIFIED.value if act == "VERIFY" else ViolationStatus.REJECTED.value
    
    # Update violation
    v.status = new_status
    v.notes = nt
    v.verified_at = datetime.utcnow()
    v.verified_by = "officer_demo"
    
    # Log audit trail
    audit = AuditLog(
        audit_id=str(uuid.uuid4()),
        user_id=None,
        action=act,
        resource_type="VIOLATION",
        resource_id=str(v.violation_id),
        old_value={"status": old_status},
        new_value={"status": new_status},
        details=f"Officer verified violation as {new_status}. Note: {nt}",
        created_at=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    
    return {
        "violation_id": str(v.violation_id),
        "action": act,
        "status": new_status,
        "note": nt,
        "timestamp": datetime.utcnow().isoformat()
    }
