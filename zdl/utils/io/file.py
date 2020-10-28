import codecs
import hashlib
import json
import os
from abc import abstractmethod, ABCMeta
from typing import Optional

import numpy as np

from zdl.utils.helper.python import ZDict
from zdl.utils.io.log import logger


class FileInfo:
    def __init__(self, path):
        self.uri = path and os.path.abspath(path)
        self.name = self.uri and os.path.basename(self.uri)
        self.hash_md5 = FileHelper.hashOfFile(self.uri)


class AbcFile(FileInfo, metaclass=ABCMeta):
    def __init__(self, path: Optional[str] = None):
        super().__init__(path)
        self.content = None

    def setPath(self, path):
        self.uri = path and os.path.abspath(path)
        self.name = self.uri and os.path.basename(self.uri)

    @abstractmethod
    def dump_hooks(self):
        pass

    @abstractmethod
    def dump(self, path):
        pass

    @classmethod
    @abstractmethod
    def load(cls, path):
        pass


class FileHelper:
    @classmethod
    def loadNpy(cls, path: str) -> np.array:
        return np.load(path)

    @classmethod
    def loadJson(cls, path: str) -> dict:
        with open(path, 'rb') as f:
            content = json.load(f)
        return content

    @classmethod
    def hashOfFile(cls, path: str, fn='md5') -> Optional[str]:
        # BUF_SIZE is totally arbitrary, change for your app!
        # lets read stuff in 500MB chunks!
        if not path:
            return None
        buf_size = 524288000
        if fn == 'md5':
            hash_ = hashlib.md5()
        elif fn == 'sha1':
            hash_ = hashlib.sha1()
        else:
            raise ValueError('fn should be in [md5, sha1]')
        with open(path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                hash_.update(data)
        return hash_.hexdigest()


class StandardFile(FileHelper, AbcFile):
    def __init__(self, path: Optional[str] = None):
        super().__init__(path)

    def hashMd5(self):
        return self.hashOfFile(self.uri)

    def dump_hooks(self):
        pass

    def dump(self, path: Optional[str] = None):
        self.dump_hooks()
        if path:
            self.setPath(path)
        if not self.uri:
            logger.error('No path set for dumping.')
            return False
        with open(self.uri, 'w') as f:
            f.write(self.content)
        logger.debug(f'{self.uri} dump finished.')
        return True

    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            content = f.read()
        obj = cls()
        obj.setPath(path)
        obj.content = content
        logger.debug(f'{path} load finished.')
        return obj


class JsonFile(FileHelper, AbcFile):
    def __init__(self, path: Optional[str] = None):
        super().__init__(path)
        self.content = ZDict({})

    # def __getattr__(self, item):
    #     # only support outermost layer, and don't support set.
    #     return self.content[item]

    # def __setattr__(self, key, value):
    #     # bug not fixed.
    #     logger.debug(f'{key} {value}')
    #     logger.debug(self.__dict__)
    #     self.content[key] = value

    def __getitem__(self, item):
        return self.content[item]

    def __setitem__(self, key, value):
        self.content[key] = value

    def dump_hooks(self):
        pass

    def dump(self, path: Optional[str] = None):
        logger.debug('')
        self.dump_hooks()
        if path:
            self.setPath(path)
        if not self.uri:
            logger.error('No path set for dumping.')
            return False
        with codecs.getwriter("utf8")(open(self.uri, "wb")) as f:
            json.dump(self.content, f, indent=2, ensure_ascii=False)
        return True

    @classmethod
    def load(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        obj = cls()
        obj.setPath(path)
        obj.content = ZDict(content)
        return obj
