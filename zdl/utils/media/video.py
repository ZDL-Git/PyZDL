import os
from functools import reduce
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import pylab
from scipy.spatial import distance as sci_dist

from zdl.utils.io.log import logger
from zdl.utils.media.image import ImageCV
from zdl.utils.media.media import Media, VIDEO_SUFFIXES, FIGSIZE
from zdl.utils.time.counter import timeit


def colabMode():
    from tqdm.notebook import tqdm as note_tqdm
    global tqdm
    tqdm = note_tqdm


class Video(Media):
    def __init__(self, fname):
        assert os.path.isfile(fname), f'{fname} not exists!'
        assert Path(fname).suffix in VIDEO_SUFFIXES, 'file type not supported!'
        self.fname = fname

        self.frame_dict = {}
        self._info = None

    def getInfo(self):
        if self._info is None:
            cap = cv2.VideoCapture(self.fname)
            success, img = cap.read()
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = self._countFrames(cap=cap)
            # frame_has_read_count = len(self.frame_dict)
            duration = frame_count / fps
            # width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float
            # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # float
            self._info = {'fname': self.fname,
                          'frame_c': frame_count,
                          'duration': duration,
                          'shape': img.shape,
                          'width': img.shape[1],
                          'height': img.shape[0],
                          'channels': img.shape[2],
                          'fps': fps}
        return self._info

    def _countFrames(self, cap=None):
        cap = cap or cv2.VideoCapture(self.fname)
        org_pos = cap.get(cv2.CAP_PROP_POS_AVI_RATIO)
        cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        cap.set(cv2.CAP_PROP_POS_AVI_RATIO, org_pos)

        return count

    def clear(self):
        self.frame_dict = {}

    def readFrame(self, index, ImageCV_=False):
        cap = cv2.VideoCapture(self.fname)
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        _, f = cap.read()
        if ImageCV_:
            return ImageCV(f, title=index)
        else:
            return f

    def readDict(self, indices=None, yield_=True):
        info = self.getInfo()
        if indices is None:
            indices = range(info['frame_c'])
        else:
            assert isinstance(indices, Iterable), 'indices shoulb be an iterable obj!'
            assert len(indices) != 0, 'Input indices equals []!'
            indices = [i + info['frame_c'] if i < 0 else i for i in indices]
            indices.sort()
        cap = cv2.VideoCapture(self.fname)
        frame_dict = {}
        p = -1
        for i in tqdm(indices, desc='Fetch Frames'):
            if i >= info['frame_c']:
                logger.warning('index out of video range!')
                break
            if i in self.frame_dict:
                frame = self.frame_dict[i]
            else:
                if i < p + 80:
                    for _ in range(i - p):
                        _, frame = cap.read()
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    _, frame = cap.read()
                p = i
            if yield_:
                yield i, frame
            else:
                frame_dict[i] = frame
        self.frame_dict.update(frame_dict)
        return frame_dict

    def show(self, indices=None):
        # for i,f in self.read_dict(indices).items():
        for i, f in self.readDict(indices):
            print(f'{i}:')
            # fig.suptitle('image #{}'.format(i), fontsize=20, y=0.85)
            fig = pylab.figure(figsize=FIGSIZE)
            pylab.imshow(f[..., ::-1])
            pylab.show()
        return self

    @timeit
    def section(self, threshold=0.003, range_=None, show=False, log=False, plot=False):
        distances = []
        sections = [[0, None]]

        def compare(pre, cur):
            pre_obj = ImageCV(pre[1], pre[0])
            cur_obj = ImageCV(cur[1], cur[0])
            distance = pre_obj.distanceHist(cur_obj, method=sci_dist.euclidean, gray=False, show=False, log=False)[-1]
            distances.append([pre[0], cur[0], distance])
            if distance >= threshold:
                sections[-1][-1] = pre[0]
                sections.append([cur[0], None])
                if log:
                    print(f'[{pre[0]}]<->[{cur[0]}] distance: {distance}, threshold: {threshold}')
                if show:
                    pre_obj.show()
                    cur_obj.show()
            del pre_obj, cur_obj
            return cur

        reduce(compare, tqdm(self.readDict(range_), 'Calculating distances'))
        sections[-1][-1] = self.getInfo()['frame_c'] - 1 if range_ is None else range_[-1]
        if plot:
            pylab.plot(range(len(distances)), np.array(distances).transpose()[-1])
        return sections, distances
