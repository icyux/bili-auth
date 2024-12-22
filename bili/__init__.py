import logging
import re
import sys
import toml
import uuid

from bili import api
from misc.requests_session import session as rs
from misc.requests_session import noAuthSession as rnas
from misc.cookie import dumpCookies, loadCookies
import misc


CREDENTIAL_PATH = 'credential.toml'


selfUid = ''
selfName = ''
selfDevId = ''
ua = ''
csrf = ''
cookies = ''
refreshTkn = ''
authedHeader = None
unauthedHeader = None


def init():
    global selfUid, selfName, selfDevId, ua

    cfg = misc.config['bili']
    selfDevId = str(uuid.uuid4()).upper()
    ua = cfg['user_agent']
    loadCredential()

    try:
        resp = api.request(
            path='/x/web-interface/nav',
            credential=True,
            headers={
                'Origin': 'https://www.bilibili.com',
                'Referer': 'https://www.bilibili.com/',
            }
        )
        selfUid = resp['mid']
        selfName = resp['uname']
        logging.info(f'logged in as @{selfName} (uid: {selfUid})')

    except api.BiliApiError as e:
        if e.code == -101:
            logging.error('Session expired. Log in again and refresh the credentials')
            sys.exit(1)
        else:
            raise e


def loadCredential():
    cred = toml.load(CREDENTIAL_PATH)
    updateCredential(cred['cookies'], cred['refresh_token'], overwrite=False)


def updateCredential(newCookies, newRefreshTkn, overwrite=True):
    global csrf, cookies, authedHeader, unauthedHeader, refreshTkn
    cookies = loadCookies(newCookies)
    refreshTkn = newRefreshTkn

    csrf = cookies.get('bili_jct')
    if csrf is None:
        errInfo = 'Missing "bili_jct" in the cookies'
        raise ValueError(errInfo)

    authedHeader = {
        'User-Agent': ua,
        'Origin': 'https://message.bilibili.com',
        'Referer': 'https://message.bilibili.com/',
    }
    rs.headers = authedHeader
    rs.cookies.update(cookies)
    unauthedHeader = {'User-Agent': ua}
    rnas.headers = unauthedHeader

    if overwrite:
        payload = {
            'cookies': dumpCookies(cookies),
            'refresh_token': refreshTkn
        }
        with open(CREDENTIAL_PATH, 'w') as f:
            toml.dump(payload, f)
