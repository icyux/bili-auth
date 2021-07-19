#!/bin/python3

import json
import secrets
from flask import Flask, request
import auth_handler

subject = 'https://www.icyu.me'
app = Flask(__name__)


@app.route('/verify/<code>', methods=('GET',))
def queryInfo(code):
    result = auth_handler.getVerifyInfo(code)
    if result:
        return json.dumps(result), 200
    else:
        return '', 404


@app.route('/verify', methods=('POST',))
def createVerify():
    code = auth_handler.createVerify(subject)
    print(repr(code))
    return code


@app.route('/verify/<code>', methods=('DELETE',))
def delVerify(code):
    uid = request.args.get('uid')
    if not uid:
        return '', 400
    try:
        result = auth_handler.revokeVerify(code, int(uid))
        if result:
            return '', 200
        else:
            return '', 404
    except ValueError:
        return '', 400
