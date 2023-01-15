#!/usr/bin/env -S python3 -u

import toml

from bili import updateCredential
from misc.selenium_utils import *
import misc


misc.config = toml.load('config.toml')
options = Options([])
with ChromeDriver(options=options) as d:
	d.set_script_timeout(10 * 60)
	d.get('https://bilibili.com/')
	refreshTkn = d.runScript('script/login.js')
	cookies = d.dumpCookie()
	updateCredential(cookies, refreshTkn)

print('credential created.')
