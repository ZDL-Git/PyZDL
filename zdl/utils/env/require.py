import platform


def requirePython(v: str):
    python_version = platform.python_version()
    assert python_version.startswith(f'{v}.'), \
        f'tensorflow version not matched, need {v}, got {python_version}'


def requireTF(v: str):
    import tensorflow as tf
    assert tf.__version__.startswith(f'{v}.'), \
        f'tensorflow version not matched, need {v}, got {tf.__version__}'
