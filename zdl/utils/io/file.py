import hashlib


def hashOfFile(file: str, fn='md5') -> str:
    # BUF_SIZE is totally arbitrary, change for your app!
    # lets read stuff in 500MB chunks!
    buf_size = 524288000
    if fn == 'md5':
        res = hashlib.md5()
    elif fn == 'sha1':
        res = hashlib.sha1()
    else:
        raise ValueError('fn should be in [md5,sha1]')

    with open(file, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            res.update(data)
    return res.hexdigest()
