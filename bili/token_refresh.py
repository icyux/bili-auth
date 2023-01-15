from selenium import webdriver
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
	options = getOptions()
	path = misc.config['selenium']['path']
	driver = webdriver.Chrome(executable_path=path, options=options)
	driver.get('https://www.bilibili.com/')
	setCookie(driver, '.bilibili.com', bili.cookies)
	driver.execute_script(f'localStorage.ac_time_value = "{bili.refreshTkn}"')
	driver.refresh()
	time.sleep(10)
	newRefreshTkn = driver.execute_script('return localStorage.ac_time_value')
	newCookies = dumpCookie(driver)
	driver.close()
	return newCookies, newRefreshTkn


def autoRefreshLoop():
	while True:
		isExpired = isCookieExpired()
		if isExpired:
			newCookies, newRefreshTkn = fetchNewCookie()
			bili.updateCredential(newCookies, newRefreshTkn)
			misc.logger.info('cookie refreshed')
		else:	
			time.sleep(300)
