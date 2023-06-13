from selenium.common import exceptions as seleniumExceptions
import logging
import time

from bili import api
from misc.selenium_utils import ChromeDriver
import bili


def isCookieExpired():
	data = api.request(
		method='GET',
		sub='passport',
		path='/x/passport-login/web/cookie/info',
		params={
			'csrf': bili.csrf,
		},
		credential=True,
	)
	return data['refresh']


def fetchNewCookie():
	with ChromeDriver() as d:
		d.set_script_timeout(120)
		# load credentials
		d.get('https://www.bilibili.com/')
		d.setCookie('.bilibili.com', bili.cookies)
		d.execute_script(f'localStorage["ac_time_value"] = "{bili.refreshTkn}"')
		d.refresh()

		# fetch refreshed credentials
		newRefreshTkn = d.runScript('script/listen_refresh_token.js')
		newCookies = d.dumpCookie()
		return newCookies, newRefreshTkn


def autoRefreshLoop():
	while True:
		isExpired = isCookieExpired()
		if isExpired:
			try:
				logging.info('cookie expired. refreshing...')
				newCookies, newRefreshTkn = fetchNewCookie()
				bili.updateCredential(newCookies, newRefreshTkn)
				logging.info('cookie refreshed')
			except seleniumExceptions.JavascriptException:
				logging.warn('cookie refresh timeout')
			except seleniumExceptions.WebDriverException as e:
				logging.warn(f'cookie refresh failed: {repr(e)}')

		else:
			logging.info('cookie alive')
			time.sleep(5 * 3600)  # 5 hours interval
