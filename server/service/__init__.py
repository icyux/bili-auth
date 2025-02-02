from flask import Flask
import logging

import misc

app = Flask(__name__,
    static_folder='../static',
    static_url_path='/static',
    template_folder='../templates',
)
app.debug = False


# set app version
@app.context_processor
def inject_globals():
    return {
        'version': misc.version,
    }


import service.auth_middleware
import service.oauth
import service.user_info
import service.verify
import service.view


hmacKey = None
