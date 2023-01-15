from flask import request
import re
import requests

from misc.requests_session import session as rs
from service import app
from bili import utils as bu


@app.route('/proxy/avatar')
def avatarProxy():
    url = request.args.get('url')
    if re.match(r'^https://i[0-9]\.hdslb\.com/bfs/face.*\.webp$', url) is None:
        return '', 400
    req = rs.get(url)
    print(url)
    if req.status_code == 200:
        return req.content, 200, (
            ('Cache-Control', 'max-age=1800'),
            ('Content-Type', req.headers['Content-Type']),
            ('Access-Control-Allow-Origin', '*'),
            ('Vary', 'Origin'),
        )
    return '', 404


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
