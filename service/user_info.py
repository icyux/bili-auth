from flask import request
import secrets

from bili import utils as bu
from misc.hmac_token import checkToken
from model import application, session, user
from service import app
from service.auth_middleware import authRequired


@app.route('/api/user')
def getCurUserInfo():
	# an OAuth app is querying user info via client credentials
	if request.args.get('uid') is not None:
		try:
			uid = int(request.args['uid'])
			clientId = request.args['client_id']
			clientSecret = request.args['client_secret']
		except (KeyError, ValueError):
			return 'illegal params', 400

		# check client secret
		# todo: integrated client auth
		expectSec = application.query(clientId).get('sec')
		if clientSecret == '' or not secrets.compare_digest(expectSec, clientSecret):
			return 'unauthorized client', 403

		# todo: check permission with one SQL query
		sessions = session.getSessionsByUid(uid)
		for s in sessions:
			if s['cid'] == clientId:
				break
		else:
			return 'not authorized user', 403

	# an authentified user is querying self info
	elif request.headers.get('Authorization', '')[:5] == 'BUTKN':
		tkn = request.headers['Authorization'][6:]
		tknInfo = checkToken(tkn)
		if tknInfo is None or tknInfo.get('uid') is None:
			return 'authentication required', 403

		uid = tknInfo['uid']

	# an OAuth app is querying user info via OAuth token
	elif request.headers.get('Authorization', '')[:6] == 'Bearer':
		oauthTkn = request.headers['Authorization'][7:]
		sessInfo = session.getSessionInfo('token', oauthTkn)
		if sessInfo is not None:
			uid = sessInfo['uid']
		else:
			return 'illegal OAuth token', 403

	# illegal request
	else:
		return 'credentials required', 401

	# return user info
	userInfo = fetchUserInfo(uid)
	return userInfo


def fetchUserInfo(uid):
	# query from DB
	cachedUserInfo = user.queryUserInfo(uid)
	if cachedUserInfo is not None:
		return cachedUserInfo

	# refresh user info
	userInfo = bu.getUserInfo(uid)
	isSucc = user.updateUserInfo(uid, userInfo)
	if isSucc:
		return userInfo
	else:
		return 'failed to cache user info', 500


@app.route('/api/user/apps/authorized')
@authRequired(uidRequired=True)
def getAuthorizedApps(*, uid, vid):
	return application.getAuthorizedApps(uid)


@app.route('/api/user/apps/created')
@authRequired(uidRequired=True)
def getCreatedApps(*, uid, vid):
	return application.getCreatedApps(uid)
