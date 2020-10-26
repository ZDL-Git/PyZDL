import time
from datetime import datetime

from zdl.utils.io.log import logger


def prettyYToMs():
    return datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logger.debug('Timeit:: %r :: %f s' % (method.__name__, (te - ts)))
        return result

    return timed
