from flask import Flask, render_template, request, jsonify
import sqlite3
import re
import requests
import threading
import msg_handler
import bili_utils
import secrets
import hmac
import time
import bili_utils
import session
import verify_request as vr

app = Flask(__name__,
    static_folder='oauth_static',
    static_url_path='/static',
)
app.debug = False

db = sqlite3.connect('oauth_application.db3', check_same_thread=False)

hmacKey = secrets.token_bytes(64)
tokenMaxAge = 86400

@app.route('/')
def mainPage():
    return render_template('base.html')

@app.route('/oauth/authorize')
def oauthPage():
    return render_template('verify.html', **{
        'botUid': bili_utils.selfUid,
        'botName': bili_utils.selfName,
    })

@app.route('/oauth/application/<cid>')
def getApp(cid):
    info = queryApp(cid)
    if info is None:
        return '', 404
    else:
        return {
            'cid': info['cid'],
            'name': info['name'],
            'url': info['url']
        }, 200

def queryApp(cid):
    cur = db.cursor()
    cur.execute('SELECT name, url, sec FROM app WHERE cid = ?', (cid, ))
    try:
        result = cur.fetchall()[0]
        return {
            'cid': cid,
            'name': result[0],
            'url': result[1],
            'sec': result[2],
        }

    except IndexError:
        return None
    finally:
        cur.close()

@app.route('/api/verify/<vid>', methods=('GET',))
def queryVerifyInfo(vid):
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
    code = vr.createVerify()
    return code, 201


@app.route('/api/verify/<vid>', methods=('DELETE',))
def delVerify(vid):
    return 'deleting verify is currently unavailable', 503
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


def authRequired(handler):
    def wrapper(*kw, **args):
        try:
            userToken = request.headers['Authorization'][7:]
            currentTs = int(time.time())
            uid, vid, expire, sign = userToken.split('.')
            if int(expire) < currentTs:
                return 'Expired token', 403
            if not secrets.compare_digest(calcToken(uid, vid, expire), sign):
                return 'Invalid sign', 403

            if type(args) != dict:
                args = {}

            args['uid'] = uid
            args['vid'] = vid

            handler(*kw, **args)

        except (IndexError, ValueError):
            return '', 400

    # rename wrapper name to prevent duplicated handler name
    wrapper.__name__ = handler.__name__
    return wrapper


@app.route('/api/session')
@authRequired
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
@authRequired
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

    expectSec = queryApp(cid).get('sec')
    if csec != '' and secrets.compare_digest(expectSec, csec):
        tkn = session.generateAccessToken(
            cid=cid,
            accCode=code,
        )
        if tkn is None:
            return 'Token has been already existed', 403

        sessionInfo = session.getSessionInfo('accCode', code)
        userInfo = bili_utils.getUserInfo(sessionInfo['uid'])
        return {
            'token': tkn,
            'user': userInfo,
        }


@app.route('/user')
def queryByToken():
    try:
        tkn = re.match(r'^Bearer (.+)$', request.headers['Authorization']).group(1)
    except IndexError:
        return '', 400

    sessionInfo = session.getSessionInfo('token', tkn)

    if sessionInfo:
        uid = sessionInfo['uid']
        userInfo = bili_utils.getUserInfo(uid)
        return userInfo, 200
    else:
        return 'Session not found matched this token', 404


@app.route('/proxy/avatar')
def avatarProxy():
    url = request.args.get('url')
    if re.match(r'^https://i[0-9]\.hdslb\.com/bfs/face.*\.webp$', url) is None:
        return '', 400
    req = requests.get(url)
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

    info = bili_utils.getUserInfo(uid)
    if info is None:
        return '', 404
    return info, 200, (
        ('Cache-Control', 'max-age=1800'),
        ('Access-Control-Allow-Origin', '*'),
        ('Vary', 'Origin'),
    )


def calcToken(uid, vid, expire):
    h = hmac.new(hmacKey, f'{uid}.{vid}.{expire}'.encode(), 'sha1')
    return h.hexdigest()
