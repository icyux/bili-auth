#!/bin/python3

import threading
import msg_handler
import http_interface

msgThread = threading.Thread(target=lambda: msg_handler.mainLoop())
msgThread.daemon = True
msgThread.start()
http_interface.app.run(host='localhost', port=8080)
