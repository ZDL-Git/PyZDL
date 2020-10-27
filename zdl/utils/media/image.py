import os
import subprocess
import sys
import tempfile
import types
from abc import abstractmethod
from pathlib import Path
from statistics import mean
from typing import Tuple, List, Callable

import PIL
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pylab
from scipy.spatial import distance as sci_dist

from zdl.utils.helper.time import timeit
from zdl.utils.io.log import logger
from zdl.utils.media.media import Media, FIGSIZE, IMG_SUFFIXES
from zdl.utils.media.rect import Rect


# class ShowType(Enum):
#     WINDOW = 1
#     COLAB = 2


class ImgArray(np.ndarray):
    # customize np.ndarray
    def __new__(cls, array):
        obj = np.asarray(array).view(cls)
        return obj

    def fill(self, v):
        # overwrite for chain call
        super().fill(v)
        return self

    def toImageCV(self):
        return ImageCV(self)


def sysShow(imagepath_or_obj):
    if isinstance(imagepath_or_obj, str):
        image_path = imagepath_or_obj
    else:
        # you can save manually in system viewer
        with tempfile.NamedTemporaryFile(mode="wb", suffix='.png') as png:
            image_path = png.name
        cv2.imwrite(image_path, imagepath_or_obj)
    logger.debug(image_path)
    image_viewer_command = {'linux': 'xdg-open',
                            'win32': 'explorer',
                            'darwin': 'open'}[sys.platform]
    subprocess.run([image_viewer_command, image_path])


