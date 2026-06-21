"""Violation detection engine - rules for 7+ violation types"""

import logging
import re
import random
from typing import List, Dict, Optional
import numpy as np
import cv2
from app.core.constants import ViolationType

logger = logging.getLogger(__name__)

def associate_plates_to_vehicles(vehicle_boxes: List[List[float]], plate_boxes: List[List[float]]) -> Dict[int, List[float]]:
    """
    Map each plate to its nearest vehicle using Euclidean distance between centers.
    Returns a dict: v_idx -> plate_box (List[float])
    """
    v_to_plate = {}
    v_to_best_dist = {}
    
    for p_box in plate_boxes:
        pcx = (p_box[0] + p_box[2]) / 2.0
        pcy = (p_box[1] + p_box[3]) / 2.0
        
        min_dist = float('inf')
        nearest_v_idx = -1
        
        for v_idx, v_box in enumerate(vehicle_boxes):
            vcx = (v_box[0] + v_box[2]) / 2.0
            vcy = (v_box[1] + v_box[3]) / 2.0
            
            dist = ((pcx - vcx) ** 2 + (pcy - vcy) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest_v_idx = v_idx
                
        if nearest_v_idx != -1:
            # Associate this plate to the vehicle. If the vehicle already has an associated plate, keep the closer one.
            if nearest_v_idx not in v_to_plate or min_dist < v_to_best_dist[nearest_v_idx]:
                v_to_plate[nearest_v_idx] = p_box
                v_to_best_dist[nearest_v_idx] = min_dist
                
    return v_to_plate


class ViolationEngine:
    """Rule-based traffic violation detection using YOLO detections and image features"""
    
    def __init__(self):
        pass
        
    def _is_overlapping(self, box_person: List[float], box_moto: List[float]) -> bool:
        """Check if person box overlaps with motorcycle box"""
        px1, py1, px2, py2 = box_person
        mx1, my1, mx2, my2 = box_moto
        
        ix1 = max(px1, mx1)
        iy1 = max(py1, my1)
        ix2 = min(px2, mx2)
        iy2 = min(py2, my2)
        
        inter_area = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
        person_area = (px2 - px1) * (py2 - py1)
        
        if person_area == 0:
            return False
            
        overlap = inter_area / person_area
        return overlap > 0.35

    def _detect_traffic_light_color(self, image: np.ndarray, box: List[float]) -> str:
        """Crop traffic light and check if RED, GREEN, or UNKNOWN in HSV"""
        try:
            h_img, w_img, _ = image.shape
            x1, y1, x2, y2 = map(int, box)
            
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_img, x2), min(h_img, y2)
            
            crop = image[y1:y2, x1:x2]
            h, w, _ = crop.shape
            
            if h < 6:
                return "UNKNOWN"
                
            top_third = crop[0:int(h/3), :]
            bottom_third = crop[int(2*h/3):h, :]
            
            top_hsv = cv2.cvtColor(top_third, cv2.COLOR_RGB2HSV)
            bottom_hsv = cv2.cvtColor(bottom_third, cv2.COLOR_RGB2HSV)
            
            # Red color range
            red_mask1 = cv2.inRange(top_hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
            red_mask2 = cv2.inRange(top_hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
            red_count = np.sum(red_mask1 > 0) + np.sum(red_mask2 > 0)
            
            # Green color range
            green_mask = cv2.inRange(bottom_hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
            green_count = np.sum(green_mask > 0)
            
            if red_count > green_count and red_count > 5:
                return "RED"
            elif green_count > red_count and green_count > 5:
                return "GREEN"
            return "UNKNOWN"
        except Exception as e:
            logger.error(f"Traffic light color detection failed: {e}")
            return "UNKNOWN"

    def detect_no_helmet(self, vehicle: Dict, persons: List[Dict], detections: Dict) -> Optional[Dict]:
        """Detect helmet violations (motorcycles and bikes only)"""
        class_names = detections.get("class_names", {})
        classes_detected = detections.get("classes", [])
        boxes = detections.get("boxes", [])
        
        v_box = vehicle['box']
        
        # Look for custom 'no-helmet' class detected by helmet_best.pt
        no_helmet_class_id = None
        for cid, name in class_names.items():
            if name.lower() == 'no-helmet':
                no_helmet_class_id = cid
                break
                
        if no_helmet_class_id is not None:
            for i, box in enumerate(boxes):
                if int(classes_detected[i]) == no_helmet_class_id:
                    if self._is_overlapping(box.tolist(), v_box):
                        return {
                            "violation": ViolationType.NO_HELMET.value,
                            "confidence": float(detections.get("confidences", [])[i])
                        }
        return None

    def detect_triple_riding(self, vehicle: Dict, persons: List[Dict]) -> Optional[Dict]:
        """Detect triple riding (carrying 3+ people on bike/motorcycle)"""
        v_box = vehicle['box']
        vx1, vy1, vx2, vy2 = v_box
        
        associated_persons = []
        for p in persons:
            p_box = p['box']
            px1, py1, px2, py2 = p_box
            pcx = (px1 + px2) / 2.0
            pcy = (py1 + py2) / 2.0
            
            is_assoc = False
            # Check center point inclusion
            if (vx1 <= pcx <= vx2) and (vy1 <= pcy <= vy2):
                is_assoc = True
            # Or check overlap area ratio
            elif self._is_overlapping(p_box, v_box):
                is_assoc = True
                
            if is_assoc:
                associated_persons.append(p)
                
        if len(associated_persons) >= 3:
            # Average confidence of bike and all associated persons
            confidences = [vehicle['confidence']] + [p['confidence'] for p in associated_persons]
            avg_conf = float(np.mean(confidences))
            
            return {
                "violation": ViolationType.TRIPLE_RIDING.value,
                "confidence": avg_conf,
                "rider_count": len(associated_persons),
                "associated_person_boxes": [p['box'] for p in associated_persons]
            }
        return None

    def detect_no_seatbelt(self, vehicle: Dict, persons: List[Dict], detections: Dict) -> Optional[Dict]:
        """Seatbelt detection model is removed; returns None"""
        return None

    def detect_wrong_side(self, vehicle: Dict) -> Optional[Dict]:
        """Wrong side detection heuristic is disabled; returns None"""
        return None

    def detect_stop_line(self, vehicle: Dict, detections: Dict) -> Optional[Dict]:
        """Stop line crossing heuristic is disabled; returns None"""
        return None

    def detect_red_light_jump(self, vehicle: Dict, traffic_lights: List[Dict], image: np.ndarray) -> Optional[Dict]:
        """Red light jump detection is disabled; returns None"""
        return None

    def detect_illegal_parking(self, vehicle: Dict, detections: Dict) -> Optional[Dict]:
        """Illegal parking heuristic is disabled; returns None"""
        return None

    def detect_violations(self, detections: Dict, image: np.ndarray = None) -> List[Dict]:
        """
        Detect violations for each vehicle in the scene.
        Associates person, plate, and helmet boxes with the vehicles.
        """
        boxes = detections.get("boxes", [])
        classes = detections.get("classes", [])
        confidences = detections.get("confidences", [])
        class_names = detections.get("class_names", {})
        
        if len(boxes) == 0:
            return []
            
        vehicles = []
        persons = []
        traffic_lights = []
        
        for i, box in enumerate(boxes):
            class_id = int(classes[i])
            name = class_names.get(class_id, "")
            conf = float(confidences[i])
            
            det_obj = {
                'box': box.tolist(),
                'class_name': name,
                'confidence': conf,
                'violations': [],
                'violation_details': [],
                'plate': None,
                'associated_plate_box': None,
                'associated_helmet_boxes': [],
                'associated_person_boxes': []
            }
            
            if name in ['car', 'motorcycle', 'bus', 'truck', 'bike']:
                vehicles.append(det_obj)
            elif name == 'person':
                persons.append(det_obj)
            elif name == 'traffic light':
                traffic_lights.append(det_obj)

        # Precompute vehicle to plate associations using Euclidean distance
        vehicle_boxes = [v['box'] for v in vehicles]
        plate_boxes = []
        for i, box in enumerate(boxes):
            name = class_names.get(int(classes[i]), "")
            if name == 'License_Plate':
                plate_boxes.append(box.tolist())
                
        v_to_plate = associate_plates_to_vehicles(vehicle_boxes, plate_boxes)

        # Evaluate violations and associate boxes for each vehicle
        for v_idx, v in enumerate(vehicles):
            v_type = v['class_name']
            v_box = v['box']
            vx1, vy1, vx2, vy2 = v_box
            
            # Find associated plate box (using precomputed nearest-vehicle mapping)
            if v_idx in v_to_plate:
                v['associated_plate_box'] = v_to_plate[v_idx]
            
            # Find associated helmet and no-helmet boxes
            associated_helmet_boxes = []
            for i, box in enumerate(boxes):
                name = class_names.get(int(classes[i]), "")
                if name in ['helmet', 'no-helmet']:
                    if self._is_overlapping(box.tolist(), v_box):
                        associated_helmet_boxes.append({
                            "box": box.tolist(),
                            "class_name": name,
                            "confidence": float(confidences[i])
                        })
            v['associated_helmet_boxes'] = associated_helmet_boxes
            
            # Find associated person boxes (riders)
            associated_person_boxes = []
            for p in persons:
                p_box = p['box']
                px1, py1, px2, py2 = p_box
                pcx = (px1 + px2) / 2.0
                pcy = (py1 + py2) / 2.0
                is_assoc = False
                if (vx1 <= pcx <= vx2) and (vy1 <= pcy <= vy2):
                    is_assoc = True
                elif self._is_overlapping(p_box, v_box):
                    is_assoc = True
                if is_assoc:
                    associated_person_boxes.append(p_box)
            v['associated_person_boxes'] = associated_person_boxes

            # 1. Helmet violations
            if v_type in ['motorcycle', 'bike']:
                helmet = self.detect_no_helmet(v, persons, detections)
                if helmet:
                    v['violations'].append(helmet["violation"])
                    v['violation_details'].append(helmet)
                    
            # 2. Triple riding
            if v_type in ['motorcycle', 'bike']:
                triple = self.detect_triple_riding(v, persons)
                if triple:
                    v['violations'].append(triple["violation"])
                    v['violation_details'].append(triple)
                    v['triple_riding_info'] = {
                        'rider_count': triple['rider_count'],
                        'associated_person_boxes': triple['associated_person_boxes'],
                        'confidence': triple['confidence']
                    }
                    
            # 3. No seatbelt
            seatbelt = self.detect_no_seatbelt(v, persons, detections)
            if seatbelt:
                v['violations'].append(seatbelt["violation"])
                v['violation_details'].append(seatbelt)
                
            # 4. Wrong side driving
            wrong_side = self.detect_wrong_side(v)
            if wrong_side:
                v['violations'].append(wrong_side["violation"])
                v['violation_details'].append(wrong_side)
                
            # 5. Stop line crossing
            stop_line = self.detect_stop_line(v, detections)
            if stop_line:
                v['violations'].append(stop_line["violation"])
                v['violation_details'].append(stop_line)
                
            # 6. Red light jump
            red_light = self.detect_red_light_jump(v, traffic_lights, image)
            if red_light:
                v['violations'].append(red_light["violation"])
                v['violation_details'].append(red_light)
                
            # 7. Illegal parking
            parking = self.detect_illegal_parking(v, detections)
            if parking:
                v['violations'].append(parking["violation"])
                v['violation_details'].append(parking)

        return vehicles
