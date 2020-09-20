from zdl.utils.env.gpu import GPU

from zdl.AI.pose.pose.pose import Pose


class BODY25B(Pose):
    NAME = 'BODY_25B'

    def __init__(self, key_points):
        super(BODY25B, self).__init__(key_points)
        assert GPU.supported(), 'BODY_25B only supports GPU mode!'

    @property
    def parts_indices(self):
        # right to left, up to down.
        indices = {}
        indices['face'] = [0, 1, 2, 3, 4]
        indices['shoulder'] = [6, 5]
        indices['arm_right'] = [6, 8, 10]
        indices['arm_left'] = [5, 7, 9]
        indices['arms'] = indices['arm_right'] + indices['arm_left']
        indices['crotch'] = [12, 11]
        indices['knee'] = [14, 13]
        indices['foot_right'] = [22, 23, 24]
        indices['foot_left'] = [19, 20, 21]
        indices['feet'] = indices['foot_right'] + indices['foot_left']
        indices['knee_and_below'] = [13, 14, 15, 16, 19, 20, 21, 22, 23, 24]

        return indices

    @property
    def sections(self):
        return [[4, 2, 0, 1, 3], [18, 17, 6, 12, 11, 5, 17], [6, 8, 10], [5, 7, 9], [12, 14, 16],
                [11, 13, 15], [16, 22, 23, 16, 24], [15, 19, 20, 15, 21]]
