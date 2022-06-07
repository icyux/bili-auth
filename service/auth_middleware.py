from flask import request
import secrets
import time

from misc.hmac_token import calcToken


def authRequired(uidRequired=True):
    def middleware(handler):
        def wrapper(*args, **kw):
            try:
                userToken = request.headers['Authorization'][7:]
                currentTs = int(time.time())

                try:
                    uid, vid, expire, sign = userToken.split('.')
                except ValueError as e:
                    if uidRequired:
                        raise e
                    uid = None
                    vid, expire, sign = userToken.split('.')

                if int(expire) < currentTs:
                    return 'Expired token', 403
                if not secrets.compare_digest(calcToken(uid, vid, expire), sign):
                    return 'Invalid sign', 403

                if type(kw) != dict:
                    kw = {}

                if uidRequired:
                    kw['uid'] = uid
                kw['vid'] = vid

                return handler(*args, **kw)

            except (IndexError, ValueError):
                return 'Invalid token', 400

        # rename wrapper name to prevent duplicated handler name
        wrapper.__name__ = handler.__name__
        return wrapper

    return middleware