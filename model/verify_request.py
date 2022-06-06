import secrets
import sqlite3
import time

from model import session
from bili.msg_handler import tasks


db = None
vidLen = 8
vidCharset = '0123456789abcdefghijklmnopqrstuvwxyz'
verifyReqMaxAge = 360
verifySuccMaxAge = 86400


def setDB(mainDB):
	global db
	db = mainDB


def isVidExisted(vid):
	cur = db.cursor()
	cur.execute(
		'SELECT 1 FROM verify WHERE vid=?',
		(vid, ),
	)
	result = cur.fetchone()
	cur.close()
	return (result is None)


def randVid():
	return ''.join([secrets.choice(vidCharset) for _ in range(vidLen)])


def generateVid():
	vid = randVid()
	while not isVidExisted(vid):
		vid = randVid()
	return vid


def createVerify(*, userAgent=None):
	vid = generateVid()
	create = int(time.time())
	expire = create + verifyReqMaxAge
	cur = db.cursor()
	cur.execute(
		'INSERT INTO verify ("vid", "create", "expire", "ua") VALUES (?,?,?,?)',
		(vid, create, expire, userAgent),
	)
	affected = cur.rowcount
	cur.close()
	db.commit()
	if affected == 1:
		tasks.put(expire)
		return vid, expire
	else:
		return None


def getVerifyInfo(vid):
	cur = db.cursor()
	cur.execute(
		'SELECT "create", "expire", "ua", "uid" FROM verify WHERE vid=?',
		(vid, ),
	)
	result = cur.fetchone()
	cur.close()
	if result is None:
		return None
	else:
		return {
			'vid': vid,
			'create': result[0],
			'expire': result[1],
			'ua': result[2],
			'isAuthed': result[3] is not None,
			'uid': result[3],
		}


def checkVerify(*, vid, uid):
	ts = int(time.time())
	expire = ts + verifySuccMaxAge
	cur = db.cursor()
	cur.execute(
		'UPDATE verify SET uid=?, expire=? WHERE vid=? AND expire>?',
		(uid, expire, vid, ts),
	)
	affected = cur.rowcount
	cur.close()
	db.commit()
	return (affected == 1)


def revokeVerify(*, vid, uid):
	cur = db.cursor()
	cur.execute(
		'DELETE FROM verify WHERE vid=? AND uid=?',
		(vid, uid),
	)
	affected = cur.rowcount
	cur.close()
	if affected == 1:
		return session.revokeSessionByVid(vid=vid)
	else:
		return None
