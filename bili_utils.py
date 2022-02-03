import requests
import time
import re
import json

selfUid = ''
selfDevId = ''
ua = ''
csrf = ''
authedHeader = None
unauthedHeader = None

def init(*, uid, cookie, dev_id, user_agent):
    global selfUid, selfDevId, csrf, ua, authedHeader, unauthedHeader
    selfUid = uid
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


def getNewMsg(beginMts: int, *, recvType: tuple = (1,)):
    beginMts -= 1
    r = requests.get(
        f'https://api.vc.bilibili.com/session_svr/v1/session_svr/new_sessions?begin_ts={beginMts}&build=0&mobi_app=web',
        headers=authedHeader
    )
    requests.get(
        f'https://api.vc.bilibili.com/session_svr/v1/session_svr/ack_sessions?begin_ts={beginMts}&build=0&mobi_app=web',
        headers=authedHeader
    )
    resp = r.json()
    assert resp['code'] == 0
    if resp['data'].get('session_list'):
        sessionList = []
    else:
        return []

    for session in resp['data']['session_list']:
        if session['unread_count'] == 0:
            continue
        sessionList.append({
            'talkerid': session['talker_id'],
            'beginSeq': session['ack_seqno'],
            'endSeq': session['ack_seqno'] + session['unread_count'],
        })

    msgList = []
    for s in sessionList:
        url = f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?\
        sender_device_id=1&talker_id={s["talkerid"]}&session_type=1&size=50&begin_seqno={s["beginSeq"]}\
        &build=0&mobi_app=web'
        r = requests.get(
            url,
            headers=authedHeader
        )
        updateAck = requests.post(
            'https://api.vc.bilibili.com/session_svr/v1/session_svr/update_ack',
            headers=authedHeader,
            data={
                'talker_id': s['talkerid'],
                'session_type': 1,
                'ack_seqno': s['endSeq'],
                'build': 0,
                'mobi_app': 'web',
                'csrf_token': csrf,
                'csrf': csrf,
            }
        )
        assert updateAck.json()['code'] == 0
        resp = r.json()
        assert resp['code'] == 0
        for m in resp['data']['messages']:
            if not m['msg_type'] in recvType:
                continue
            if m['sender_uid'] == selfUid:
                continue
            if m['msg_type'] == 1:
                content = json.loads(m['content'])['content']
            else:
                content = m['content']
            # logging.info(f'recv msg: uid={m["sender_uid"]}, content={content}')
            msgList.append({
                'uid': m['sender_uid'],
                'msgType': m['msg_type'],
                'content': content,
                'ts': m['timestamp'],
                'seq': m['msg_seqno'],
            })
    return msgList


def sendMsg(recver: int, content: str, *, msgType: int = 1):
    if msgType == 1:
        content = content.replace('"', '\\"')
        content = '{{"content":"{}"}}'.format(content)
        print(content)
    r = requests.post(
        'https://api.vc.bilibili.com/web_im/v1/web_im/send_msg',
        headers=authedHeader,
        data={
            'msg[sender_uid]': selfUid,
            'msg[receiver_id]': recver,
            'msg[receiver_type]': 1,
            'msg[msg_type]': msgType,
            'msg[msg_status]': 0,
            'msg[content]': content,
            'msg[timestamp]': int(time.time()),
            'msg[new_face_version]': 0,
            'msg[dev_id]': selfDevId,
            'csrf': csrf,
            'csrf_token': csrf,
            'from_firework': 0,
            'build': 0,
            'mobi_app': 'web',
        }
    )
    resp = r.json()
    if resp['code'] == 0:
        return resp['data']['msg_key']
    return False


def getUserInfo(uid: int):
    r = requests.get(
        f'https://api.bilibili.com/x/space/acc/info?mid={uid}&jsonp=jsonp',
        headers=unauthedHeader
    )
    resp = r.json()
    try:
        return {
            'uid': resp['data']['mid'],
            'nickname': resp['data']['name'],
            'avatar': resp['data']['face'].replace('http://', 'https://'),
            'bio': resp['data']['sign'],
        }
    except IndexError:
        return None
