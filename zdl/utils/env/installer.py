from abc import abstractmethod, ABCMeta

from zdl.utils.env.terminal import Terminal


class Installer(Terminal, metaclass=ABCMeta):
    @abstractmethod
    def _prepare(self):
        pass

    @abstractmethod
    def install(self):
        pass

    @abstractmethod
    def test(self):
        pass
