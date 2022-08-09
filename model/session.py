import secrets
import sqlite3
import time

from model import verify_request as vr
import model


accCodeLen = 16
tokenLen = 24


def initDB():
	global db
	db = model.db


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
	newAccCode = secrets.token_urlsafe(accCodeLen)
	cur = db.cursor()
	cur.execute(
		'UPDATE session SET accCode=?, token=? WHERE cid=? AND accCode=?',
		(newAccCode, token, cid, accCode),
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


def getSessionsByUid(uid, cid=None):
	cur = db.cursor()
	if cid is None:
		cur.execute(
			'SELECT * FROM session WHERE uid=?',
			(uid, ),
		)
	else:
		cur.execute(
			'SELECT * FROM session WHERE uid=? AND cid=?',
			(uid, cid),
		)

	cols = [desc[0] for desc in cur.description]
	rows = cur.fetchall()
	result = [{cols[i]:row[i] for i in range(len(cols))} for row in rows]
	cur.close()
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
