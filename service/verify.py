from flask import request

from misc.hmac_token import calcToken
from model import verify_request as vr
from service import app
from service.auth_middleware import authRequired


@app.route('/api/verify/<vidParam>', methods=('GET',))
@authRequired(uidRequired=False)
def queryVerifyInfo(vidParam, *, vid):
    assert vidParam == vid
    result = vr.getVerifyInfo(vid)
    if result is None:
        return '', 404
    elif result['isAuthed'] == False:
        return result, 202
    else:
        uid = result['uid']
        expire = result['expire']
        sign = calcToken(uid, vid, expire)
        finalToken = f'{uid}.{vid}.{expire}.{sign}'
        result['token'] = finalToken
        return result, 200


@app.route('/api/verify', methods=('POST',))
def createVerify():
    try:
        data = request.get_json()
        ua = data['ua']
    except Exception:
        ua = None

    vid, expire = vr.createVerify(userAgent=ua)
    sign = calcToken(None, vid, expire)
    token = f'{vid}.{expire}.{sign}'

    return {
        'vid': vid,
        'token': token,
        'expire': expire,
    }, 201


@app.route('/api/verify/<vid>', methods=('DELETE',))
def delVerify(vid):
    return 'deleting verify is currently unavailable', 501
    if not uid:
        return '', 400
    try:
        result = auth_handler.revokeVerify(code, int(uid))
        if result:
            return '', 200
        else:
            return '', 404
    except ValueError:
        return '', 400
