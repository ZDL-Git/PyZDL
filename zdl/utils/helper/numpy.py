import numpy as np


def ndarrayLen(array: np.ndarray):
    """
    兼容 shape==() 的情况，返回 len:0
    :param array:
    :return:
    """
    return array.shape and array.shape[0] or 0
