from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import binascii
import logging
import re
import time

from misc.cookie import dumpCookies, loadCookies
from misc.requests_session import session
from bili import api
import bili

def isRefreshPreferred():
    data = api.request(
        method='GET',
        sub='passport',
        path='/x/passport-login/web/cookie/info',
        params={
            'csrf': bili.csrf,
        },
        credential=True,
    )
    return data['refresh']


# <https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/login/cookie_refresh.md>
def fetchNewCookie():
    pubKey = RSA.importKey('''\
        -----BEGIN PUBLIC KEY-----
        MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLgd2OAkcGVtoE3ThUREbio0Eg
        Uc/prcajMKXvkCKFCWhJYJcLkcM2DKKcSeFpD/j6Boy538YXnR6VhcuUJOhH2x71
        nzPjfdTcqMz7djHum0qSZA0AyCBDABUqCrfNgCiJ00Ra7GmRj+YCK1NJEuewlb40
        JNrRuoEUXpabUzGB8QIDAQAB
        -----END PUBLIC KEY-----'''.replace('  ', '').replace('\t', ''))
    cipher = PKCS1_OAEP.new(pubKey, SHA256)

    ts = int(time.time() * 1000)
    encrypted = cipher.encrypt(f'refresh_{ts}'.encode())
    payload = binascii.b2a_hex(encrypted).decode()
    raw_data = api.request(
        sub='www',
        path=f'/correspond/1/{payload}',
        credential=True,
        json_response=False,
    )
    match = re.search('<div id="1-name">(.+)</div>', raw_data)
    if match is None:
        raise ValueError('unexpected response format')
    refreshCsrf = match.group(1)

    resp = api.request(
        method='POST',
        sub='passport',
        path='/x/passport-login/web/cookie/refresh',
        data={
            'csrf': bili.csrf,
            'refresh_csrf': refreshCsrf,
            'source': 'main_web',
            'refresh_token': bili.refreshTkn,
        },
        credential=True,
    )
    newRefreshTkn = resp['refresh_token']
    newCsrf = session.cookies.get_dict
    newCookies = session.cookies.get_dict()
    newCookieStr = dumpCookies(newCookies)

    resp = api.request(
        method='POST',
        sub='passport',
        path='/x/passport-login/web/confirm/refresh',
        data={
            'csrf': newCookies['bili_jct'],
            'refresh_token': bili.refreshTkn,
        },
        credential=True,
    )

    return newCookieStr, newRefreshTkn


def autoRefreshLoop():
    while True:
        try:
            isExpired = isRefreshPreferred()
        except Exception as e:
            logging.warn(f'checking cookie status failed: {repr(e)}')
            time.sleep(5 * 60)  # 5 minutes interval
            continue

        if isExpired:
            logging.info('cookie expired. refreshing...')
            newCookies, newRefreshTkn = fetchNewCookie()
            bili.updateCredential(newCookies, newRefreshTkn)
            logging.info('cookie refreshed')

        else:
            logging.info('cookie alive')
            time.sleep(5 * 3600)  # 5 hours interval
