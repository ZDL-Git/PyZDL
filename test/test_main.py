from zdl.utils.io import log

log.theme('dark')
from zdl.AI.pose.extractor.openpose_extractor import OpenposeExtractor
from zdl.AI.pose.pose.body25 import BODY25
from zdl.AI.pose.pose.pose import Poses
from zdl.utils.io.log import logger, addFileLogger, configConsoleLogger
from zdl.utils.media.image import sysShow

addFileLogger('test_main.log')
configConsoleLogger(10)

if __name__ == '__main__':
    pass
    logger.info('start.')
    OpenposeExtractor.setModel("/Volumes/CodeYard/Software/code-type/C++/openpose/models/")
    datum = OpenposeExtractor() \
        .extract('/Volumes/CodeYard/Software/code-type/Python/ZDL-AI/resources/media/mike-tyson-full-body.png')
    # .addPreHooks(lambda x: print(x.shape))
    sysShow(datum.cvOutputData)
    logger.info(Poses(datum.poseKeypoints, BODY25).centers())
    logger.info('exit.')
