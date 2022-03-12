import sqlite3
import secrets
import time
import verify_request as vr

db = None
accCodeLen = 16
tokenLen = 24


def setDB(mainDB):
	global db
	db = mainDB


def createSession(*, vid, cid):
	createTs = int(time.time())
	accessCode = secrets.token_urlsafe(accCodeLen)
	vInfo = vr.getVerifyInfo(vid)
	uid = vInfo['uid']
	assert vInfo['isAuthed']
	cur = db.cursor()
	try:
		cur.execute(
			'INSERT INTO session ("vid", "uid", "cid", "create", "accCode") VALUES (?,?,?,?,?)',
			(vid, uid, cid, createTs, accessCode),
		)
		affected = cur.rowcount
		assert affected == 1
		cur.execute('SELECT sid FROM session ORDER BY sid DESC LIMIT 1')
		sid = cur.fetchone()[0]
	finally:
		cur.close()
		db.commit()

	return sid, accessCode


def generateAccessToken(*, cid, accCode):
	token = secrets.token_urlsafe(tokenLen)
	cur = db.cursor()
	cur.execute(
		'UPDATE session SET token=? WHERE cid=? AND accCode=? and token IS NULL',
		(token, cid, accCode),
	)
	affected = cur.rowcount
	cur.close()
	db.commit()
	if affected == 1:
		return token
	else:
		return None

def getSessionInfo(key, value):
	assert key in ('accCode', 'sid', 'token')
	cur = db.cursor()
	cur.execute(
		f'SELECT * FROM session WHERE {key}=?',
		(value, ),
	)
	data = cur.fetchone()
	columnTitles = [desc[0] for desc in cur.description]
	cur.close()
	if data is None:
		return None

	result = {}
	for i in range(len(columnTitles)):
		result[columnTitles[i]] = data[i]

	return result


def revokeSessionByVid(*, vid):
	cur = db.cursor()
	cur.execute(
		'DELETE FROM session WHERE vid=?',
		(vid, ),
	)
	affected = cur.rowcount
	cur.close()
	db.commit()
	return affected