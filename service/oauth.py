from flask import request, jsonify
import secrets

from bili import utils as bu
from model import application, user
from model import session
from service import app
from service.auth_middleware import authRequired


tokenMaxAge = 86400


@app.route('/oauth/application/<cid>')
def getApp(cid):
    info = application.query(cid)
    if info is None:
        return '', 404

    rtn = {}
    fieldList = ('cid', 'name', 'link', 'desc', 'icon', 'prefix')
    for field in fieldList:
        rtn[field] = info[field]

    ownerInfo = user.queryUserInfo(info['ownerUid'])
    rtn['owner'] = {
        'uid': info['ownerUid'],
        'name': ownerInfo['name'],
        'avatar': ownerInfo['avatar'],
    }

    return rtn, 200


@app.route('/oauth/application', methods=('POST', ))
@authRequired()
def createApp(*, uid, vid):
    appInfo = {}
    try:
        appInfo['name'] = request.form['name']
        appInfo['icon'] = request.form['icon']
        appInfo['link'] = request.form['link']
        appInfo['desc'] = request.form['desc']
        appInfo['prefix'] = request.form['prefix']

    except KeyError:
        return '', 400

    result = application.updateApp(uid=uid, **appInfo)
    if result is None:
        return '', 500
    else:
        return result


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
    sid, accCode = session.createSession(
        vid=vid,
        cid=cid,
    )
    return {
        'sessionId': sid,
        'accessCode': accCode,
    }, 200


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
