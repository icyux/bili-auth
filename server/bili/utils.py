import json
import logging
import re
import time
import urllib.parse

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
        params={
            'w_sender_uid': bili.selfUid,
            'w_receiver_id': recver,
            'w_dev_id': bili.selfDevId,
        },
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
            'from_firework': 0,
            'build': 0,
            'mobi_app': 'web',
            'csrf_token': bili.csrf,
            'csrf': bili.csrf,
        },
        credential=True,
        wbi=True,
    )
    return data['msg_key']


def getWebId(uid: int):
    data = api.request(
        method='GET',
        sub='space',
        path=f'/{uid}',
        headers={
            'Referer': 'https://www.bilibili.com/',
        },
        json_response=False,
    )
    match = re.search('<script id="__RENDER_DATA__" type="application/json">(.+)</script>', data)
    if match is None:
        raise ValueError('access_id not found in the response')

    payload = json.loads(urllib.parse.unquote(match.group(1)))
    webId = payload['access_id']
    return webId


def getUserInfo(uid: int):
    try:
        webId = getWebId(uid)
        data = api.request(
            method='GET',
            path='/x/space/wbi/acc/info',
            params={
                'mid': uid,
                'token': '',
                'platform': 'web',
                'web_location': '1550101',
                'dm_img_list': '[]',
                # base64("WebGL 1.0 (OpenGL ES 2.0 Chromium)")
                'dm_img_str': 'V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ',
                # base64("ANGLE (Intel, Intel(R) HD Graphics 4600 (0x00000416) Direct3D11 vs_5_0 ps_5_0, D3D11)Google Inc. (Intel")
                'dm_cover_img_str': 'QU5HTEUgKEludGVsLCBJbnRlbChSKSBIRCBHcmFwaGljcyA0NjAwICgweDAwMDAwNDE2KSBEaXJlY3QzRDExIHZzXzVfMCBwc181XzAsIEQzRDExKUdvb2dsZSBJbmMuIChJbnRlbC',
                'dm_img_inter': '{"ds":[],"wh":[3874,3583,8],"of":[98,196,98]}',
                'w_webid': webId,
            },
            headers={
                'Origin': 'https://space.bilibili.com',
                'Referer': f'https://space.bilibili.com/{uid}',
            },
            wbi=True,
        )
        return {
            'uid': data['mid'],
            'name': data['name'],
            'avatar': data['face'].replace('http://', 'https://'),
            'raw_data': data,
        }

    except api.BiliApiError as e:
        # deleted account
        if e.code == -404:
            return {
                'uid': uid,
                'name': None,
                'avatar': None,
                'raw_data': None,
            }
        else:
            raise e