class _ImageBase(Media):
    CHANNELS_ORDER = None

    def __init__(self):
        self._img = None
        self.fname = None
        self.imshow_params = None
        self.title = None
        self.hold = None
        self._info = None
        self.gray_obj = None
        self.hist_obj = None
        self.HSV_obj = None
        self.B_obj = None
        self.G_obj = None
        self.R_obj = None
        self.H_obj = None
        self.S_obj = None
        self.V_obj = None

    @abstractmethod
    def _loadImage(self):
        pass

    @abstractmethod
    def _shape(self):
        pass

    @abstractmethod
    def getInfo(self):
        pass

    def channelInfo(self):
        for i, c in enumerate(cv2.split(self.org())):
            logger.info(f"channel {i}:")
            logger.info(f"  mean:", c.mean())
            sum_, full = c.sum(), c.size * 255
            logger.info("  sum: {}/{} {:.2f}%".format(sum_, full, sum_ / full * 100))
        return self

    def hold(self, hold):
        self.hold = hold
        return self

    def setTitle(self, title):
        self.title = title
        return self

    def isColor(self):
        _, _, c = self._shape()
        if c == 3:
            return True
        elif c == 1:
            return False
        else:
            assert False, 'unimplemented image type!'

    def equal(self, another):
        assert isinstance(another, type(self)), f'Another should be an {type(self)} obj!'
        return pylab.array_equal(self.org(), another.org())

    def __eq__(self, another):
        return self.equal(another)

    def show(self, title=None, figsize=None, **params):
        if params.get('show') == False:  # keep call chaining
            return self
        logger.info('===============showing image============')
        self.info()
        info = self.getInfo()
        assert info['width'] and info['height'], 'img shape error!'
        params = dict(self.imshow_params, **params)
        logger.info(params)
        logger.info(f'{title or self.title}:')
        if self.isColor():
            if params['cmap'] == 'hsv':
                logger.warn('HSV format should covert back to RGB!')
            img = self.org()
            if self.CHANNELS_ORDER == ('b', 'g', 'r'):
                img = img[..., ::-1]  # swap B and R channels for plt show
        else:
            if params['cmap'] == 'viridis':
                logger.warn("Single channel image, set cmap to default 'Grey_r'")
                params['cmap'] = 'Greys_r'
                img = self.gray().org()
            else:
                img = self.org()
        fig = pylab.figure(figsize=figsize or FIGSIZE)
        x_major_locator = int(img.shape[1] / 10)
        x_minor_locator = x_major_locator / 4
        ax = plt.gca()
        ax.xaxis.set_major_locator(pylab.MultipleLocator(x_major_locator))
        ax.xaxis.set_minor_locator(pylab.MultipleLocator(x_minor_locator))
        ax.yaxis.set_minor_locator(pylab.MultipleLocator(x_minor_locator))
        pylab.imshow(img, **params)
        pylab.show()
        return self

    def save(self, fpath, all_=False):
        cv2.imwrite(fpath, self.org(), [cv2.IMWRITE_PNG_COMPRESSION, 0])
        if all_:
            base_name, suffix = os.path.basename(fpath).split('.')
            cv2.imwrite(base_name + '-gray.' + suffix, self.gray())
        return self

    def org(self):
        if self._img is None:
            self._loadImage()
        return self._img

    @abstractmethod
    def B(self):
        pass

    @abstractmethod
    def G(self):
        pass

    @abstractmethod
    def R(self):
        pass

    @abstractmethod
    def gray(self):
        pass

    @abstractmethod
    def brightness(self):
        pass

    def hist(self, show=True, hist_size=None):
        if hist_size is None:
            hist_size = [256]
        assert 256 % hist_size[0] == 0, 'histSize should be 256 factor!'
        step = int(256 / hist_size[0])
        hists = []
        if self.isColor():
            for i, col in enumerate(self.CHANNELS_ORDER):
                hist = cv2.calcHist([self.org()], [i], None, hist_size, [0, 256])
                hist_trans = hist.transpose().ravel()
                if show:
                    # pylab.plot(hist,color = col) #256 可以直接显示
                    pylab.plot(range(int(step / 2), 256, step), hist_trans, color=col)
                hists.append(hist_trans)
        hist = cv2.calcHist([self.gray().org()], [0], None, hist_size, [0, 256])
        hist_trans = hist.transpose().ravel()
        hists.append(hist_trans)
        if show:
            pylab.plot(range(int(step / 2), 256, step), hist_trans, color='grey')
            pylab.xlim([0, 256])
            pylab.show()
        return pylab.array(hists)

    def hist2d(self):
        hist = cv2.calcHist([self.HSV().org()], [0, 1], None, [180, 256], [0, 180, 0, 256])
        pylab.imshow(hist, cmap='Blues_r', interpolation='nearest')
        pylab.show()
        return hist

    def HSV(self):
        assert self.isColor(), 'HSV needs 3 channels image!'
        if self.HSV_obj is None:
            if self.imshow_params['cmap'] == 'hsv':
                logger.warn('Self is already an HSV image!')
                return self
            imshow_params = {'cmap': 'hsv'}
            HSV_obj = self.__class__(cv2.cvtColor(self.org(), cv2.COLOR_BGR2HSV), imshow_params)
            if self.hold:
                self.HSV_obj = HSV_obj
        return self.HSV_obj or HSV_obj

    def V(self):
        V_obj = self.V_obj or self.__class__(self.HSV().org()[..., 2], imshow_params={'cmap': 'Greys_r'})
        if self.hold:
            self.V_obj = V_obj
        return V_obj

    def diff(self, another):
        logger.info('===============diffing image===============')
        if isinstance(another, np.ndarray):
            assert self.org().shape == another.shape, 'The shapes should be the same!'
            another = self.__class__(another)
        elif isinstance(another, type(self)):
            assert self.org().shape == another.org().shape, 'The shapes should be the same!'
        else:
            assert False, f'Another should be a numpy.ndarray or {type(self)}'
        diff_ = cv2.absdiff(self.org(), another.org())
        return self.__class__(diff_, self.imshow_params)

    def grayDiff(self, another):
        logger.info('===============diffing image===============')
        if isinstance(another, np.ndarray):
            another = self.__class__(another)
        elif not isinstance(another, type(self)):
            assert False, f'Another should be a numpy.ndarray or {type(self)}'
        if self.org().shape != another.org().shape:
            logger.warn('Comparing images with different shapes')
        diff_ = cv2.absdiff(self.gray().org(), another.gray().org())
        return self.__class__(diff_, imshow_params={'cmap': 'Greys_r'})

    def distanceHist(self, another, method=sci_dist.euclidean, hist_size=None, gray=False,
                     show=True):
        if hist_size is None:
            hist_size = [256]
        assert isinstance(method, types.FunctionType), 'method should be a function!'
        if isinstance(another, np.ndarray):
            another = self.__class__(another)
        elif isinstance(another, type(self)):
            assert self.org().shape == another.org().shape, 'The shapes should be the same!'
        else:
            assert False, f'Another should be a numpy.ndarray or {type(self)}'
        hist_self = self.hist(show, hist_size=hist_size)
        hist_another = another.hist(show, hist_size=hist_size)
        if gray:
            d = method(hist_self[-1].transpose(), hist_another[-1].transpose())
        else:
            assert len(hist_self) == len(hist_another) == 4, 'color mode needs three channels image!'
            d = []
            for c in range(3):
                d.append(method(hist_self[c].transpose(), hist_another[c].transpose()))
            d = mean(d)
        full_size = self.gray().org().size
        ratio = d / full_size
        logger.debug(d, full_size, ratio)
        return d, full_size, ratio

    def distanceLine(self, another, method=sci_dist.euclidean):
        self_info = self.getInfo()
        w, h = self_info['width'], self_info['height']

    def normRectToXywhRect(self, norm_rect, dilate_ratio=1):
        img_info = self.getInfo()
        h, w = img_info['height'], img_info['width']
        ymin, xmin, ymax, xmax = norm_rect
        y_l, x_l = ymax - ymin, xmax - xmin
        y_d, x_d = y_l * (dilate_ratio - 1), x_l * (dilate_ratio - 1)
        xywh_rect_x = int(max((xmin - x_d) * w, 0))
        xywh_rect_y = int(max((ymin - y_d) * h, 0))
        xywh_rect_w = int(min((xmax + x_d) * w, w) - xywh_rect_x)
        xywh_rect_h = int(min((ymax + y_d) * h, h) - xywh_rect_y)
        return xywh_rect_x, xywh_rect_y, xywh_rect_w, xywh_rect_h

    def normRectToAbsRect(self, norm_rect: Rect, dilate_ratio=1) -> Rect:
        img_info = self.getInfo()
        img_h, img_w = img_info['height'], img_info['width']
        y_d, x_d = norm_rect.h * (dilate_ratio - 1), norm_rect.w * (dilate_ratio - 1)
        yxyx = max((norm_rect.r_t - y_d) * img_h, 0), max((norm_rect.c_l - x_d) * img_w, 0) \
            , min((norm_rect.r_b + y_d) * img_h, img_h), min((norm_rect.c_r + x_d) * img_w, img_w)
        return Rect(yxyx=yxyx)

    def rectDilate(self, abs_rect: Rect, dilate_ratio=1) -> Rect:
        img_info = self.getInfo()
        h, w = img_info['height'], img_info['width']
        ymin = max(0, abs_rect.r_t - (abs_rect.h * (dilate_ratio - 1)))
        ymax = min(h, abs_rect.r_b + (abs_rect.h * (dilate_ratio - 1)))
        xmin = max(0, abs_rect.c_l - (abs_rect.w * (dilate_ratio - 1)))
        xmax = min(w, abs_rect.c_r + (abs_rect.w * (dilate_ratio - 1)))
        return Rect(xyxy=(xmin, ymin, xmax, ymax))

    def roiCopy(self, rect: Rect):
        rect = rect.toInt()
        roi = self.org()[rect.r_t:rect.r_b, rect.c_l:rect.c_r]
        return self.__class__(np.copy(roi), self.title)

    @abstractmethod
    def enhanceBrightnessTo(self, target_brightness):
        pass

    def apply(self, func: Callable) -> '_ImageBase':
        # func: one input param img, return img processed
        self._img = func(self.org())
        return self


