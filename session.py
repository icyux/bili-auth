import sqlite3
import secrets
import time

db = None
accCodeLen = 24
tokenLen = 24


def setDB(mainDB):
	db = mainDB


def createSession(*, vid, uid, cid):
	createTs = int(time.time())
	accessCode = secrets.token_urlsafe(accCodeLen)
	cur = db.cursor()
	try:
		affected = cur.execute(
			'INSERT INTO session (vid, uid, cid, create, accCode) VALUES (?,?,?,?,?)',
			(vid, uid, cid, createTs, accessCode),
		)
		assert affected == 1
		cur.execute('SELECT sid FROM session ORDER BY sid DESC LIMIT 1')
		sid = cur.fetchone()[0]
	finally:
		cur.close()

	return sid, accessCode


def generateAccessToken(*, cid, accCode):
	token = secrets.token_urlsafe(tokenLen)
	cur = db.cursor()
	affected = cur.execute(
		'UPDATE session SET token=? WHERE cid=? AND accCode=? and token IS NULL',
		(token, cid, accCode),
	)
	cur.close()
	if affected == 1:
		return token
	else:
		return None


def revokeSessionByVid(*, vid):
	cur = db.cursor()
	affected = cur.execute(
		'DELETE FROM session WHERE vid=?',
		(vid, ),
	)
	cur.close()
	return affected
