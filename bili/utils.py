import json
import logging
import time

from bili import api
import bili


def getNewMsg(beginMts: int, *, recvType: tuple = (1,)):
    data = api.request(
        method='GET',
        sub='api.vc',
        path='/session_svr/v1/session_svr/new_sessions',
        params={
            'begin_ts': beginMts,
        },
        credential=True,
        timeout=10,
    )
    if data.get('session_list'):
        sessionList = []
    else:
        return []

    ackRequired = False
    for session in data['session_list']:
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
        api.request(
            method='GET',
            sub='api.vc',
            path='/session_svr/v1/session_svr/ack_sessions',
            params={
                'begin_ts': beginMts,
            },
            credential=True,
        )

    msgList = []
    for s in sessionList:
        data = api.request(
            method='GET',
            sub='api.vc',
            path='/svr_sync/v1/svr_sync/fetch_session_msgs',
            params={
                'talker_id': s["talkerid"],
                'begin_seqno': s["beginSeq"],
                'size': 50,
                'session_type': 1,
            },
            credential=True,
        )
        for m in data['messages']:
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
        api.request(
            method='POST',
            sub='api.vc',
            path='/session_svr/v1/session_svr/update_ack',
            data={
                'talker_id': s['talkerid'],
                'session_type': 1,
                'ack_seqno': s['endSeq'],
                'csrf_token': bili.csrf,
                'csrf': bili.csrf,
            },
            credential=True,
        )

    return msgList


def sendMsg(recver: int, content: str, *, msgType: int = 1):
    if msgType == 1:
        content = content.replace('"', '\\"').replace('\n', '\\n')
        content = '{{"content":"{}"}}'.format(content)

    data = api.request(
        method='POST',
        sub='api.vc',
        path='/web_im/v1/web_im/send_msg',
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
        },
        credential=True,
    )
    return data['msg_key']


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
