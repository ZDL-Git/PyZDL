from datetime import datetime


def prettyYToMs():
    return datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
