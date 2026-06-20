import os
import gdown
import cv2
import torch
import numpy as np

from .enhancer import BaseEnhancementModel
from pathlib import Path
from .zero_dce_arch import enhance_net_nopool

BASE_DIR = Path(__file__).parent

WEIGHTS_DIR = BASE_DIR / "weights"

WEIGHT_PATH = (
    WEIGHTS_DIR
    / "Epoch99.pth"
)

url = "https://drive.google.com/uc?id=1zT16PNQxpp1X_EwNM5OlEthYKGaeq0WA"

def download_zero_dce():

    WEIGHTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    gdown.download(
        url,
        str(WEIGHT_PATH),
        quiet=False
    )

def load_zero_dce(device):

    if not WEIGHT_PATH.exists():
        print("Downloading Zero-DCE weights...")
        download_zero_dce()

    model = enhance_net_nopool()

    model.load_state_dict(
        torch.load(
            WEIGHT_PATH,
            map_location=device
        )
    )

    model.to(device)
    model.eval()

    return model


class ZeroDCEModel(BaseEnhancementModel):

    def __init__(self, model, device):

        self.model = model
        self.device = device

    def enhance(self, frame):

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

        try:

            with torch.no_grad():

                _, enhanced, _ = self.model(img)

        except Exception as e:

            print(
                f"Zero-DCE failed: {e}"
            )

            return frame

        enhanced = enhanced.squeeze(0)\
                           .permute(1, 2, 0)\
                           .cpu()\
                           .numpy()

        enhanced = np.clip(
            enhanced,
            0,
            1
        )

        enhanced = (
            enhanced * 255
        ).astype(np.uint8)

        enhanced = cv2.cvtColor(
            enhanced,
            cv2.COLOR_RGB2BGR
        )

        return enhanced