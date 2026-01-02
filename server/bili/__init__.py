import logging
import re
import requests
import sys
import time
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

userAgentExp = 0


def init():
    global selfUid, selfName, selfDevId, ua

    cfg = misc.config['bili']
    selfDevId = str(uuid.uuid4()).upper()
    ua = cfg.get('user_agent')
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
    global csrf, cookies, refreshTkn

    checkUserAgent()
    cookies = loadCookies(newCookies)
    refreshTkn = newRefreshTkn

    csrf = cookies.get('bili_jct')
    if csrf is None:
        errInfo = 'Missing "bili_jct" in the cookies'
        raise ValueError(errInfo)

    rs.cookies.update(cookies)

    if overwrite:
        payload = {
            'cookies': dumpCookies(cookies),
            'refresh_token': refreshTkn
        }
        with open(CREDENTIAL_PATH, 'w') as f:
            toml.dump(payload, f)


def updateHeader():
    global authedHeader, unauthedHeader
    authedHeader = {
        'User-Agent': ua,
        'Origin': 'https://message.bilibili.com',
        'Referer': 'https://message.bilibili.com/',
    }
    rs.headers = authedHeader
    unauthedHeader = {'User-Agent': ua}
    rnas.headers = unauthedHeader


def checkUserAgent():
    global ua, userAgentExp
    if misc.config['bili'].get('auto_user_agent') is True and time.time() > userAgentExp:
        latestChromeVersion = getLatestChromeVersion()
        latestUserAgent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{latestChromeVersion}.0.0.0 Safari/537.36'
        if ua != latestUserAgent:
            ua = latestUserAgent
            logging.info(f'updated user agent to Chrome {latestChromeVersion}')
        updateHeader()
        userAgentExp = time.time() + 86400


def getLatestChromeVersion():
    try:
        # API provided by chrome-mask <https://github.com/denschub/chrome-mask/blob/main/src/shared.js>
        url = 'https://chrome-mask-remote-storage.0b101010.services/current-chrome-major-version.txt'
        latestChromeVersion = rnas.get(url, timeout=10).text
        return latestChromeVersion
    except requests.exceptions.RequestException as e:
        fallbackVersion = '143'
        logging.warning(f'fetching latest Chrome version failed: {e}. fallback to {fallbackVersion}')
        return fallbackVersion
