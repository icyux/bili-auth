import queue; tasks = queue.Queue()  # initialization tasks queue

from random import random
import logging
import re
import requests
import time

from bili import utils as bu
from model import verify_request as vr

sendCD = 1

patt = re.compile(r'^\s*?/?\s*?(\S+?)(?:\s+?(\S+?)?\s*?$|\s*$)', re.IGNORECASE)
ackMts = int(time.time() * 1000)
lastSendTs = 0

aboutText = '''【 bili-auth 】 是一个第三方实现的 Bili OAuth API，基于私信验证用户对帐号的所有权。
它可以让用户使用哔哩哔哩帐号，完成第四方应用鉴权。
提供通用的 OAuth 2.0 API，应用可快速接入。
代码开源，开发者可本地部署。
更多信息，您可以访问 GitHub: vapehacker/bili-auth 。
'''

def checkMsg():
    global ackMts
    msgList = bu.getNewMsg(ackMts)
    for m in msgList:
        uid = m['uid']
        content = m['content']
        ts = m['ts']
        logging.info(f'recv<-{uid}: {content}')
        result = patt.search(content)
        if result:
            action = result.group(1).lower()
            arg = result.group(2)
            cmdHandler(uid, action, arg)
        ackMts = max(ts * 1000, ackMts)


def cmdHandler(uid, action, arg):
    if action == '确认授权' and arg is not None:
        vid = arg.lower()
        if vr.checkVerify(vid=vid, uid=uid):
            info = vr.getVerifyInfo(vid)
            try:
                ua = info['ua'].split(';')
                platform, browser = ua[0], ua[1]
            except (AttributeError, IndexError):
                platform, browser = '未知', '未知'

            dt = time.strftime('%Y-%m-%d %H:%M:%S (UTC%z)', time.localtime(info['create']))
            reply = '\n'.join((
                '【 bili-auth 】 验证完成，以下为详细信息。',
                f'请求来源：{platform}, {browser}',
                f'验证代码：{vid}',
                f'创建时间：{dt}',
                '您发送的消息是一条验证请求，可用于登录第三方应用。系统自动回复此消息以告知您验证结果。',
                f'如果您在不知情的情况下意外发送了此次请求，请回复"/revoke {vid}"以撤销此次验证。',
                '如果您对本项目有兴趣，可以发送"/about"进一步了解。'
            ))
        else:
            reply = '【 bili-auth 】 未找到此验证请求, 可能是此验证信息已过期。请尝试重新发起验证。'
        sendText(uid, reply)
    elif action == 'revoke' and arg is not None:
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
    global lastSendTs
    logging.info(f'send->{uid}: {content}')
    sleepTime = lastSendTs + sendCD - time.time()
    if sleepTime > 0:
        time.sleep(sleepTime)
    bu.sendMsg(uid, content)
    lastSendTs = time.time()


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
            logging.warn(e)

        time.sleep(4 + random() * 2)

