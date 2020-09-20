import sys

sys.path.append('/usr/local/python')
sys.path.append('/usr/local/lib')

from openpose import pyopenpose as opp
from zdl.AI.pose.extractor.extractor import Extractor
from zdl.utils.io.log import logger


class OpenposeExtractor(Extractor):

    def __init__(self, params={}):
        super().__init__()
        full_params = {
            'model_folder': self.__class__.model_path,
            'model_pose': 'BODY_25',
            'number_people_max': 3,
            # 'net_resolution': '-1x368', # it is default value
            'logging_level': 3,
            'display': 0,
            'alpha_pose': 0.79,
            # 'face': 1,
            # 'hand': 1,
        }
        full_params.update(params)

        self.opWrapper = opp.WrapperPython()
        self.opWrapper.configure(full_params)
        self.opWrapper.start()
        self.datum = opp.Datum()

    def callExtractorCore(self, img):
        self.datum.cvInputData = img
        self.opWrapper.emplaceAndPop([self.datum])
        logger.debug(self.datum.poseKeypoints)
        return self.datum
