import re
import toml
import uuid

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
    selfUid = cfg['uid']
    selfName = cfg['nickname']
    selfDevId = str(uuid.uuid4()).upper()
    ua = cfg['user_agent']
    loadCredential()


def loadCredential():
    cred = toml.load(CREDENTIAL_PATH)
    updateCredential(cred['cookies'], cred['refresh_token'], overwrite=False)


def updateCredential(newCookies, newRefreshTkn, overwrite=True):
    global csrf, cookies, authedHeader, unauthedHeader, refreshTkn
    cookies = loadCookies(newCookies)
    refreshTkn = newRefreshTkn

    csrf = cookies.get('bili_jct')
    if csrf is None:
        errInfo = 'Invalid cookie. Check if the key "bili_jct" included for CSRF verify.'
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
