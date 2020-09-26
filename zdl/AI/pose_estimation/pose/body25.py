import numpy as np

from zdl.AI.pose_estimation.pose.pose import Pose


class BODY25(Pose):
    NAME = 'BODY_25'
    SHAPE = (25, 3)
    PARTS_INDICES = {
        'face': [15, 16, 17, 18],
        'shoulder': [2, 5],
        'arm_right': [2, 3, 4],
        'arm_left': [5, 6, 7],
        'arms': [2, 3, 4, 5, 6, 7],
        'crotch': [9, 12],
        'knee': [10, 13],
        'foot_right': [22, 23, 24],
        'foot_left': [19, 20, 21],
        'feet': [22, 23, 24, 19, 20, 21],
        'knee_and_below': [10, 11, 13, 14, 19, 20, 21, 22, 23, 24],
    }

    def __init__(self, key_points: np.ndarray, add_inherit_flag_col: bool = True):
        super(BODY25, self).__init__(key_points, add_inherit_flag_col)

    @property
    def sections(self):
        return [[17, 15, 0, 16, 18], [0, 1, 8], [1, 2, 3, 4], [1, 5, 6, 7], [8, 9, 10, 11],
                [8, 12, 13, 14], [11, 23, 22, 11, 24], [14, 20, 19, 14, 21]]
