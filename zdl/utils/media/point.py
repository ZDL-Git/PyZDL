from statistics import mean

import numpy as np


class Point:
    # _Point = namedtuple('_Point',['x','y'])
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def _ndim2PointsCenter(cls, points, need_type=None):
        points = np.asarray(points)
        x_array, y_array = points[:, 0], points[:, 1]
        x_or_y_positive = np.logical_or(x_array > 0, y_array > 0)
        center = [mean(x_array[x_or_y_positive]), mean(y_array[x_or_y_positive])] \
            if np.any(x_or_y_positive) else [0, 0]
        if need_type is None:
            center = cls(*center)
        elif need_type == list:
            center = center
        elif need_type == tuple:
            center = tuple(center)
        return center

    @classmethod
    def pointsCenter(cls, points, need_type=None):
        if points == []:
            return []
        # ndim 2 to 3
        # points_array.shape = (1,)+points_array.shape
        points_array = np.asarray(points)
        if points_array.ndim == 2:
            return cls._ndim2PointsCenter(points_array, need_type)
        elif points_array.ndim == 3:
            center_points = []
            for p_points in points_array:
                center_points.append(cls._ndim2PointsCenter(p_points, need_type))
            return center_points
        else:
            raise NotImplementedError('Only 2D/3D is supported!')

    @classmethod
    def dis(cls, point1: 'Point', point2: 'Point'):
        return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5

    def disTo(self, another_point: 'Point'):
        return self.dis(self, another_point)
