#!/bin/python3

from flask import Flask, render_template, request
import sqlite3
import re
import requests
import threading
import auth_handler
import msg_handler
import bili_utils

app = Flask(__name__,
    static_folder='oauth_static',
    static_url_path='/static',
)
app.debug = False

db = sqlite3.connect('oauth_application.db3', check_same_thread=False)

@app.route('/')
def mainPage():
    return render_template('base.html')

@app.route('/oauth/authorize')
def oauthPage():
    return render_template('verify.html')

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

@app.route('/oauth/verify/<code>', methods=('GET',))
def queryVerifyInfo(code):
    result = auth_handler.getVerifyInfo(code)
    if result is None:
        return '', 404
    elif result['isAuthed'] == False:
        return result, 202
    else:
        return result, 200

@app.route('/oauth/verify', methods=('POST',))
def createVerify():
    cid = request.args.get('client_id')
    appInfo = queryApp(cid)
    if appInfo is None:
        return '', 404
    code = auth_handler.createVerify(appInfo['cid'], appInfo['name'])
    print(repr(code))
    return code, 201


@app.route('/oauth/verify/<code>', methods=('DELETE',))
def delVerify(code):
    uid = request.args.get('uid')
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

@app.route('/oauth/access_token', methods=('POST', ))
def createAccessToken():
    try:
        cid = request.args['client_id']
        csec = request.args['client_secret']
        code = request.args['code']
    except IndexError:
        return '', 400

    info = auth_handler.getVerifyInfo(code)
    if info is not None and info['isAuthed'] and info['cid'] == cid:
        expectSec = queryApp(cid).get('sec')
        if expectSec == csec and csec != '':
            tkn = auth_handler.createToken(code)
            if tkn is not None:
                return {
                    'token': tkn,
                    **info,
                }, 200
            else:
                return '', 500
        else:
            return '', 403
    else:
        return '', 403

@app.route('/user')
def queryByToken():
    try:
        tkn = re.match(r'^Bearer (.+)$', request.headers['Authorization'])
    except IndexError:
        return '', 400

    info = auth_handler.tokenQuery(tkn)

    if info:
        return info, 200
    return '', 404

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
        ('Content-Type', req.headers['Content-Type']),
        ('Access-Control-Allow-Origin', '*'),
        ('Vary', 'Origin'),
    )