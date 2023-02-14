from flask import request

from service import app
from bili import utils as bu


@app.route('/proxy/user')
def userInfoProxy():
    try:
        uid = int(request.args['uid'])
    except (IndexError, ValueError):
        return '', 400

    info = bu.getUserInfo(uid)
    if info is None:
        return '', 404
    return info, 200, (
        ('Cache-Control', 'max-age=1800'),
        ('Access-Control-Allow-Origin', '*'),
        ('Vary', 'Origin'),
    )
