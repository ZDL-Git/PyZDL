from abc import ABC, abstractmethod


class Extractor(ABC):
    model_path = None

    @abstractmethod
    def extract(self, img):
        pass

    @classmethod
    def setModel(cls, path):
        cls.model_path = path
