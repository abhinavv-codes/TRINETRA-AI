import cv2
import torch

from .quality import QualityAssessment
from .enhancer import ImageEnhancer

from .zerodce import (
    load_zero_dce,
    ZeroDCEModel
)

from .restormer import (
    load_restormer,
    RestormerModel
)


device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

qa = QualityAssessment()

enhancer = None


def initialize_pipeline():

    global enhancer

    if enhancer is not None:
        return enhancer

    print(
        f"Initializing Enhancement Pipeline on {device}"
    )

    zero_dce = load_zero_dce(device)

    restormer = load_restormer(device)

    models = {
        "brightness": ZeroDCEModel(
            zero_dce,
            device
        ),

        "deblur": RestormerModel(
            restormer,
            device
        )
    }

    enhancer = ImageEnhancer(
        models
    )

    print(
        "Enhancement Pipeline Ready"
    )

    return enhancer


def process_frame(frame):

    enhancer_instance = initialize_pipeline()

    decision = qa.decide(frame)

    enhanced = enhancer_instance.execute(
        frame,
        decision["pipeline"]
    )

    return {
        "frame": enhanced,
        "pipeline": decision["pipeline"],
        "scores": decision["scores"]
    }


def process_video(video_path):

    cap = cv2.VideoCapture(
        video_path
    )

    if not cap.isOpened():

        raise ValueError(
            f"Could not open video: {video_path}"
        )

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        yield process_frame(
            frame
        )

    cap.release()