import sqlite3
import time
import secrets

db = None
vidMax = 10**10
clgCodeLen = 8
clgCodeChars = '1234567890qwertyuiopasdfghjklzxcvbnm'
verifyReqMaxAge = 360

def setDB(mainDB):
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


def isClgCodeExisted(clgCode):
	cur = db.cursor()
	cur.execute(
		'SELECT 1 FROM verify WHERE clgCode=?',
		(clgCode, ),
	)
	result = cur.fetchone()
	cur.close()
	return (result is None)


def generateVid():
	vid = secrets.randbelow(vidMax)
	while not isVidExisted(vid):
		vid = secrets.randbelow(vidMax)
	return vid


def randClgCode():
	return ''.join([secrets.choice(clgCodeChars) for _ in range(clgCodeLen)])


def generateClgCode():
	clgCode = randClgCode()
	while not isClgCodeExisted(vid):
		clgCode = randClgCode()
	return clgCode


def createVerify():
	vid = generateVid()
	clgCode = generateClgCode()
	create = int(time.time())
	expire = create + verifyReqMaxAge
	cur = db.cursor()
	affected = cur.execute(
		'INSERT INTO verify (vid, clgCode, create, expire) VALUES (?,?,?,?)',
		(vid, clgCode, create, expire),
	)
	cur.close()
	if affected == 1:
		return clgCode
	else:
		return None


def checkVerify(*, clgCode, uid):
	ts = int(time.time())
	cur = db.cursor()
	affected = cur.execute(
		'UPDATE verify SET uid=? WHERE clgCode=? AND expire>?',
		(uid, clgCode, ts),
	)
	return (affected == 1)

