import hmac

import service


def calcToken(uid, vid, expire):
    if uid is None:
        body = f'{uid}.{vid}.{expire}'
    else:
        body = f'{vid}.{expire}'
    h = hmac.new(service.hmacKey, body.encode(), 'sha1')
    return h.hexdigest()
