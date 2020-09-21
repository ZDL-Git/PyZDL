import sys


def requirePython(v: str, greater_ok: bool = True):
    v_tuple = tuple(map(int, v.split('.')))
    v_len = len(v_tuple)
    v_sys = sys.version_info[:v_len]
    if (not greater_ok and v_tuple != v_sys) or (greater_ok and v_tuple > v_sys):
        raise Exception(f'python version not matched, need {v}, got {v_sys}')


def requireTF(v: str):
    import tensorflow as tf
    assert tf.__version__.startswith(f'{v}.'), \
        f'tensorflow version not matched, need {v}, got {tf.__version__}'