class ImageCV(_ImageBase):
    CHANNELS_ORDER = ('b', 'g', 'r')

    def __init__(self, media, title=None, imshow_params=None, hold=False):
        super().__init__()
        if imshow_params is None:
            imshow_params = {}
        if isinstance(media, np.ndarray):
            self._img = ImgArray(media)
            self.fname = None
        elif isinstance(media, str):
            assert os.path.isfile(media), f'{media} not exists!'
            assert Path(media).suffix in IMG_SUFFIXES, 'file type not supported!'
            self._img = None
            self.fname = media
        else:
            assert False, f'wrong type of media param->{type(media)}'
        imshow_default_params = {'interpolation': 'none', 'cmap': 'viridis', 'vmin': 0, 'vmax': 255}
        self.imshow_params = dict(imshow_default_params, **imshow_params)
        self.title = title or self.fname
        self.hold = hold

    def _loadImage(self):
        self._img = ImgArray(cv2.imread(self.fname))

    def _shape(self):
        shape = self.org().shape
        if len(shape) == 2:
            h, w = shape
            c = 1
        else:
            h, w, c = shape
        return h, w, c

    def getInfo(self):
        if self._info is None:
            shape = self._shape()
            self._info = {'fname': self.fname,
                          'frame_c': 1,
                          'shape': shape,
                          'width': shape[1],
                          'height': shape[0],
                          'channels': shape[2] if self.isColor() else 1,
                          'mode': 'cv2',
                          'cmap': self.imshow_params['cmap']}
        return self._info

    def gray(self):
        if self.gray_obj is None:
            imshow_params = {'cmap': 'Greys_r'}
            if self.isColor():
                gray_obj = self.__class__(cv2.cvtColor(self.org(), cv2.COLOR_BGR2GRAY), imshow_params)
            else:
                # assert False, 'It is already a single channel!'
                gray_obj = self.__class__(self.org(), imshow_params)
            if self.hold:
                self.gray_obj = gray_obj
        return self.gray_obj or gray_obj

    def B(self):
        assert self.isColor(), 'It is already a single channel!'
        B_obj = self.B_obj or self.__class__(cv2.split(self.org())[0], imshow_params={'cmap': 'Blues_r'})
        if self.hold:
            self.B_obj = B_obj
        return B_obj

    def G(self):
        assert self.isColor(), 'It is already a single channel!'
        G_obj = self.G_obj or self.__class__(self.org()[..., 1], imshow_params={'cmap': 'Greens_r'})
        if self.hold:
            self.G_obj = G_obj
        return G_obj

    def R(self):
        assert self.isColor(), 'It is already a single channel!'
        R_obj = self.R_obj or self.__class__(self.org()[..., 2], imshow_params={'cmap': 'Reds_r'})
        if self.hold:
            self.R_obj = R_obj
        return R_obj

    def brightness(self):
        return self.gray().org().mean()

    @timeit
    def enhanceBrightnessTo(self, target_brightness):
        org_brightness = self.brightness()
        img = PIL.Image.fromarray(self.org())
        factor = target_brightness / self.brightness() + 0.1
        enhancer = PIL.ImageEnhance.Brightness(img)
        enhanced_img = enhancer.enhance(factor)
        self._img = ImgArray(np.asarray(enhanced_img))
        logger.debug(f'original brightness is {org_brightness}')
        logger.debug(f'enhanced brightness is {self.brightness()}')
        return self

    def drawBboxes(self, bbox_entities: List[Tuple[Rect, str]], copy=True):
        """
        bbox_entities: List[Tuple[rect, label]]
        """
        # Log.debug(bbox_entities)
        img = self.org().copy() if copy else self.org()
        for i, bbox_entity in enumerate(bbox_entities):
            bbox, label = bbox_entity
            logger.info(label)
            # color = tuple(np.random.randint(256, size=3))
            xywh = tuple(bbox.toInt().xywh)
            color = tuple(np.random.choice(range(40, 256), size=3))
            color_int = tuple(map(int, color))[::-1]
            label_w = len(label) * 12
            label_h = 25
            thickness = 3
            cv2.rectangle(img, rec=xywh, color=color_int, thickness=thickness)
            cv2.rectangle(img,
                          rec=(
                              xywh[0] - thickness // 2 - 1,
                              max(0, xywh[1] - label_h),
                              label_w,
                              label_h,
                          ),
                          color=color_int, thickness=-1)
            cv2.putText(img, label, org=(xywh[0], max(22, xywh[1] - 5)),
                        fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=0.6,
                        color=(0, 0, 0),
                        lineType=cv2.LINE_AA)
        return self.__class__(img, f'{self.title}:draw_bboxes') if copy else self

    def drawPoints(self, points, copy=True):
        img = self.org().copy() if copy else self.org()
        for p in points:
            cv2.circle(img, p, radius=10, color=(0, 0, 0), thickness=-1)
            cv2.circle(img, p, radius=10, color=(255, 255, 255), thickness=2)
        return self.__class__(img, f'{self.title}:draw_points') if copy else self


