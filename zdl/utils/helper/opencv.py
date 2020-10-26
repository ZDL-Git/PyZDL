from typing import Optional

import cv2


def countFrames(vname: Optional[str] = None, cap: Optional[cv2.VideoCapture] = None):
    cap = cap or cv2.VideoCapture(vname)
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    return count
