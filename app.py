#!/usr/bin/env -S python3 -u

import base64
import secrets
import sqlite3
import threading
import toml

from misc import proxy_setup
import misc
import service
import bili
import bili.token_refresh
import model


# read config
misc.config = toml.load('config.toml')

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
model.initDB(sqlite3.connect('oauth_application.db3', check_same_thread=False))

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

# run oauth http service
host = misc.config['oauth_service']['host']
port = misc.config['oauth_service']['port']
service.app.run(host=host, port=port)
