import time
import re
from random import random
import bili_utils
import queue; tasks = queue.Queue()  # initialization tasks queue
import auth_handler
import requests

sendCD = 1

patt = re.compile(r'^\s*?"?(\S+?)\((\S+?)\)"?\s*?$', re.IGNORECASE)
ackMts = int(time.time() * 1000)
lastSendTs = 0


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
            arg = result.group(2).lower()
            if action in ('auth', 'revoke'):
                cmdHandler(uid, action, arg)
        ackMts = max(ts * 1000, ackMts)


def cmdHandler(uid, action, arg):
    if action == 'auth':
        if auth_handler.checkVerify(arg, uid):
            info = auth_handler.getVerifyInfo(arg)
            reply = r'【 bili-auth 】 验证完成。\n请求来源: "{}" 。\n如果此次请求为意外发出, 请回复"revoke({})"以撤销此次验证。\n此消息是自动回复。'
            reply = reply.format(info['subject'], arg)
        else:
            reply = '未找到此验证信息, 可能是此验证信息已过期。请尝试重新验证。'
        sendText(uid, reply)
    if action == 'revoke':
        if auth_handler.revokeVerify(arg, uid):
            reply = '撤销成功。验证id: {}。'
            reply = reply.format(arg)
        else:
            reply = '未找到此id对应的与您相关的可撤销验证信息。'
        sendText(uid, reply)


def sendText(uid, content):
    print(f'[send -> {uid}]', content)
    sleepTime = lastSendTs + sendCD - time.time()
    if sleepTime > 0:
        time.sleep(sleepTime)
    bili_utils.sendMsg(uid, content)


def mainLoop():
    maxExpire = 0
    while True:

        while maxExpire < time.time():
            curExpire = tasks.get()
            if curExpire > maxExpire:
                maxExpire = curExpire

        try:
            checkMsg()
        except Exception as e:
            print(e)

        time.sleep(4 + random() * 2)

