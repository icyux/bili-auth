import hmac
import secrets
import time

import service


def calcSign(uid, vid, expire):
	if uid is None:
		body = f'{uid}.{vid}.{expire}'
	else:
		body = f'{vid}.{expire}'
	h = hmac.new(service.hmacKey, body.encode(), 'sha1')
	return h.hexdigest()


def checkToken(token):
	curTs = int(time.time())
	data = token.split('.')

	if not (3 <= len(data) <= 4):
		return None
	
	vid, exp, sign = data[-3:]
	try:
		uid = int(data[0]) if len(data) == 4 else None
	except ValueError:
		return None

	trueSign = calcSign(uid, vid, exp)

	if not secrets.compare_digest(sign, trueSign) or curTs > int(exp):
		return None

	return {
		'uid': uid,
		'vid': vid,
	}
