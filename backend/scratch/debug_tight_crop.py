import os
import sys
import cv2
import numpy as np

# Set environment variables to prevent OpenMP/MKL multi-threading deadlocks on Windows CPU
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["FLAGS_use_onednn"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["FLAGS_enable_pir_in_executor"] = "0"

backend_path = r"d:\GRIDLOCK\backend"
sys.path.append(backend_path)

from app.inference.model_loader import load_models, get_ocr_model, get_yolo_model, get_plate_model
from app.inference.ocr import OCRReader
from app.inference.yolo import YOLODetector
from app.routers.violations import extract_plate_crop, process_ocr_with_hybrid_enhancement

def main():
    print("1. Loading models...", flush=True)
    load_models()
    
    yolo_model = get_yolo_model()
    ocr_model = get_ocr_model()
    plate_model = get_plate_model()
    
    detector_yolo = YOLODetector(yolo_model)
    ocr_reader = OCRReader(ocr_model)
    
    print("2. Loading test image...", flush=True)
    image_path = r"C:\Users\acer\.gemini\antigravity-ide\brain\5136487d-2184-4108-835d-85d84a5d4499\traffic_motorcycle_1781883048249.png"
    img = cv2.imread(image_path)
    
    print("3. Running YOLO...", flush=True)
    dets = detector_yolo.detect(img)
    
    # Let's find motorcycle box
    boxes = dets.get("boxes", [])
    classes = dets.get("classes", [])
    class_names = dets.get("class_names", {})
    
    motorcycle_box = None
    for i, box in enumerate(boxes):
        name = class_names.get(int(classes[i]), "")
        if name == 'motorcycle':
            motorcycle_box = box.tolist()
            break
            
    if motorcycle_box is None:
        print("No motorcycle detected")
        return
        
    print(f"4. Motorcycle box: {motorcycle_box}", flush=True)
    
    # Run custom plate model on motorcycle crop
    vx1, vy1, vx2, vy2 = map(int, motorcycle_box)
    vehicle_crop = img[vy1:vy2, vx1:vx2]
    
    print("5. Running custom plate model...", flush=True)
    plate_results = plate_model(vehicle_crop, conf=0.25, verbose=False)
    print(f"   Plate boxes detected: {len(plate_results[0].boxes)}", flush=True)
    
    if len(plate_results[0].boxes) > 0:
        best_box = sorted(plate_results[0].boxes, key=lambda b: float(b.conf[0]), reverse=True)[0]
        px1, py1, px2, py2 = map(int, best_box.xyxy[0].cpu().numpy())
        print(f"   Plate box coordinates inside vehicle crop: [{px1}, {py1}, {px2}, {py2}]", flush=True)
        plate_crop = vehicle_crop[py1:py2, px1:px2]
        print(f"   Plate crop shape: {plate_crop.shape}", flush=True)
        
        # Run OCR
        plate_text, ocr_conf, orig_conf, enh_conf = process_ocr_with_hybrid_enhancement(plate_crop, ocr_reader)
        print(f"   OCR Text: '{plate_text}', Conf: {ocr_conf}", flush=True)
        print(f"   Orig OCR Conf: {orig_conf}, Enh OCR Conf: {enh_conf}", flush=True)
    else:
        print("No plate box detected by plate_model")

if __name__ == "__main__":
    main()
