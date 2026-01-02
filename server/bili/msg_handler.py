import queue; tasks = queue.Queue()  # initialization tasks queue

from random import random
import logging
import re
import requests
import time

from bili import utils as bu
from misc import config
from model import verify_request as vr

sendCD = 1
maxErrCnt = 3

commandPattern = re.compile(r'^/\s*(\S+)(?:\s+(\S.*)$|$)', re.IGNORECASE)
claimPattern = re.compile(r'^确认授权\s*(\S+)$')
ackMts = int(time.time() * 1000000)
lastSendTs = 0

aboutText = '''【 bili-auth 】 是一个第三方实现的 Bili OAuth API，基于私信验证用户对帐号的所有权。
它可以让用户使用哔哩哔哩帐号，完成第四方应用鉴权。
提供通用的 OAuth 2.0 API，应用可快速接入。
代码开源，开发者可本地部署。
您可以在 GitHub 查看 icyux/bili-auth 以了解更多。
'''

def checkMsg():
    global ackMts
    msgList = bu.getNewMsg(ackMts)
    for m in msgList:
        uid = m['uid']
        content = m['content'].strip()
        ts = m['ts']
        logging.info(f'recv<-{uid}: {content}')

        matchResult = claimPattern.search(content)
        if matchResult is not None:
            vid = matchResult.group(1).lower()
            verifyClaimHandler(uid, vid)

        matchResult = commandPattern.search(content)
        if matchResult:
            action = matchResult.group(1).lower()
            arg = matchResult.group(2)
            cmdHandler(uid, action, arg)


def verifyClaimHandler(uid, vid):
    isRespRequired = config['bili']['verifyResultResp']
    isSucc = vr.checkVerify(vid=vid, uid=uid)
    if isSucc and isRespRequired:
        info = vr.getVerifyInfo(vid)
        assert info is not None

        ua = info.get('ua', '未知')
        dt = time.strftime('%Y-%m-%d %H:%M:%S (UTC%z)', time.localtime(info['create']))
        reply = '\n'.join((
            '【 bili-auth 】 验证完成，以下为详细信息。',
            f'请求来源：{ua}',
            f'验证代码：{vid}',
            f'创建时间：{dt}',
            '您发送的消息是一条验证请求，可用于登录第三方应用。系统自动回复此消息以告知您验证结果。',
            f'如果您在不知情的情况下意外发送了此次请求，请回复"/revoke {vid}"以撤销此次验证。',
            '如果您对本项目有兴趣，可以发送"/about"进一步了解。'
        ))

    else:
        reply = '【 bili-auth 】 未找到此验证请求, 可能是此验证信息已过期。请尝试重新发起验证。'

    sendText(uid, reply)


def cmdHandler(uid, action, arg):
    if action == 'revoke' and arg is not None:
        vid = arg.lower()
        if vr.revokeVerify(vid=vid, uid=uid) is not None:
            reply = '【 bili-auth 】 撤销成功。\n验证代码: {}\n对应的应用授权已立即被全部撤销，但生效时间取决于第四方应用的实现。'
            reply = reply.format(arg)
        else:
            reply = '【 bili-auth 】 未找到此验证代码对应的信息。'
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
    expire = int(time.time()) + 1
    tasks.put(expire)


def mainLoop():
    maxExpire = 0
    curErrCnt = 0

    while True:

        while maxExpire < time.time():
            curExpire = tasks.get()
            if curExpire > maxExpire:
                maxExpire = curExpire

        try:
            checkMsg()
            curErrCnt = 0
        except requests.exceptions.RequestException as e:
            curErrCnt += 1
            if curErrCnt >= maxErrCnt:
                logging.warn(f'max requesting error rate reached: {repr(e)}')

        time.sleep(4 + random() * 2)

