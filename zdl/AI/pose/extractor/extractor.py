from abc import ABC, abstractmethod
from typing import Union, List, Callable, Type

import cv2
import numpy as np
from zdl.utils.io.log import logger

from zdl.AI.pose.pose.pose import Pose


class Extractor(ABC):

    def __init__(self):
        self.model_path = None
        self.pre_hooks = []
        self.pose_type: Type[Pose] = None

    @abstractmethod
    def _callExtractorCore(self, img):
        # should return extracted result
        pass

    def _callPreHooks(self, img):
        # all hooks should work in-place
        for h in self.pre_hooks:
            h(img)

    def setModel(self, path):
        self.model_path = path
        return self

    def addPreHooks(self, hook_or_hooks: Union[Callable, List[Callable[[np.ndarray], None]]]):
        if isinstance(hook_or_hooks, Callable):
            self.pre_hooks.append(hook_or_hooks)
        elif isinstance(hook_or_hooks, List):
            self.pre_hooks += hook_or_hooks
        else:
            raise TypeError('hook_or_hooks type error!')
        return self

    def extract(self, img, silent=False):
        # entry function
        if not silent:
            if isinstance(img, str):
                img = cv2.imread(img)
            logger.debug(img.shape)

        self._callPreHooks(img)
        pose = self._callExtractorCore(img)
        return pose
