class Rect:
    def __init__(self, xyxy=None, yxyx=None, xywh=None):
        if xyxy:
            pass
        elif yxyx:
            xyxy = yxyx[1], yxyx[0], yxyx[3], yxyx[2]
        elif xywh:
            xyxy = xywh[0], xywh[1], xywh[0] + xywh[2], xywh[1] + xywh[3]
        else:
            raise ValueError('xyxy/yxyx/xywh, one of them must have a value!')
        self.c_l, self.r_t, self.c_r, self.r_b = xyxy
        self.w, self.h = xyxy[2] - xyxy[0], xyxy[3] - xyxy[1]
