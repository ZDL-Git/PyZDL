import numpy as np

from zdl.AI.pose_estimation.pose.base_pose import BasePose
from zdl.utils.env.gpu import GPU


class BODY25B(BasePose):
    NAME = 'BODY_25B'
    SHAPE = (25, 3)
    PARTS_INDICES = {
        'face': [0, 1, 2, 3, 4],
        'shoulder': [6, 5],
        'arm_right': [6, 8, 10],
        'arm_left': [5, 7, 9],
        'arms': [6, 8, 10, 5, 7, 9],
        'crotch': [12, 11],
        'knee': [14, 13],
        'foot_right': [22, 23, 24],
        'foot_left': [19, 20, 21],
        'feet': [22, 23, 24, 19, 20, 21],
        'knee_and_below': [13, 14, 15, 16, 19, 20, 21, 22, 23, 24],
    }
    SECTIONS = [[4, 2, 0, 1, 3], [18, 17, 6, 12, 11, 5, 17], [6, 8, 10], [5, 7, 9], [12, 14, 16],
                [11, 13, 15], [16, 22, 23, 16, 24], [15, 19, 20, 15, 21]]

    def __init__(self, key_points: np.ndarray, add_inherit_flag_col: bool = True):
        assert GPU.supported(), 'BODY_25B only supports GPU mode!'
        super(BODY25B, self).__init__(key_points, add_inherit_flag_col)
