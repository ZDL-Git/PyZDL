import numpy as np

from zdl.utils.media.point import Point


class Rect:
    def __init__(self, xyxy=None, yxyx=None, xywh=None):
        if xyxy is not None:
            self.xyxy = np.asarray(xyxy)
            self.yxyx = self.xyxy[[1, 0, 3, 2]]
            self.xywh = self.xyxy - [0, 0, self.xyxy[0], self.xyxy[1]]
            self.w, self.h = self.xywh[-2:]
        elif yxyx is not None:
            self.yxyx = np.asarray(yxyx)
            self.xyxy = self.yxyx[[1, 0, 3, 2]]
            self.xywh = self.xyxy - [0, 0, self.xyxy[0], self.xyxy[1]]
            self.w, self.h = self.xywh[-2:]
        elif xywh is not None:
            self.xywh = np.asarray(xywh)
            self.xyxy = self.xywh + [0, 0, xywh[0], xywh[1]]
            self.yxyx = self.xyxy[[1, 0, 3, 2]]
            self.w, self.h = xywh[2], xywh[3]
        else:
            raise ValueError('xyxy/yxyx/xywh, one of them must have a value!')
        self.c_l, self.r_t, self.c_r, self.r_b = self.xyxy

    def toInt(self) -> 'Rect':
        return self.__class__(xyxy=self.xyxy.astype(int))

    def diagonal(self):
        return (self.w ** 2 + self.h ** 2) ** 0.5

    def center(self):
        return Point(self.xyxy[0] + self.w / 2, self.xyxy[1] + self.h / 2)
