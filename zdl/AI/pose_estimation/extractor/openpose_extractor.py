import sys

from zdl.AI.helper.openpose import DatumPickleable
from zdl.AI.pose_estimation.extractor.extractor import Extractor
from zdl.AI.pose_estimation.pose.body25b import BODY25B
from zdl.AI.pose_estimation.pose.base_pose import Poses
from zdl.utils.io.log import logger

sys.path.append('/usr/local/python')
sys.path.append('/usr/local/lib')

from openpose import pyopenpose as opp


class OpenposeExtractor(Extractor):

    def __init__(self, pose_type=BODY25B, params=None):
        if params is None:
            params = {}
        if 'model_pose' in params:
            logger.warning('model_pose param specified by pose_type arg, conflict.')
        super().__init__()
        self.pose_type = pose_type
        self.full_params = {
            'model_folder': self.model_path,
            'number_people_max': 3,
            # 'net_resolution': '-1x368', # it is default value
            'logging_level': 3,
            'display': 0,
            'alpha_pose': 0.79,
            # 'face': 1,
            # 'hand': 1,
        }
        self.full_params.update(params)
        self.full_params.update({
            'model_pose': pose_type.NAME,
        })

        self.opWrapper = opp.WrapperPython()
        self.opWrapper.configure(self.full_params)
        self.opWrapper.start()
        self.datum: opp.Datum = opp.Datum()

    def _callExtractorCore(self, img):
        self.datum.cvInputData = img
        self.opWrapper.emplaceAndPop([self.datum])
        logger.debug(self.datum.poseKeypoints)
        return Poses(self.datum.poseKeypoints, self.pose_type), DatumPickleable(self.datum, self.pose_type)
