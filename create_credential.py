#!/usr/bin/env -S python3 -u

import toml

from bili import updateCredential
from misc import proxy_setup
from misc.selenium_utils import *
import misc


misc.config = toml.load('config.toml')
proxy_setup.init()
options = Options([])
with ChromeDriver(options=options) as d:
	d.set_script_timeout(10 * 60)
	d.get('https://bilibili.com/')
	refreshTkn = d.runScript('script/login.js')
	d.get('https://space.bilibili.com/')
	cookies = d.dumpCookie()
	updateCredential(cookies, refreshTkn)

print('credential created.')
