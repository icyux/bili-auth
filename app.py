#!/usr/bin/env python3

import base64
import secrets
import sqlite3
import threading
import uuid

from bili import msg_handler
from service import oauth
from misc import config_reader
from model import session
from model import verify_request as vr
import bili


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
