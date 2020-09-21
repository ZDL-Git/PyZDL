import os
from abc import abstractmethod, ABCMeta

from zdl.utils.io.log import logger

FIGSIZE = [12.8, 9.6]
# FIGSIZE=[20,15]
IMG_SUFFIXES = ['.jpeg', '.png', '.jpg']
VIDEO_SUFFIXES = ['.mp4', '.avi', '.mkv', '.flv']


class Media(metaclass=ABCMeta):
    def __init__(self, fname=None):
        if fname is not None:
            assert os.path.isfile(fname), f'{fname} not exists!'
        self.fname = fname

    @abstractmethod
    def getInfo(self):
        pass

    def info(self):
        logger.info(self.getInfo())
        return self

    @abstractmethod
    def show(self):
        pass