class ImagePIL(_ImageBase):
    CHANNELS_ORDER = ('r', 'g', 'b')

    def __init__(self, media, title=None, imshow_params=None, hold=False):
        super().__init__()
        if imshow_params is None:
            imshow_params = {}
        if isinstance(media, PIL.Image.Image):
            self._img = media
            self.fname = None
        elif isinstance(media, str):
            assert os.path.isfile(media), f'{media} not exists!'
            assert Path(media).suffix in IMG_SUFFIXES, 'file type not supported!'
            self._img = None
            self.fname = media
        else:
            assert False, f'media param type wrong->{type(media)}'
        imshow_default_params = {'interpolation': 'none', 'cmap': 'viridis'}
        self.imshow_params = dict(imshow_default_params, **imshow_params)
        self.title = title or self.fname
        self.hold = hold

    def _loadImage(self):
        self._img = PIL.Image.open(self.fname)

    def _shape(self):
        w, h = self.org().size
        c = len(self.org().mode)
        return h, w, c

    def getInfo(self):
        if self._info is None:
            shape = self._shape()
            self._info = {'fname': self.fname,
                          'frame_c': 1,
                          'shape': shape,
                          'width': shape[1],
                          'height': shape[0],
                          'channels': shape[2] if self.isColor() else 1,
                          'mode': 'PIL',
                          'cmap': self.imshow_params['cmap']}
        return self._info

    def gray(self):
        if self.gray_obj is None:
            imshow_params = {'cmap': 'Greys_r'}
            if self.isColor():
                gray_obj = self.__class__(self.org().convert('L'), imshow_params)
            else:
                # assert False, 'It is already a single channel!'
                gray_obj = self.__class__(self.org(), imshow_params)
            if self.hold:
                self.gray_obj = gray_obj
        return self.gray_obj or gray_obj

    def B(self):
        assert self.isColor(), 'It is already a single channel!'
        B_obj = self.B_obj or self.__class__(self.org().split()[2], imshow_params={'cmap': 'Blues_r'})
        if self.hold:
            self.B_obj = B_obj
        return B_obj

    def G(self):
        assert self.isColor(), 'It is already a single channel!'
        G_obj = self.G_obj or self.__class__(self.org().split()[1], imshow_params={'cmap': 'Greens_r'})
        if self.hold:
            self.G_obj = G_obj
        return G_obj

    def R(self):
        assert self.isColor(), 'It is already a single channel!'
        R_obj = self.R_obj or self.__class__(self.org().split()[0], imshow_params={'cmap': 'Reds_r'})
        if self.hold:
            self.R_obj = R_obj
        return R_obj

    def brightness(self):
        return np.asarray(self.gray().org()).mean()

    @timeit
    def enhanceBrightnessTo(self, target_brightness):
        org_brightness = self.brightness()
        factor = target_brightness / org_brightness + 0.1
        enhancer = PIL.ImageEnhance.Brightness(self.org())
        enhanced_img = enhancer.enhance(factor)
        self._img = enhanced_img
        logger.debug(f'original brightness is {org_brightness}')
        logger.debug(f'enhanced brightness is {self.brightness()}')
        return self
