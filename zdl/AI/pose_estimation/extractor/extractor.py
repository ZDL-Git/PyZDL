from abc import ABC, abstractmethod
from typing import Union, List, Callable, Type, Tuple

import cv2
import numpy as np

from zdl.AI.helper.openpose import DatumPickleable
from zdl.AI.pose_estimation.pose.pose import Pose, Poses
from zdl.utils.io.log import logger


class Extractor(ABC):
    model_path = None

    def __init__(self):
        self.pre_hooks = []
        self.post_hooks = []
        self.pose_type: Type[Pose] = None

    @abstractmethod
    def _callExtractorCore(self, img):
        # should return extracted result
        pass

    def _callPreHooks(self, img):
        # all hooks should work in-place
        for h in self.pre_hooks:
            h(img)

    def _callPostHooks(self, poses: Poses, others):
        for h in self.post_hooks:
            h(poses, others)

    @classmethod
    def setModel(cls, path):
        cls.model_path = path

    def addPreHooks(self, hook_or_hooks: Union[Callable, List[Callable[[np.ndarray], None]]]):
        if isinstance(hook_or_hooks, Callable):
            self.pre_hooks.append(hook_or_hooks)
        elif isinstance(hook_or_hooks, List):
            self.pre_hooks += hook_or_hooks
        else:
            raise TypeError('hook_or_hooks type error!')
        return self

    def addPostHooks(self, hook_or_hooks: Union[Callable[[np.ndarray], None], List[Callable[[np.ndarray], None]]]):
        if isinstance(hook_or_hooks, Callable):
            self.post_hooks.append(hook_or_hooks)
        elif isinstance(hook_or_hooks, List):
            self.post_hooks += hook_or_hooks
        else:
            raise TypeError('hook_or_hooks type error!')
        return self

    def extract(self, img, silent=True) -> Tuple[Poses, DatumPickleable]:
        # entry function
        if not silent:
            if isinstance(img, str):
                img = cv2.imread(img)
            logger.debug(img.shape)

        self._callPreHooks(img)
        poses, datum = self._callExtractorCore(img)
        self._callPostHooks(poses, datum)
        return poses, datum
