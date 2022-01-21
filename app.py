#!/usr/bin/env python3

import uuid
import threading
import oauth
import bili_utils
import config_reader
import auth_handler
import msg_handler


# read config
cfg = config_reader.readConfig('config.json')

# generate random device UUID
biliCfg = cfg['bili']
if biliCfg['dev_id'] == '':
	biliCfg['dev_id'] = str(uuid.uuid4()).upper()

# fill config into bili_utils
bili_utils.init(**biliCfg)

# run message listener
auth_handler.initPool()
msgThread = threading.Thread(target=msg_handler.mainLoop)
msgThread.daemon = True
msgThread.start()

# run oauth http service
oauth.app.run(**cfg['oauth_service'])
