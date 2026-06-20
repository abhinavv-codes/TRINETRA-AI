class BaseEnhancementModel:

    def enhance(self, frame):
        raise NotImplementedError


class ImageEnhancer:

    def __init__(self, models):
        self.models = models

    def execute(
        self,
        frame,
        pipeline,
    ):
        enhanced = frame.copy()

        for operation in pipeline:

            if operation not in self.models:
                continue

            enhanced = self.models[
                operation
            ].enhance(enhanced)

        return enhanced