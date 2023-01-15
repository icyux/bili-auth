from selenium.common import exceptions as seleniumExceptions
import time

from misc.requests_session import session as rs
from misc.selenium_utils import ChromeDriver
import misc
import bili


def isCookieExpired():
	respPayload = rs.get(
		f'https://passport.bilibili.com/x/passport-login/web/cookie/info?csrf={bili.csrf}',
		headers=bili.authedHeader,
	).json()['data']
	return respPayload['refresh']


def fetchNewCookie():
	with ChromeDriver() as d:
		# load credentials
		d.get('https://bilibili.com/')
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
				newCookies, newRefreshTkn = fetchNewCookie()
				bili.updateCredential(newCookies, newRefreshTkn)
				misc.logger.info('cookie refreshed')
			except seleniumExceptions.JavascriptException:
				misc.logger.warn('cookie refresh failed')

		else:
			time.sleep(5 * 60)
