class Bbox:
    def __init__(self, xyxy):
        self.xmin, self.ymin, self.xmax, self.ymax = xyxy


class ObjectDetected:
    def __init__(self, bbox: Bbox, class_name: str, score: float):
        self.class_name = class_name
        self.bbox = bbox
        self.score = score
