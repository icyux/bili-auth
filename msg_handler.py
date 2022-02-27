import time
import re
from random import random
import bili_utils
import queue; tasks = queue.Queue()  # initialization tasks queue
import auth_handler
import requests

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
        if auth_handler.checkVerify(arg.lower(), uid):
            info = auth_handler.getVerifyInfo(arg)
            reply = r'【 bili-auth 】 验证完成。\n请求来源: "{}" 。\n如果此次请求为意外发出, 请回复"/revoke {}"以撤销此次验证。\n此消息是自动回复。您可发送"/about"了解本项目。'
            reply = reply.format(info['subject'], arg)
        else:
            reply = '未找到此验证信息, 可能是此验证信息已过期。请尝试重新验证。'
        sendText(uid, reply)
    elif action == 'revoke':
        if auth_handler.revokeVerify(arg.lower(), uid):
            reply = '撤销成功。验证id: {}。'
            reply = reply.format(arg)
        else:
            reply = '未找到此id对应的与您相关的可撤销验证信息。'
        sendText(uid, reply)
    elif action == 'about':
        sendText(uid, aboutText)


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

