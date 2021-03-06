import os
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

from zdl.AI.object_detection.structs import ObjectDetected
from zdl.utils.env.require import requireTF
from zdl.utils.env.terminal import Terminal
from zdl.utils.io.log import logger
from zdl.utils.media.rect import Rect

# Patch the location of gfile
tf.gfile = tf.io.gfile

os.environ["TFHUB_CACHE_DIR"] = '/content/tfhub_model_cache'

requireTF('2')


def installObjectDetectionPackage():
    # size: 85M
    Terminal.checkCall('git clone --depth 1 https://github.com/tensorflow/models.git '
                       '&& cd models/research/ '
                       '&& protoc object_detection/protos/*.proto --python_out=. '
                       '&& pip install .')


try:
    from object_detection.utils import label_map_util
except ModuleNotFoundError:
    logger.warning('installing object_detection package.')
    installObjectDetectionPackage()
    from object_detection.utils import label_map_util


class ObjectDetector(ABC):
    @classmethod
    def _mtype(cls, model):
        if model.startswith(('https:', 'https:')):
            return HubObjectDetector
        elif os.path.isdir(model):
            return RetrainedObjectDetector
        else:
            return GardenObjectDetector

    @classmethod
    def create(cls, model):
        return cls._mtype(model)().loadModel(model)

    @abstractmethod
    def _loadModel(self, model):
        pass

    def loadModel(self, model):
        model_loadable, signature = self._loadModel(model)
        self._detector = hub.load(model_loadable).signatures[signature]
        return self

    def modelInfo(self):
        logger.info(f'=====model info====='
                    f'inputs: {self._detector.inputs}'
                    f'output_dtypes: {self._detector.output_dtypes}'
                    f'output_shapes: {self._detector.output_shapes}'
                    f'label_map: {self._getLabelMap()}')

    @abstractmethod
    def _parseDetectResult(self, result):
        pass

    @abstractmethod
    def _getLabelMap(self):
        pass

    # @timeit
    def detect(self, image) -> Tuple[Dict, List[ObjectDetected]]:
        def detect_single_img(tensor):
            converted_img = tf.image.convert_image_dtype(tensor, self._detector.inputs[0].dtype)[tf.newaxis, ...]
            raw_result = self._detector(converted_img)
            logger.debug(f'Detect original result: {raw_result}')
            object_detected_list = self._parseDetectResult(raw_result)
            return raw_result, object_detected_list

        tensor = tf.convert_to_tensor(image[..., ::-1])
        return detect_single_img(tensor)


class HubObjectDetector(ObjectDetector):
    def _loadModel(self, model):
        model_loadable = model
        signature = 'default'
        return model_loadable, signature

    def _getLabelMap(self):
        pass

    def _parseDetectResult(self, raw_result) -> List[ObjectDetected]:
        result = {key: value.numpy() for key, value in raw_result.items()}
        class_names = result['detection_class_entities']
        scores = result["detection_scores"].flatten()
        bboxes = result["detection_boxes"]
        # boxes = boxes[0]
        bboxes.shape = (-1, bboxes.shape[-1])
        object_detected_list = [ObjectDetected(t[0], Rect(yxyx=t[1]), t[2]) for t in zip(class_names, bboxes, scores)
                                if t[2]]
        object_detected_list.sort(key=lambda o: o.score, reverse=True)
        return object_detected_list


class GardenObjectDetector(ObjectDetector):
    def __init__(self):
        self._path_to_labels = 'models/research/object_detection/data/mscoco_label_map.pbtxt'
        self._label_map = None

    def _loadModel(self, model):
        base_url = 'http://download.tensorflow.org/models/object_detection/'
        origin = base_url + model + '.tar.gz'
        model_dir = tf.keras.utils.get_file(
            fname=model,
            origin=origin,
            untar=True)
        model_loadable = os.path.join(model_dir, 'saved_model')
        signature = 'serving_default'
        return model_loadable, signature

    def _getLabelMap(self):
        if not self._label_map:
            assert self._path_to_labels, 'path_to_labels is None!'
            self._label_map = label_map_util.create_category_index_from_labelmap(
                self._path_to_labels, use_display_name=True)
        return self._label_map

    def _parseDetectResult(self, raw_result) -> List[ObjectDetected]:
        result = {key: value.numpy() for key, value in raw_result.items()}
        scores = result["detection_scores"].flatten()
        class_ids = result['detection_classes'].flatten()
        bboxes = result["detection_boxes"]
        bboxes.shape = (-1, bboxes.shape[-1])
        num_detections = int(result["num_detections"][0])
        label_map = self._getLabelMap()
        class_names = np.array([label_map[i]['name'] for i in class_ids])
        object_detected_list = [ObjectDetected(t[0], Rect(yxyx=t[1]), t[2]) for t in zip(class_names, bboxes, scores)
                                if t[2]]
        object_detected_list.sort(key=lambda o: o.score, reverse=True)
        return object_detected_list


class RetrainedObjectDetector(GardenObjectDetector):
    def __init__(self):
        self._path_to_labels = None
        self._label_map = None

    def _loadModel(self, model):
        self._path_to_labels = os.path.join(model, '..', 'label_map.pbtxt')
        assert os.path.exists(self._path_to_labels)
        model_loadable = model
        signature = 'serving_default'
        return model_loadable, signature
