import cv2
import numpy as np


class QualityAssessment:

    def __init__(
        self,
        blur_threshold=100,
        brightness_threshold=60,
    ):
        self.blur_threshold = blur_threshold
        self.brightness_threshold = brightness_threshold

    def blur_score(self, frame):
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        return cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

    def brightness_score(self, frame):
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        return np.mean(gray)

    def contrast_score(self, frame):
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        return np.std(gray)

    def assess(self, frame):

        return {
            "blur": self.blur_score(frame),
            "brightness": self.brightness_score(frame),
            "contrast": self.contrast_score(frame),
        }

    def decide(self, frame):

        scores = self.assess(frame)

        pipeline = []

        if scores["brightness"] < self.brightness_threshold:
            pipeline.append("brightness")

        if (
            scores["brightness"] > 30
            and
            scores["blur"] < self.blur_threshold
        ):
            pipeline.append("deblur")

        return {
            "scores": scores,
            "pipeline": pipeline,
        }