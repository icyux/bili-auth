from flask import request, jsonify, Response
import os
import pathlib
import secrets
import uuid

from bili import utils as bu
from misc import config
from misc.icon_process import process_icon
from model import application, user
from model import session
from model.session import VerificationRevokedException
from service import app
from service.auth_middleware import authRequired


tokenMaxAge = 86400


@app.route('/oauth/application/<cid>')
def getApp(cid):
    info = application.query(cid)
    if info is None:
        return '', 404

    rtn = {}
    fieldList = ('cid', 'name', 'link', 'desc', 'prefix')
    for field in fieldList:
        rtn[field] = info[field]

    rtn['icon'] = f'/oauth/application/{info["cid"]}/icon'

    ownerInfo = user.mustQueryUserInfo(info['ownerUid'])
    rtn['owner'] = {
        'uid': info['ownerUid'],
        'name': ownerInfo['name'],
        'avatar': ownerInfo['avatar'],
    }

    return rtn, 200


@app.route('/oauth/application/<cid>/icon')
def getAppIcon(cid):
    info = application.query(cid)
    if info is None:
        return '', 404

    icon_filename = info['icon']
    if icon_filename is None or icon_filename == '':
        icon_filename = config['storage']['oauth_app_icon_default']

    icon_root_path = config['storage']['oauth_app_icons_path']
    icon_path = str(pathlib.Path(icon_root_path, icon_filename))
    with open(icon_path, 'rb') as f:
        icon_data = f.read()

    return Response(
        icon_data,
        mimetype='image/jpeg',
    )


@app.route('/oauth/application/<cid>/icon', methods=['PUT'])
@authRequired()
def updateAppIcon(cid, *, uid, vid):
    info = application.query(cid)
    if info is None:
        return 'app not found', 404

    if info['ownerUid'] != uid:
        return 'not app owner', 403

    icon_file = request.files.get('icon')
    if icon_file is not None:
        icon_filename = save_icon(icon_file)
    else:
        return '', 400

    result = application.updateAppIcon(cid, icon_filename)

    if result is True:
        return '', 200
    else:
        return '', 500


@app.route('/oauth/application/<cid>/icon', methods=['DELETE'])
@authRequired()
def removeAppIcon(cid, *, uid, vid):
    info = application.query(cid)
    if info is None:
        return 'app not found', 404

    if info['ownerUid'] != uid:
        return 'not app owner', 403

    result = application.removeAppIcon(cid)

    if result is True:
        return '', 200
    else:
        return '', 500


@app.route('/oauth/application', methods=('POST', ))
@authRequired()
def createApp(*, uid, vid):
    appInfo = {}
    try:
        appInfo['name'] = request.form['name']
        appInfo['link'] = request.form['link']
        appInfo['desc'] = request.form['desc']
        appInfo['prefix'] = request.form['prefix']
    except KeyError:
        return '', 400

    icon_file = request.files.get('icon')
    if icon_file is not None:
        appInfo['icon'] = save_icon(icon_file)

    result = application.createApp(uid=uid, **appInfo)
    if result is None:
        return '', 500
    else:
        return result


@app.route('/oauth/application/<cid>', methods=('PUT', ))
@authRequired()
def updateApp(cid, *, uid, vid):
    info = application.query(cid)
    if info is None:
        return 'app not found', 404

    if info['ownerUid'] != uid:
        return 'not app owner', 403

    new_info = {
        'name': request.form['name'],
        'link': request.form['link'],
        'desc': request.form['desc'],
        'prefix': request.form['prefix'],
    }

    result = application.updateApp(cid, **new_info)

    if result is True:
        return '', 200
    else:
        return '', 500


@app.route('/api/session')
@authRequired()
def querySession(*, uid, vid):
    cid = request.args.get('client_id')
    origSessions = session.getSessionsByUid(uid, cid)
    finalSessions = []
    fieldList = ('sid', 'vid', 'cid', 'create', 'accCode')
    for origSess in origSessions:
        sess = {}
        for field in fieldList:
            sess[field] = origSess[field]
        finalSessions.append(sess)
    return jsonify(finalSessions)


@app.route('/api/session', methods=('POST', ))
@authRequired()
def createSession(*, uid, vid):
    cid = request.args['client_id']
    try:
        sid, accCode = session.createSession(
            vid=vid,
            cid=cid,
        )
        return {
            'sessionId': sid,
            'accessCode': accCode,
        }, 200

    except VerificationRevokedException:
        return 'verification has been revoked', 403



@app.route('/oauth/access_token', methods=('POST', ))
def createAccessToken():
    try:
        cid = request.args['client_id']
        csec = request.args['client_secret']
        code = request.args['code']
    except IndexError:
        return '', 400

    expectSec = application.query(cid).get('sec')
    if csec == '' or not secrets.compare_digest(expectSec, csec):
        return 'Invalid client id or client secret', 403

    tkn = session.generateAccessToken(
        cid=cid,
        accCode=code,
    )
    if tkn is None:
        return 'Invalid access code', 403

    sessionInfo = session.getSessionInfo('token', tkn)
    userInfo = user.queryUserInfo(sessionInfo['uid'])
    return {
        'token': tkn,
        'user': userInfo,
    }


@app.route('/api/user/apps/authorized', methods=('DELETE', ))
@authRequired()
def revokeAuthorization(*, uid, vid):
    cid = request.args.get('cid')
    if cid is None:
        return '', 400

    result = application.revokeAuthorization(uid=uid, cid=cid)
    if result is True:
        return '', 200
    else:
        return '', 404


@app.route('/oauth/application/<cid>', methods=('DELETE', ))
@authRequired()
def deleteApplication(cid, *, uid, vid):
    appInfo = application.query(cid)
    if appInfo is None:
        return '', 404

    if appInfo['ownerUid'] != uid:
        return '', 403

    result = application.deleteApplication(cid)
    if result is True:
        return '', 200
    else:
        return '', 500


def save_icon(icon_file):
    processed_icon = process_icon(icon_file)

    icon_uuid = str(uuid.uuid4())
    icon_filename = f'{icon_uuid}.jpg'
    icon_root_path = config['storage']['oauth_app_icons_path']
    icon_path = str(pathlib.Path(icon_root_path, icon_filename))

    os.makedirs(icon_root_path, exist_ok=True)
    with open(icon_path, 'wb') as f:
        f.write(processed_icon)

    return icon_filename
