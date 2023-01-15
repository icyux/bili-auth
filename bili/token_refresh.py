from selenium import webdriver
from selenium.common import exceptions as seleniumExceptions
import requests
import time

import misc
import bili


def isCookieExpired():
	respPayload = requests.get(
		f'https://passport.bilibili.com/x/passport-login/web/cookie/info?csrf={bili.csrf}',
		headers=bili.authedHeader,
	).json()['data']
	return respPayload['refresh']


def getOptions():
	rawOptions = misc.config['selenium']['options']
	options = webdriver.ChromeOptions()
	for op in rawOptions:
		options.add_argument(op)

	return options


def runScript(driver, path):
	with open(path, encoding='UTF-8') as f:
		script = f.read()

	return driver.execute_script(script)


def setCookie(driver, domain, origCookie):
	pairs = origCookie.split('; ')
	for p in pairs:
		if p == '':
			continue

		k, v = p.split('=')
		driver.add_cookie({
			'domain': domain,
			'name': k,
			'value': v,
			'path': '/',
			'expires': None,
		})


def dumpCookie(driver):
	cookieList = [f'{cookie["name"]}={cookie["value"]}' for cookie in driver.get_cookies()]
	return '; '.join(cookieList)


def fetchNewCookie():
	try:
		# init selenium
		options = getOptions()
		path = misc.config['selenium']['path']
		driver = webdriver.Chrome(executable_path=path, options=options)

		# load credentials
		driver.get('https://bilibili.com/')
		setCookie(driver, '.bilibili.com', bili.cookies)
		driver.execute_script(f'localStorage["ac_time_value"] = "{bili.refreshTkn}"')
		driver.refresh()

		# fetch refreshed credentials
		newRefreshTkn = runScript(driver, 'script/listen_refresh_token.js')
		newCookies = dumpCookie(driver)
		return newCookies, newRefreshTkn

	finally:
		driver.close()


def autoRefreshLoop():
	while True:
		isExpired = isCookieExpired()
		if isExpired:
			try:
				newCookies, newRefreshTkn = fetchNewCookie()
				bili.updateCredential(newCookies, newRefreshTkn)
				misc.logger.info('cookie refreshed')
			except seleniumExceptions.JavascriptException:
				misc.logger.warn('cookie refresh failed')

		else:
			time.sleep(5 * 60)
