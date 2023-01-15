from selenium import webdriver

import misc


class Options(webdriver.ChromeOptions):
	def __init__(self, rawOptions):
		super().__init__()
		for op in rawOptions:
			super().add_argument(op)


class ChromeDriver(webdriver.Chrome):
	def __init__(self, *, options=None):
		if options is None:
			options = Options(misc.config['selenium']['options'])
		path = misc.config['selenium']['path']
		super().__init__(executable_path=path, options=options)


	def runScript(self, path):
		with open(path, encoding='UTF-8') as f:
			script = f.read()

		return self.execute_script(script)


	def setCookie(self, domain, origCookie):
		pairs = origCookie.split('; ')
		for p in pairs:
			if p == '':
				continue

			k, v = p.split('=')
			self.add_cookie({
				'domain': domain,
				'name': k,
				'value': v,
				'path': '/',
				'expires': None,
			})


	def dumpCookie(self):
		cookieList = [f'{cookie["name"]}={cookie["value"]}' for cookie in self.get_cookies()]
		return '; '.join(cookieList)
