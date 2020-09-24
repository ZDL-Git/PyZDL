from zdl.utils.media.rect import Rect


class ObjectDetected:
    def __init__(self, class_name: str, bbox: Rect, score: float):
        self.class_name = class_name
        self.bbox = bbox
        self.score = score
