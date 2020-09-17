from zdl.utils.io import log

log.theme('dark')
from zdl.utils.io.log import logger, addFileLogger, configConsoleLogger
from zdl.AI.pose.extractor.openpose_extractor import OpenposeExtractor

addFileLogger('test_main.log')
configConsoleLogger(10)

if __name__ == '__main__':
    pass
    logger.info('start.')
    OpenposeExtractor.setModel("/Volumes/CodeYard/Software/code-type/C++/openpose/models/")
    OpenposeExtractor() \
        .extract('/Volumes/CodeYard/Software/code-type/Python/ZDL-AI/resources/media/mike-tyson-full-body.png')
    # .addPreHooks(lambda x: print(x.shape))
    logger.info('exit.')
