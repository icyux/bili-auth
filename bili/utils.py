import json
import time

from misc.requests_session import session as rs
from misc.requests_session import noAuthSession as rnas
from bili import api
import bili


def getNewMsg(beginMts: int, *, recvType: tuple = (1,)):
    r = rs.get(
        f'https://api.vc.bilibili.com/session_svr/v1/session_svr/new_sessions?begin_ts={beginMts}&build=0&mobi_app=web',
        timeout=10,
    )
    resp = r.json()
    assert resp['code'] == 0
    if resp['data'].get('session_list'):
        sessionList = []
    else:
        return []

    ackRequired = False
    for session in resp['data']['session_list']:
        sessionTs = session['session_ts']
        if sessionTs > beginMts:
            ackRequired = True
            beginMts = sessionTs
        if session['unread_count'] == 0:
            continue
        sessionList.append({
            'talkerid': session['talker_id'],
            'beginSeq': session['ack_seqno'],
            'endSeq': session['max_seqno'],
        })

    # ack sessions
    if ackRequired:
        rs.get(
            f'https://api.vc.bilibili.com/session_svr/v1/session_svr/ack_sessions?begin_ts={beginMts}&build=0&mobi_app=web',
        )

    msgList = []
    for s in sessionList:
        url = f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?\
        sender_device_id=1&talker_id={s["talkerid"]}&session_type=1&size=50&begin_seqno={s["beginSeq"]}\
        &build=0&mobi_app=web'
        r = rs.get(
            url,
            headers=bili.authedHeader
        )
        resp = r.json()
        assert resp['code'] == 0
        for m in resp['data']['messages']:
            if not m['msg_type'] in recvType:
                continue
            if m['sender_uid'] == bili.selfUid:
                continue
            if m['msg_type'] == 1:
                content = json.loads(m['content'])['content']
            else:
                content = m['content']
            msgList.append({
                'uid': m['sender_uid'],
                'msgType': m['msg_type'],
                'content': content,
                'ts': m['timestamp'],
                'seq': m['msg_seqno'],
            })

        # update session ack
        updateAck = rs.post(
            'https://api.vc.bilibili.com/session_svr/v1/session_svr/update_ack',
            headers=bili.authedHeader,
            data={
                'talker_id': s['talkerid'],
                'session_type': 1,
                'ack_seqno': s['endSeq'],
                'build': 0,
                'mobi_app': 'web',
                'csrf_token': bili.csrf,
                'csrf': bili.csrf,
            }
        )
        assert updateAck.json()['code'] == 0

    return msgList


def sendMsg(recver: int, content: str, *, msgType: int = 1):
    if msgType == 1:
        content = content.replace('"', '\\"').replace('\n', '\\n')
        content = '{{"content":"{}"}}'.format(content)

    r = rs.post(
        'https://api.vc.bilibili.com/web_im/v1/web_im/send_msg',
        headers=bili.authedHeader,
        data={
            'msg[sender_uid]': bili.selfUid,
            'msg[receiver_id]': recver,
            'msg[receiver_type]': 1,
            'msg[msg_type]': msgType,
            'msg[msg_status]': 0,
            'msg[content]': content,
            'msg[timestamp]': int(time.time()),
            'msg[new_face_version]': 0,
            'msg[dev_id]': bili.selfDevId,
            'csrf': bili.csrf,
            'csrf_token': bili.csrf,
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
    try:
        data = api.request(
            method='GET',
            path='/x/space/wbi/acc/info',
            params={
                'mid': uid,
            },
            wbi=True,
        )
        return {
            'uid': data['mid'],
            'name': data['name'],
            'avatar': data['face'].replace('http://', 'https://'),
            'bio': data['sign'],
        }

    except api.BiliApiError as e:
        # deleted account
        if e.code == -404:
            return {
                'uid': uid,
                'name': None,
                'avatar': None,
                'bio': None,
            }
        else:
            raise e
