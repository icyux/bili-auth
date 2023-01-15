from flask import Flask
import logging
import sys

import misc

app = Flask(__name__,
    static_folder='../static',
    static_url_path='/static',
    template_folder='../templates',
)
app.debug = False

# setup logger
app.logger.setLevel(logging.INFO)
misc.logger = app.logger

import service.auth_middleware
import service.bili_proxy
import service.oauth
import service.verify
import service.view


hmacKey = None
