import numpy as np


class Rect:
    def __init__(self, xyxy=None, yxyx=None, xywh=None):
        if xyxy:
            self.xyxy = np.asarray(xyxy)
            self.w, self.h = self.xyxy[[2, 3]] - self.xyxy[[0, 1]]
        elif yxyx:
            self.xyxy = np.asarray(yxyx)[[1, 0, 3, 2]]
            self.w, self.h = self.xyxy[[2, 3]] - self.xyxy[[0, 1]]
        elif xywh:
            self.xyxy = np.asarray(xywh) + [0, 0, xywh[0], xywh[1]]
            self.w, self.h = xywh[2], xywh[3]
        else:
            raise ValueError('xyxy/yxyx/xywh, one of them must have a value!')
        self.c_l, self.r_t, self.c_r, self.r_b = self.xyxy

