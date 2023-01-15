import misc
from misc import selenium_utils
from misc import requests_session

def init():
	proxyPref = misc.config['proxy']
	isEnabled = proxyPref['enable']

	if isEnabled:
		typ = proxyPref['type']
		addr = proxyPref['addr']
		addrUrl = f'{typ}://{addr}'

		# selenium proxy
		selenium_utils.proxy = addrUrl

		# requests proxy
		requests_session.session.proxies = {
			'all': addrUrl,
		}

		misc.logger.info('proxy enabled')
