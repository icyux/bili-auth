from flask import request
import secrets
import time

from misc.hmac_token import checkToken


def authRequired(uidRequired=True):
    def middleware(handler):
        def wrapper(*args, **kw):
            try:
                userToken = request.headers['Authorization'][6:]
                checkResult = checkToken(userToken)

                if checkResult is None or (uidRequired and checkResult['uid'] is None):
                    return 'invalid or expired token', 403

                if type(kw) != dict:
                    kw = {}

                if uidRequired:
                    kw['uid'] = checkResult['uid']
                kw['vid'] = checkResult['vid']

                return handler(*args, **kw)

            except (KeyError, IndexError, ValueError):
                return 'Invalid token', 400

        # rename wrapper name to prevent duplicated handler name
        wrapper.__name__ = handler.__name__
        return wrapper

    return middleware