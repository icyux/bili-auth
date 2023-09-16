#!/usr/bin/env -S python3 -u

import base64
import logging
import secrets
import sqlite3
import threading
import toml

from misc import proxy_setup
from model import execute_wrapper
import misc
from service import app
import service
import bili
import bili.token_refresh
import model


# init bili utils
bili.init()

# init proxy
proxy_setup.init()

# generate global HMAC key
hmacKey = base64.b64decode(misc.config['oauth_service']['hmac_key'])
if hmacKey == b'':
	hmacKey = secrets.token_bytes(64)

service.hmacKey = hmacKey

# connect database
dbCfg = misc.config['database']
dbType = dbCfg['type']

if dbType == 'sqlite3':
	model.initDB(sqlite3.connect(dbCfg['path'], check_same_thread=False))

elif dbType == 'mysql':
	model.initDB(execute_wrapper.WrappedMysqlConn(
		host=dbCfg['host'],
		port=dbCfg['port'],
		db=dbCfg['db'],
		user=dbCfg['user'],
		passwd=dbCfg['pswd'],
	))

else:
	raise ValueError('unsupported database type')

# run message listener
msgThread = threading.Thread(target=bili.msg_handler.mainLoop)
msgThread.daemon = True
msgThread.start()

# enable periodic wakeup
wakerThread = threading.Thread(target=bili.msg_handler.periodicWakeup)
wakerThread.daemon = True
wakerThread.start()

# token auto refresh
refreshThread = threading.Thread(target=bili.token_refresh.autoRefreshLoop)
refreshThread.daemon = True
refreshThread.start()

# selenium self-test
if misc.config['debug']['seleniumTest'] == True:
	bili.token_refresh.seleniumSelfTest()
