#!/usr/bin/env -S python3 -u

from apscheduler.schedulers.background import BackgroundScheduler
import base64
import datetime
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
import bili.utils
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

# run task scheduler
logging.getLogger('apscheduler').setLevel(logging.WARNING)
scheduler = BackgroundScheduler()
scheduler.add_job(
	bili.msg_handler.periodicWakeup,
	'interval',
	minutes=5,
	next_run_time=datetime.datetime.now(),
	id='msg_periodic_poll'
)
scheduler.add_job(
	bili.token_refresh.autoRefresh,
	'interval',
	hours=5,
	next_run_time=datetime.datetime.now(),
	id='token_refresh'
)
scheduler.start()

# run message listener
msgThread = threading.Thread(target=bili.msg_handler.mainLoop)
msgThread.daemon = True
msgThread.start()

if __name__ == '__main__':
	host = misc.config['service']['host']
	port = misc.config['service']['port']
	app.run(host=host, port=port)
