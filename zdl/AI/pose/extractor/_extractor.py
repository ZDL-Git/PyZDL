from abc import ABC, abstractmethod
from typing import Union, List, Callable

import cv2
import numpy as np
from zdl.utils.io.log import darkThemeColorLogger as logger


class Extractor(ABC):
    model_path = None

    def __init__(self):
        self.pre_hooks = []

    @classmethod
    def setModel(cls, path):
        cls.model_path = path

    @abstractmethod
    def callExtractorCore(self, img):
        # should return extracted result
        pass

    def addPreHooks(self, hook_or_hooks: Union[Callable, List[Callable[[Union[np.ndarray]], Union[np.ndarray]]]]):
        if isinstance(hook_or_hooks, Callable):
            self.pre_hooks.append(hook_or_hooks)
        elif isinstance(hook_or_hooks, List):
            self.pre_hooks += hook_or_hooks
        else:
            raise TypeError('hook_or_hooks type error!')
        return self

    def callPreHooks(self, img):
        # all hooks should work in-place
        for h in self.pre_hooks:
            h(img)

    def extract(self, img, silent=False):
        # entry function
        if not silent:
            if isinstance(img, str):
                img = cv2.imread(img)
            logger.debug(img.shape)

        self.callPreHooks(img)
        extracted = self.callExtractorCore(img)
        return extracted
