#!/usr/bin/env -S python3 -u

import base64
import secrets
import sqlite3
import threading
import uuid

from bili import msg_handler
from misc import config_reader
import bili
import model
import service


# read config
cfg = config_reader.readConfig('config.json')

# generate random device UUID
biliCfg = cfg['bili']
if biliCfg['dev_id'] == '':
	biliCfg['dev_id'] = str(uuid.uuid4()).upper()

# fill config into bili utils
bili.init(**biliCfg)

# generate global HMAC key
hmacKey = base64.b64decode(cfg['oauth_service']['hmac_key'])
if hmacKey == b'':
	hmacKey = secrets.token_bytes(64)

service.hmacKey = hmacKey

# connect database
model.initDB(sqlite3.connect('oauth_application.db3', check_same_thread=False))


# set logger
msg_handler.logger = service.app.logger

# run message listener
msgThread = threading.Thread(target=msg_handler.mainLoop)
msgThread.daemon = True
msgThread.start()

# enable periodic wakeup
wakerThread = threading.Thread(target=msg_handler.periodicWakeup)
wakerThread.daemon = True
wakerThread.start()

# run oauth http service
host = cfg['oauth_service']['host']
port = cfg['oauth_service']['port']
service.app.run(host=host, port=port)
