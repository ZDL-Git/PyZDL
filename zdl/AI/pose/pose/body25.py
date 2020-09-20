from zdl.AI.pose.pose.pose import Pose


class BODY25(Pose):
    NAME = 'BODY_25'

    def __init__(self, key_points):
        super(BODY25, self).__init__(key_points)

    @property
    def parts_indices(self):
        # right to left, up to down.
        indices = {}
        indices['face'] = [15, 16, 17, 18]
        indices['shoulder'] = [2, 5]
        indices['arm_right'] = [2, 3, 4]
        indices['arm_left'] = [5, 6, 7]
        indices['arms'] = indices['arm_right'] + indices['arm_left']
        indices['crotch'] = [9, 12]
        indices['knee'] = [10, 13]
        indices['foot_right'] = [22, 23, 24]
        indices['foot_left'] = [19, 20, 21]
        indices['feet'] = indices['foot_right'] + indices['foot_left']
        indices['knee_and_below'] = [10, 11, 13, 14, 19, 20, 21, 22, 23, 24]

        return indices

    @property
    def sections(self):
        return [[17, 15, 0, 16, 18], [0, 1, 8], [1, 2, 3, 4], [1, 5, 6, 7], [8, 9, 10, 11],
                [8, 12, 13, 14], [11, 23, 22, 11, 24], [14, 20, 19, 14, 21]]
