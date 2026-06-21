"""Image preprocessing utilities using OpenCV"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


def apply_denoising(image: np.ndarray) -> np.ndarray:
    """
    Apply fastNlMeansDenoisingColored to reduce noise (e.g., from rain or high ISO)
    """
    try:
        # Check if color or grayscale
        if len(image.shape) == 3 and image.shape[2] == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    except Exception as e:
        logger.error(f"Denoising failed: {e}")
        return image


def apply_equalize_hist(image: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization to improve contrast (especially in low light/shadow)
    """
    try:
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Convert to YCrCb space to equalize only luminance
            ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
            channels = list(cv2.split(ycrcb))
            channels[0] = cv2.equalizeHist(channels[0])
            ycrcb = cv2.merge(channels)
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
        else:
            return cv2.equalizeHist(image)
    except Exception as e:
        logger.error(f"Histogram equalization failed: {e}")
        return image


def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Apply Gaussian Blur to smooth image and reduce high-frequency noise
    """
    try:
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    except Exception as e:
        logger.error(f"Gaussian Blur failed: {e}")
        return image


def apply_contrast_brightness(image: np.ndarray, alpha: float = 1.2, beta: int = 10) -> np.ndarray:
    """
    Adjust contrast and brightness using convertScaleAbs
    """
    try:
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    except Exception as e:
        logger.error(f"convertScaleAbs failed: {e}")
        return image


def preprocess_image_pipeline(
    image: np.ndarray,
    low_light: bool = False,
    noisy: bool = False,
    motion_blur: bool = False
) -> np.ndarray:
    """
    Run full preprocessing pipeline based on image environmental conditions
    """
    processed = image.copy()
    
    # 1. Denoise if noisy (rain/grain)
    if noisy:
        processed = apply_denoising(processed)
    
    # 2. Equalize histogram if low light/shadows
    if low_light:
        processed = apply_equalize_hist(processed)
    
    # 3. Smooth with Gaussian Blur
    processed = apply_gaussian_blur(processed)
    
    # 4. Sharpen and adjust contrast for motion blur / default contrast
    alpha = 1.3 if motion_blur else 1.15
    beta = 5 if low_light else 0
    processed = apply_contrast_brightness(processed, alpha=alpha, beta=beta)
    
    return processed


def preprocess_crop_for_ocr(crop: np.ndarray) -> np.ndarray:
    """
    Specific preprocessing optimized for OCR extraction from vehicle/plate crop
    """
    if crop is None or crop.size == 0:
        return crop
        
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
        
        # Apply gentle blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Equalize contrast
        equalized = cv2.equalizeHist(blurred)
        
        # Convert back to RGB because PaddleOCR works best on color crops
        return cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)
    except Exception as e:
        logger.error(f"OCR preprocessing failed: {e}")
        return crop
