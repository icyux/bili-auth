import re
import toml
import uuid

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

    # generate random device UUID
    cfg = misc.config['bili']
    if cfg['dev_id'] == '':
        cfg['dev_id'] = str(uuid.uuid4()).upper()

    selfUid = cfg['uid']
    selfName = cfg['nickname']
    selfDevId = cfg['dev_id']
    ua = cfg['user_agent']
    loadCredential()


def loadCredential():
    cred = toml.load(CREDENTIAL_PATH)
    updateCredential(cred['cookies'], cred['refresh_token'], overwrite=False)


def updateCredential(newCookies, newRefreshTkn, overwrite=True):
    global csrf, cookies, authedHeader, unauthedHeader, refreshTkn
    cookies = newCookies
    refreshTkn = newRefreshTkn

    try:
        csrf = re.search(r'bili_jct=(.*?)(?:; |$)', cookies).group(1)
    except AttributeError:
        errInfo = 'Invalid cookie. Check if the key "bili_jct" included for CSRF verify.'
        raise ValueError(errInfo)

    authedHeader = {
        'Cookie': cookies,
        'User-Agent': ua,
        'Origin': 'https://message.bilibili.com',
        'Referer': 'https://message.bilibili.com/',
    }
    unauthedHeader = {'User-Agent': ua}

    if overwrite:
        payload = {
            'cookies': cookies,
            'refresh_token': refreshTkn
        }
        with open(CREDENTIAL_PATH, 'w') as f:
            toml.dump(payload, f)
