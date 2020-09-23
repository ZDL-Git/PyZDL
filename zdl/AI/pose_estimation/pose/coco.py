from zdl.AI.pose_estimation.pose.pose import Pose


class COCO(Pose):
    NAME = 'COCO'
    PARTS_INDICES = {
        'face': [0, 14, 15, 16, 17],
        'shoulder': [2, 5],
        'arm_right': [2, 3, 4],
        'arm_left': [5, 6, 7],
        'arms': [2, 3, 4, 5, 6, 7],
        'crotch': [8, 11],
        'knee': [9, 12],
        'foot_right': [],
        'foot_left': [],
        'feet': [],
        'knee_and_below': [9, 12, 10, 13],
    }

    def __init__(self, key_points):
        super(COCO, self).__init__(key_points)

    @property
    def sections(self):
        return [[16, 14, 0, 15, 17], [0, 1], [1, 2, 3, 4], [1, 5, 6, 7], [1, 8, 9, 10], [1, 11, 12, 13]]
