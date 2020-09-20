from zdl.AI.pose.pose.pose import Pose


class COCO(Pose):
    NAME = 'COCO'

    def __init__(self, key_points):
        super(COCO, self).__init__(key_points)

    @property
    def parts_indices(self):
        # right to left, up to down.
        indices = {}
        indices['face'] = [0, 14, 15, 16, 17]
        indices['shoulder'] = [2, 5]
        indices['arm_right'] = [2, 3, 4]
        indices['arm_left'] = [5, 6, 7]
        indices['arms'] = indices['arm_right'] + indices['arm_left']
        indices['crotch'] = [8, 11]
        indices['knee'] = [9, 12]
        indices['foot_right'] = []
        indices['foot_left'] = []
        indices['feet'] = indices['foot_right'] + indices['foot_left']
        indices['knee_and_below'] = [9, 12, 10, 13]

        return indices

    @property
    def sections(self):
        return [[16, 14, 0, 15, 17], [0, 1], [1, 2, 3, 4], [1, 5, 6, 7], [1, 8, 9, 10], [1, 11, 12, 13]]
