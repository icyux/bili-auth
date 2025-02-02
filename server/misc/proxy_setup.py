import logging

import misc
from misc import requests_session

def init():
	proxyPref = misc.config['proxy']
	isEnabled = proxyPref['enable']

	if isEnabled:
		typ = proxyPref['type']
		addr = proxyPref['addr']
		addrUrl = f'{typ}://{addr}'
		isGlobal = proxyPref['globalProxy']

		# requests proxy
		requests_session.session.proxies = {
			'all': addrUrl,
		}

		if isGlobal:
			requests_session.noAuthSession = requests_session.session
			logging.info('proxy enabled (global)')
		else:
			logging.info('proxy enabled')
