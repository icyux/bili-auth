import re


selfUid = ''
selfName = ''
selfDevId = ''
ua = ''
csrf = ''
authedHeader = None
unauthedHeader = None


def init(*, uid, cookie, nickname, dev_id, user_agent):
    global selfUid, selfName, selfDevId, csrf, ua, authedHeader, unauthedHeader
    selfUid = uid
    selfName = nickname
    selfDevId = dev_id
    ua = user_agent

    try:
        csrf = re.search(r'bili_jct=(.*?); ', cookie).group(1)
    except AttributeError:
        errInfo = 'Invalid cookie. Check if the key "bili_jct" included for CSRF verify.'
        raise ValueError(errInfo)
    authedHeader = {
        'Cookie': cookie,
        'User-Agent': ua,
        'Origin': 'https://message.bilibili.com',
        'Referer': 'https://message.bilibili.com/',
    }
    unauthedHeader = {'User-Agent': ua}
