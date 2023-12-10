from hashlib import md5
import time
import urllib.parse

from misc.requests_session import session as rs
from misc.requests_session import noAuthSession as rnas


wbiKey = None
wbiKeyExp = 0
maxAge = 3600


# todo: raise api error
class BiliApiError(Exception):
	def __init__(self, url, code, msg):
		self.code = code
		self.msg = msg
		self.url = url

	def __repr__(self):
		return f'BiliApiError({self.code}, {self.msg})'

	def __str__(self):
		return repr(self)


def request(*, method='GET', sub='api', path, params=None, data=None, timeout=None, wbi=False, credential=False):
	assert sub in ['api', 'api.vc', 'passport']
	if params is None:
		qs = ''
	elif wbi:
		qs = '?' + wbiSign(params)
	else:
		qs = '?' + encodeParams(params)


	url = f'https://{sub}.bilibili.com{path}{qs}'

	session = rs if credential else rnas
	resp = session.request(method, url, data=data, timeout=timeout)
	resp.raise_for_status()
	body = resp.json()
	if body['code'] != 0:
		raise BiliApiError(url, body['code'], body['message'])

	return body['data']


def wbiSign(params):
	params['wts'] = int(time.time())
	qs = encodeParams(params)
	wbiKey = getWbiKey()
	sign = md5((qs + wbiKey).encode()).hexdigest()
	return f'{qs}&w_rid={sign}'


# reference: <https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/misc/sign/wbi.md>
def getWbiKey():
	global wbiKey, wbiKeyExp
	curTs = int(time.time())
	if curTs > wbiKeyExp:
		# refresh wbi key
		resp = rnas.get('https://api.bilibili.com/x/web-interface/nav')
		resp.raise_for_status()
		data = resp.json()
		k1 = data['data']['wbi_img']['img_url'].rsplit('/', 1)[1].split('.')[0]
		k2 = data['data']['wbi_img']['sub_url'].rsplit('/', 1)[1].split('.')[0]
		k = k1 + k2
		mixinKeyEncTab = [
			46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
			33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
			61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
			36, 20, 34, 44, 52
		]
		wbiKey = ''.join([k[i] for i in mixinKeyEncTab[:32]])
		wbiKeyExp = curTs + maxAge

	return wbiKey


def encodeParams(params):
	params = dict(sorted(params.items()))
	query = urllib.parse.urlencode(params)
	return query

