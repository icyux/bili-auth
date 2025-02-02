import json
import logging
import time

from bili import api
from bili import utils as bu
import model


def initDB():
	global db
	db = model.db


def queryUserInfo(uid, *, maxAge=86400*7):
	cur = db.cursor()
	cur.execute(
		'SELECT uid, name, avatar, raw_data, updateTs FROM users WHERE uid=?',
		(uid, ),
	)
	data = cur.fetchone()
	cur.close()

	if data is None:
		return None

	expireTs = data[4] + maxAge
	if int(time.time()) > expireTs:
		return None

	return {
		'uid': data[0],
		'name': data[1],
		'avatar': data[2],
		'raw_data': json.loads(data[3]) if data[3] is not None else None,
		# update time could be hidden
		# 'updateTs': data[4],
	}


def updateUserInfo(uid, data):
	cur = db.cursor()
	try:
		cur.execute(
			'REPLACE INTO users (uid, name, avatar, raw_data, updateTs) VALUES (?, ?, ?, ?, ?)',
			(uid, data['name'], data['avatar'], json.dumps(data['raw_data']) if data['raw_data'] is not None else None, int(time.time())),
		)
		return cur.rowcount >= 1

	finally:
		cur.close()
		db.commit()


def mustQueryUserInfo(uid):
	# query from DB
	cachedUserInfo = queryUserInfo(uid)
	if cachedUserInfo is not None:
		return cachedUserInfo

	# refresh user info
	try:
		userInfo = bu.getUserInfo(uid)

	except api.BiliApiError as e:
		logging.warn(f'failed to fetch "{e.url}": {repr(e)}')
		raise e

	isSucc = updateUserInfo(uid, userInfo)
	if isSucc:
		return userInfo
	else:
		raise Exception('failed to update DB')
