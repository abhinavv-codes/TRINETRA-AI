import os
import cv2
import gdown
import torch
import numpy as np
import torch.nn.functional as F
import sys
import yaml

from .enhancer import BaseEnhancementModel
from pathlib import Path


BASE_DIR = Path(__file__).parent

RESTORMER_DIR = BASE_DIR / "Restormer"

sys.path.append(
    str(RESTORMER_DIR)
)
from basicsr.models.archs.restormer_arch import Restormer

WEIGHTS_DIR = BASE_DIR / "weights"

WEIGHT_PATH = (
    WEIGHTS_DIR
    / "motion_deblurring.pth"
)

url = "https://drive.google.com/uc?id=1izDnH8Qr0ovzjXvngf2oHbNpbDnRDnqr"

def download_restormer():

    WEIGHTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    gdown.download(
        url,
        str(WEIGHT_PATH),
        quiet=False
    )

def load_restormer(device):

    if not WEIGHT_PATH.exists():

        print(
            "Downloading Restormer weights..."
        )

        download_restormer()

    yaml_file = (
        RESTORMER_DIR
        / "Motion_Deblurring"
        / "Options"
        / "Deblurring_Restormer.yml"
    )

    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    network_cfg = config["network_g"]

    network_cfg.pop(
        "type",
        None
    )

    model = Restormer(
        **network_cfg
    ).to(device)

    checkpoint = torch.load(
        WEIGHT_PATH,
        map_location=device
    )

    model.load_state_dict(
        checkpoint["params"]
    )

    model.eval()

    print(
        "Restormer Loaded Successfully"
    )

    return model


class RestormerModel(BaseEnhancementModel):

    def __init__(self, model, device):
        self.model = model
        self.device = device

    def enhance(self, frame):

        original_h, original_w = frame.shape[:2]

        MAX_WIDTH = 640
    
        scale = 1.0
    
        if original_w > MAX_WIDTH:
    
            scale = MAX_WIDTH / original_w
    
            new_w = int(original_w * scale)
            new_h = int(original_h * scale)
    
            frame = cv2.resize(
                frame,
                (new_w, new_h),
                interpolation=cv2.INTER_AREA
            )
        
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        img = rgb.astype(
            np.float32
        ) / 255.0

        img = torch.from_numpy(img)\
                   .permute(2, 0, 1)\
                   .unsqueeze(0)\
                   .to(self.device)

        h, w = img.shape[2], img.shape[3]

        factor = 8

        H = ((h + factor) // factor) * factor
        W = ((w + factor) // factor) * factor

        padh = H - h if h % factor != 0 else 0
        padw = W - w if w % factor != 0 else 0

        img = F.pad(
            img,
            (0, padw, 0, padh),
            mode="reflect"
        )

        try:

            with torch.no_grad():
                restored = self.model(img)

        except Exception as e:

            print(
                f"Restormer failed: {e}"
            )

            return frame

        restored = restored[:, :, :h, :w]

        restored = torch.clamp(
            restored,
            0,
            1
        )

        restored = restored.squeeze(0)\
                           .permute(1, 2, 0)\
                           .cpu()\
                           .numpy()

        restored = (
            restored * 255
        ).astype(np.uint8)

        restored = cv2.cvtColor(
            restored,
            cv2.COLOR_RGB2BGR
        )

        if scale != 1.0:

            restored = cv2.resize(
                restored,
                (original_w, original_h),
                interpolation=cv2.INTER_LINEAR
            )
        
        return restored