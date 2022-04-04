#!/usr/bin/env python3

import uuid
import threading
import oauth
import bili_utils
import config_reader
import msg_handler
import verify_request as vr
import session
import sqlite3
import secrets
import base64


# read config
cfg = config_reader.readConfig('config.json')

# generate random device UUID
biliCfg = cfg['bili']
if biliCfg['dev_id'] == '':
	biliCfg['dev_id'] = str(uuid.uuid4()).upper()

# fill config into bili_utils
bili_utils.init(**biliCfg)

# generate global HMAC key
hmacKey = base64.b64decode(cfg['oauth_service']['hmac_key'])
if hmacKey == b'':
	hmacKey = secrets.token_bytes(64)

oauth.hmacKey = hmacKey

# connect database
db = sqlite3.connect('oauth_application.db3', check_same_thread=False)
vr.setDB(db)
session.setDB(db)
oauth.setDB(db)

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
oauth.app.run(host=host, port=port)
