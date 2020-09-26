from abc import ABC, abstractmethod
from typing import List, Type

import numpy as np
from numba import jit
from zdl.utils.helper.numpy import ndarrayLen
from zdl.utils.io.log import logger
from zdl.utils.media.point import Point


class Pose(ABC):
    def __init__(self, key_points: np.ndarray):
        assert key_points.ndim == 2, f'Should be a 2D pose! shape: {key_points.shape}'
        self.key_points = key_points
        self._center = None

    @property
    @abstractmethod
    def NAME(self):
        pass

    @property
    @abstractmethod
    def SHAPE(self):
        pass

    @property
    @abstractmethod
    def PARTS_INDICES(self):
        # right to left, up to down
        pass

    @property
    @abstractmethod
    def sections(self):
        pass

    # TODO: switch to abstract
    # @abstractmethod
    def meanBoneLength(self, pose):
        pass

    def shoulderBreadth(self):
        r_shoulder, l_shoulder = self.PARTS_INDICES['shoulder']
        if self.key_points[r_shoulder][0] > 0 and self.key_points[l_shoulder][0] > 0:
            breadth = abs(self.key_points[r_shoulder][0] - self.key_points[l_shoulder][0])
        else:
            breadth = 0
        return breadth

    def torsoHeight(self):
        indices = self.PARTS_INDICES
        r_shoulder, l_shoulder = indices['shoulder'][0], indices['shoulder'][-1]
        r_crotch, l_crotch = indices['crotch'][0], indices['crotch'][-1]
        right_height = abs(self.key_points[r_shoulder][1] - self.key_points[r_crotch][1]) \
            if self.key_points[r_shoulder][1] > 0 and self.key_points[r_crotch][1] > 0 else 0
        left_height = abs(self.key_points[l_shoulder][1] - self.key_points[l_crotch][1]) \
            if self.key_points[l_shoulder][1] > 0 and self.key_points[l_crotch][1] > 0 else 0
        # Log.debug(f'r_shoulder {pose[r_shoulder]},l_shoulder {pose[l_shoulder]},r_crotch {pose[r_crotch]},l_crotch {pose[l_crotch]}')
        return (right_height + left_height) / 2 if right_height and left_height else (right_height or left_height)

    def _isZero(self):
        return not np.any(self.key_points != 0)

    @classmethod
    def newZeroPose(cls):
        return cls(key_points=np.zeros((25, 4), dtype=np.float32))

    def cleanup(self, body_parts: list, copy=False):
        if ndarrayLen(self.key_points) == 0: return self
        if copy:
            cleaning = self.key_points.copy()
        else:
            cleaning = self.key_points
            self._center = None
        for part in body_parts:
            cleaning[self.PARTS_INDICES[part]] = 0
        return cleaning

    def center(self, need_type=None):
        if self._center is None:
            key_points = self.cleanup(['face', 'feet'], copy=True)
            self._center = Point.pointsCenter(key_points, need_type)
        return self._center

    @classmethod
    def distance(cls, pose1: np.ndarray, pose2: np.ndarray, algorithm='Manhattan'):
        if algorithm == 'Manhattan':
            func = cls.manhattanDistance
        elif algorithm == 'Euclidean':
            func = cls.euclideanDistance
        else:
            raise Exception
        return func(pose1, pose2)

    def distanceTo(self, another: 'Pose', algorithm='Manhattan'):
        if algorithm == 'Manhattan':
            func = self.manhattanDistance
        elif algorithm == 'Euclidean':
            func = self.euclideanDistance
        else:
            raise Exception
        return func(self.key_points, another.key_points)

    @classmethod
    # @jit
    def manhattanDistance(cls, pose1, pose2):
        pose1, pose2 = np.asarray(pose1), np.asarray(pose2)
        pose1_nonzero_b, pose2_nonzero_b = pose1 != 0, pose2 != 0
        pose1_x_or_y_nonzero = np.logical_or(pose1_nonzero_b[..., 0], pose1_nonzero_b[..., 1])
        pose2_x_or_y_nonzero = np.logical_or(pose2_nonzero_b[..., 0], pose2_nonzero_b[..., 1])
        pose1_pose2_xy_nonzero = np.logical_and(pose1_x_or_y_nonzero, pose2_x_or_y_nonzero)
        if np.any(pose1_pose2_xy_nonzero):
            dis = abs((pose1 - pose2)[..., :2])
            # Remove the maximum
            r, c = np.unravel_index(np.argmax(dis, axis=None), dis.shape)
            pose1_pose2_xy_nonzero[r] = False
            mean_dis = dis[pose1_pose2_xy_nonzero].mean()
        else:
            logger.debug("Poses haven't same nonzero index points, change to use center point dis!")
            pose1_x_mean, pose1_y_mean = np.split(pose1[..., :2][pose1_x_or_y_nonzero].mean(axis=0), 2, axis=0) \
                                             if np.any(pose1_x_or_y_nonzero) else [0], [0]
            pose2_x_mean, pose2_y_mean = np.split(pose2[..., :2][pose2_x_or_y_nonzero].mean(axis=0), 2, axis=0) \
                                             if np.any(pose2_x_or_y_nonzero) else [0], [0]
            mean_dis = (pose1_x_mean[0] - pose2_x_mean[0] + pose1_y_mean[0] - pose2_y_mean[0]) / 2
        return mean_dis

    @classmethod
    @jit
    def euclideanDistance(cls, pose1, pose2):
        pose1xy, pose2xy = pose1[..., :2], pose2[..., :2]
        pose1_positive, pose2_positive = pose1[..., 2] > 0, pose2[..., 2] > 0
        pose1_pose2_positive = np.logical_and(pose1_positive, pose2_positive)
        pose1_pose2_positive_num = pose1_pose2_positive.sum()
        if pose1_pose2_positive_num:
            # Remove the maximum
            x2_plus_y2 = (pose1xy - pose2xy) ** 2
            dis_sum = (x2_plus_y2[..., 0] + x2_plus_y2[..., 1]) ** 0.5
            dis_sum_max = dis_sum.max()
            mean_dis = (dis_sum[pose1_pose2_positive].sum() - dis_sum_max) / (pose1_pose2_positive_num - 1)
        else:
            logger.debug("Poses haven't same nonzero index points, change to use center point dis!")
            mean_dis = Point.dis(cls(pose1).center(), cls(pose2).center())
        return mean_dis


class Poses:
    def __init__(self, all_keypoints, pose_type: Type[Pose]):
        """

        :param all_keypoints:
        :param pose_type: class - body25.BODY25 etc.
        """
        assert all_keypoints.ndim in [0, 3], 'poses shape error!'
        self.all_keypoints = all_keypoints
        self.pose_type = pose_type
        self.poses = [pose_type(keypoints) for keypoints in all_keypoints] if all_keypoints.ndim == 3 else []

    def __iter__(self):
        return iter(self.poses)

    def __getitem__(self, i):
        return self.poses[i]

    def __len__(self):
        return len(self.poses)

    @property
    def PARTS_INDICES(self):
        return self.pose_type.PARTS_INDICES

    def cleanup(self, body_parts: List):
        for pose in self.poses:
            pose.cleanup(body_parts)

    def centers(self, need_type=list):
        return [pose.center(need_type) for pose in self.poses]
