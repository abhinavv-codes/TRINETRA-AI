"""Evidence storage - save and hash evidence images"""

import logging
import hashlib
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class EvidenceManager:
    """Manage evidence images with tamper-detection"""
    
    def hash_evidence(self, image_bytes: bytes, prev_hash: str = None) -> str:
        """
        Generate SHA-256 hash of evidence
        
        Args:
            image_bytes: Image binary data
            prev_hash: Previous hash (for chain)
        
        Returns:
            SHA-256 hash hex string
        """
        
        if prev_hash:
            combined = image_bytes + prev_hash.encode()
        else:
            combined = image_bytes
        
        return hashlib.sha256(combined).hexdigest()
    
    def create_evidence_record(
        self,
        violation_id: str,
        image_bytes: bytes,
        prev_hash: str = None,
        metadata: dict = None
    ) -> Dict:
        """
        Create tamper-evident evidence record
        
        Args:
            violation_id: Associated violation ID
            image_bytes: Image binary data
            prev_hash: Previous hash for chain
            metadata: Additional metadata
        
        Returns:
            Evidence record dict with hash and chain
        """
        
        # Generate hash chain
        image_hash = self.hash_evidence(image_bytes, prev_hash)
        
        return {
            "violation_id": violation_id,
            "sha256": image_hash,
            "prev_hash": prev_hash,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
    
    def verify_evidence_chain(self, records: list) -> bool:
        """Verify integrity of evidence chain"""
        
        for i in range(len(records)):
            if i == 0:
                continue
            
            current = records[i]
            previous = records[i-1]
            
            if current.get('prev_hash') != previous.get('sha256'):
                logger.warning(f"Chain break detected at record {i}")
                return False
        
        return True

    def annotate_image(
        self,
        image_bytes: bytes,
        detections: List[Dict]
    ) -> bytes:
        """
        Draw bounding boxes and labels on evidence image
        
        Args:
            image_bytes: Image binary data
            detections: List of dicts with keys:
                - box: [x1, y1, x2, y2]
                - class_name: e.g. "car", "bike", "motorcycle"
                - plate: e.g. "KA05AB1234"
                - violations: list of string violation types
                - associated_person_boxes: list of rider boxes
                - associated_plate_box: plate box
                - associated_helmet_boxes: list of dicts with box and class_name
        """
        import cv2
        import numpy as np
        
        try:
            # Decode image bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.warning("Failed to decode image bytes for annotation")
                return image_bytes
                
            for det in detections:
                box = det.get('box')
                if box is None:
                    continue
                x1, y1, x2, y2 = map(int, box)
                
                # Check if it has violations
                violations = det.get('violations', [])
                # BGR: Red for violations, Green for clean
                color = (0, 0, 255) if violations else (0, 255, 0)
                
                # 1. Draw main vehicle bounding box
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                # Prepare label text
                label = f"{det.get('class_name', 'vehicle').upper()}"
                plate = det.get('plate')
                if plate:
                    label += f" | {plate}"
                
                # Draw text background
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                cv2.rectangle(img, (x1, y1 - 15), (x1 + tw, y1), color, -1)
                cv2.putText(img, label, (x1, y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
                
                # 2. Draw associated plate bounding box (Cyan)
                plate_box = det.get('associated_plate_box')
                if plate_box:
                    px1, py1, px2, py2 = map(int, plate_box)
                    cv2.rectangle(img, (px1, py1), (px2, py2), (255, 255, 0), 2)
                    cv2.putText(img, "PLATE", (px1, py1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 0), 1, cv2.LINE_AA)
                
                # 3. Draw associated person bounding boxes (Blue)
                for p_box in det.get('associated_person_boxes', []):
                    rx1, ry1, rx2, ry2 = map(int, p_box)
                    cv2.rectangle(img, (rx1, ry1), (rx2, ry2), (255, 0, 0), 2)
                    cv2.putText(img, "RIDER", (rx1, ry1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 0), 1, cv2.LINE_AA)
                
                # 4. Draw associated helmet/no-helmet bounding boxes (Green for helmet, Red for no-helmet)
                for h_det in det.get('associated_helmet_boxes', []):
                    hx1, hy1, hx2, hy2 = map(int, h_det['box'])
                    h_name = h_det['class_name'].upper()
                    h_color = (0, 255, 0) if h_name == 'HELMET' else (0, 0, 255)
                    cv2.rectangle(img, (hx1, hy1), (hx2, hy2), h_color, 2)
                    cv2.putText(img, h_name, (hx1, hy1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.35, h_color, 1, cv2.LINE_AA)
                
                # 5. Draw violations below box if any
                if violations:
                    v_label = f"VIOLATION: {', '.join(violations)}"
                    (vw, vh), _ = cv2.getTextSize(v_label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                    cv2.rectangle(img, (x1, y2), (x1 + vw, y2 + 15), (0, 0, 255), -1)
                    cv2.putText(img, v_label, (x1, y2 + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
                    
            # Encode back to bytes
            success, encoded_img = cv2.imencode('.jpg', img)
            if success:
                return encoded_img.tobytes()
                
            return image_bytes
        except Exception as e:
            logger.error(f"Image annotation failed: {e}")
            return image_bytes
