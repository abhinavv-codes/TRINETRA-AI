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

from app.inference.model_loader import load_models, get_ocr_model, get_yolo_model
from app.inference.ocr import OCRReader
from app.inference.yolo import YOLODetector
from app.utils.preprocessing import preprocess_crop_for_ocr
from app.inference.enhancement.pipeline import initialize_pipeline

def main():
    print("1. Loading models...", flush=True)
    load_models()
    print("2. Retrieving model instances...", flush=True)
    yolo_model = get_yolo_model()
    ocr_model = get_ocr_model()
    
    detector_yolo = YOLODetector(yolo_model)
    ocr_reader = OCRReader(ocr_model)
    
    print("3. Loading test image...", flush=True)
    image_path = r"C:\Users\acer\.gemini\antigravity-ide\brain\5136487d-2184-4108-835d-85d84a5d4499\traffic_motorcycle_1781883048249.png"
    img = cv2.imread(image_path)
    if img is None:
        print("Image not found!", flush=True)
        return
        
    print(f"4. Running YOLO detection. Image shape: {img.shape}", flush=True)
    dets = detector_yolo.detect(img)
    print("   YOLO detection complete.", flush=True)
    
    # Find motorcycle
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
        print("   No motorcycle detected, using fallback", flush=True)
        motorcycle_box = [0, 0, img.shape[1], img.shape[0]]
        
    print(f"5. Extracting plate crop from box: {motorcycle_box}", flush=True)
    from app.routers.violations import extract_plate_crop
    crop = extract_plate_crop(motorcycle_box, img, dets)
    print(f"   Crop extracted. Shape: {crop.shape}", flush=True)
    
    print("6. Preprocessing crop for OCR...", flush=True)
    orig_ocr_crop = preprocess_crop_for_ocr(crop)
    print(f"   Preprocessed shape: {orig_ocr_crop.shape}", flush=True)
    
    print("7. Running initial PaddleOCR on original crop...", flush=True)
    orig_text, orig_conf = ocr_reader.read_plate(orig_ocr_crop)
    print(f"   Initial OCR complete. Text: '{orig_text}', Conf: {orig_conf}", flush=True)
    
    if orig_conf >= 0.85:
        print("8. OCR confidence >= 85%, done.", flush=True)
        return
        
    print("8. OCR confidence < 85%, running enhancement unconditionally...", flush=True)
    enhancer = initialize_pipeline()
    print("   Running Zero-DCE + Restormer on crop...", flush=True)
    enhanced_crop = enhancer.execute(crop, ["brightness", "deblur"])
    print("   Enhancement complete.", flush=True)
    
    print("9. Preprocessing enhanced crop for OCR...", flush=True)
    enhanced_ocr_crop = preprocess_crop_for_ocr(enhanced_crop)
    print("10. Running PaddleOCR on enhanced crop...", flush=True)
    enhanced_text, enhanced_conf = ocr_reader.read_plate(enhanced_ocr_crop)
    print(f"    Enhanced OCR complete. Text: '{enhanced_text}', Conf: {enhanced_conf}", flush=True)

if __name__ == "__main__":
    main()
