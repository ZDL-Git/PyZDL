import sys


def requirePython(v: str, greater_ok: bool = True):
    sys_version = sys.version_info
    for i, n in enumerate(v.split('.')):
        n = int(n)
        if (not greater_ok and n != sys_version[i]) or (greater_ok and n > sys_version[i]):
            raise Exception(f'python version not matched, need {v}, got {sys_version}')


def requireTF(v: str):
    import tensorflow as tf
    assert tf.__version__.startswith(f'{v}.'), \
        f'tensorflow version not matched, need {v}, got {tf.__version__}'
