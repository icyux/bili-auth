import time
import re
from random import random
import bili_utils
import queue; tasks = queue.Queue()  # initialization tasks queue
import requests
import verify_request as vr

sendCD = 1

patt = re.compile(r'^\s*?/\s*?(\S+?)(?:\s+?(\S+?)?\s*?$|\s*$)', re.IGNORECASE)
ackMts = int(time.time() * 1000)
lastSendTs = 0

aboutText = '''【 bili-auth 】 是一个第三方实现的 Bili OAuth API，基于私信验证用户对帐号的所有权。
它可以让用户使用哔哩哔哩帐号，完成第四方应用鉴权。
提供通用的 OAuth2.0 API，应用可快速接入。
代码开源，开发者可本地部署。
更多信息，您可以访问 GitHub: vapehacker/bili-auth 。
'''

def checkMsg():
    global ackMts
    msgList = bili_utils.getNewMsg(ackMts)
    for m in msgList:
        uid = m['uid']
        content = m['content']
        ts = m['ts']
        result = patt.search(content)
        if result:
            action = result.group(1).lower()
            arg = result.group(2)
            if action in ('auth', 'revoke', 'about'):
                cmdHandler(uid, action, arg)
        ackMts = max(ts * 1000, ackMts)


def cmdHandler(uid, action, arg):
    if action == 'auth':
        vid = arg.lower()
        if vr.checkVerify(vid=vid, uid=uid):
            info = vr.getVerifyInfo(vid)
            try:
                ua = info['ua'].split(';')
                platform, browser = ua[0], ua[1]
            except (AttributeError, IndexError):
                platform, browser = '未知', '未知'

            reply = '\n'.join((
                '【 bili-auth 】 验证完成。',
                f'发起验证的用户操作系统：{platform}，',
                f'浏览器（仅供参考）：{browser}。',
                f'如果此次请求为意外发出, 请回复"/revoke {vid}"以撤销此次验证。',
                '此消息是自动回复。您可以发送"/about"了解本项目。',
            ))
        else:
            reply = '【 bili-auth 】 未找到此验证请求, 可能是此验证信息已过期。请尝试重新发起验证。'
        sendText(uid, reply)
    elif action == 'revoke':
        vid = arg.lower()        
        if vr.revokeVerify(vid=vid, uid=uid):
            reply = '【 bili-auth 】 撤销成功。\nvid: {}\n对应的应用授权已立即被全部撤销，但生效时间取决于第四方应用的实现。'
            reply = reply.format(arg)
        else:
            reply = '【 bili-auth 】 未找到此 vid 对应的验证信息。'
        sendText(uid, reply)
    elif action == 'about':
        sendText(uid, aboutText)


def sendText(uid, content):
    print(f'[send -> {uid}]', content)
    sleepTime = lastSendTs + sendCD - time.time()
    if sleepTime > 0:
        time.sleep(sleepTime)
    bili_utils.sendMsg(uid, content)


def periodicWakeup():
    while True:
        expire = int(time.time()) + 1
        tasks.put(expire)
        time.sleep(5*60)


def mainLoop():
    maxExpire = 0
    while True:

        while maxExpire < time.time():
            curExpire = tasks.get()
            if curExpire > maxExpire:
                maxExpire = curExpire

        try:
            checkMsg()
        except requests.exceptions.RequestException as e:
            print(e)

        time.sleep(4 + random() * 2)

