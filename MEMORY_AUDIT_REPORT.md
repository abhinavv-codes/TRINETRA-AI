# TRINETRA AI - Production Memory & Inference Audit Report

This report presents a detailed audit of the memory footprint and CPU inference overhead of the TRINETRA AI backend, detailing the root cause of the "Memory Limit Exceeded" crash on Render and providing a clear path to resolution.

---

## 🛑 1. Exact Root Cause of the Crash

The backend starts up successfully on Render's Free Tier because we previously removed startup-time model loading. When the container boots, it consumes only baseline memory (~100 MB).

However, as soon as the first request to `/api/v1/violations/detect` is received, the following sequence occurs:
1. **YOLO Models Loading**: The system lazily loads three separate YOLOv8 models (`yolov8n.pt`, `helmet_best.pt`, and `plate_best.pt`). This raises the RAM consumption from **~100 MB** to **~460 MB**.
2. **PaddleOCR Loading**: The system reaches the OCR detection step and calls `get_ocr_model()`. The logs print `"Loading PaddleOCR (lazy initialization)..."`.
3. **Out of Memory (OOM)**: Instantiating PaddleOCR imports the PaddlePaddle framework and loads its text detection, classification, and recognition models. This requires an additional **~400 MB** of memory, driving total RAM to **~860 MB**.
4. **Crash**: Because the Render Free Tier has a hard limit of **512 MB**, the container immediately crosses the limit, and the Render scheduler terminates the process (OOM SIGKILL).

---

## 📊 2. Memory Footprint Estimates (CPU)

Below is an estimation of RAM usage during the model lifecycle on CPU:

| Model / Component | Weights Size | Loaded RAM Footprint | Peak Inference RAM (Transient) |
| :--- | :--- | :--- | :--- |
| **FastAPI Baseline** | N/A | ~100 MB | ~10 MB |
| **YOLOv8 General (`yolov8n.pt`)** | 6.5 MB | ~100 MB | ~20 MB |
| **YOLOv8 Helmet (`helmet_best.pt`)** | 22.5 MB | ~130 MB | ~20 MB |
| **YOLOv8 Plate (`plate_best.pt`)** | 22.5 MB | ~130 MB | ~20 MB |
| **PaddleOCR** | ~18.5 MB | ~400 MB | ~100 MB |
| **Zero-DCE (Low-light)** | 0.32 MB | ~25 MB | ~10 MB |
| **Restormer (Deblurring)** | 104.7 MB | ~450 MB | ~300 MB - ~500 MB (transient) |
| **Total (All Loaded & Running)**| **~175 MB** | **~1.34 GB** | **~480 MB - ~680 MB** |

### Projected Combined RAM Demands:
* **Idle (FastAPI baseline only)**: **~100 MB**
* **YOLO Only (No OCR/Enhancement)**: **~460 MB** (Fits inside 512 MB)
* **YOLO + PaddleOCR (No Enhancement)**: **~860 MB** (Requires >1 GB)
* **Full Pipeline (YOLO + OCR + Enhancements)**: **~1.34 GB - 1.8 GB** (Requires >2 GB)

---

## 🛠️ 3. Singleton & Caching Verification

Our audit of the codebase confirms:
1. **YOLO Models**: Properly loaded and cached as singletons (`_yolo_model`, `_helmet_model`, `_plate_model` in `model_loader.py`). They are loaded once on demand and kept in memory.
2. **PaddleOCR**: Cached as a singleton (`_ocr_model` in `model_loader.py`).
3. **Enhancement Pipeline**: Cached as a global singleton (`enhancer` in `pipeline.py`).
4. **Per-Request Memory**: No new model instances are recreated per request. However, memory spikes during execution due to transient crop images, PyTorch activation tensors (especially Restormer's self-attention maps), and PaddlePaddle memory structures.

---

## ⚙️ 4. Recommended Environment Flags for Render

To allow the application to run smoothly under resource-constrained environments like Render Free Tier, we propose adding two new feature flags:

### A. `ENABLE_IMAGE_ENHANCEMENT` (Default: `false` in production)
* **Purpose**: Completely bypasses the quality assessment, Zero-DCE, and Restormer deblurring pipeline for OCR crops.
* **RAM Saved**: **~450 MB** baseline RAM and up to **~500 MB** transient peak RAM.
* **Tradeoff**: Marginally lower OCR reading accuracy on highly blurred or dark license plate crops, but essential to fit within standard servers.

### B. `ENABLE_OCR` (Default: `true`)
* **Purpose**: When set to `false`, it completely bypasses the PaddleOCR step and returns blank plate strings/UNREADABLE status, executing only the YOLO object, helmet, and plate detection.
* **RAM Saved**: **~400 MB** baseline RAM and **~100 MB** inference RAM.
* **Tradeoff**: Disables text extraction, but allows running the full violation detection engine (e.g., Helmet detection, Triple Riding detection) within the Render Free Tier (512 MB).

---

## 📈 5. Recommended Render Instance Size

* **To run the YOLO-only platform**: **Free Tier (512 MB RAM)** is sufficient with `ENABLE_OCR=false` and `ENABLE_IMAGE_ENHANCEMENT=false`.
* **To run YOLO + PaddleOCR (No Enhancements)**: **Starter Tier (1 GB RAM)** is required with `ENABLE_IMAGE_ENHANCEMENT=false`.
* **To run the Full Pipeline (YOLO + OCR + Restormer/Zero-DCE)**: **Individual / Standard Tier (2 GB RAM)** is required.
