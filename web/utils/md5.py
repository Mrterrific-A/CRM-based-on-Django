import hashlib


def gen_md5(origin):
    """对密码加密"""
    ha = hashlib.md5(b'd2r3ewefw')
    ha.update(origin.encode('utf-8'))
    return ha.hexdigest()