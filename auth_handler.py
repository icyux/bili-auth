import time
import secrets
import kv_storage

CODE_MAX_AGE = 360
TOKEN_LENGTH = 24

chars = '1234567890qwertyuiopasdfghjklzxcvbnm'

def initPool():
    global pool
    pool = kv_storage.Pool()


def codeGen(length=8):
    while True:
        code = ''.join([secrets.choice(chars) for _ in range(length)])
        if not pool.get(code):
            break
    return code


def createVerify(cid, subject):
    code = codeGen()
    pool.set(code, {
            'createTs': int(time.time()),
            'cid': cid,
            'subject': subject,
            'isAuthed': False,
        },
        expire=CODE_MAX_AGE,
    )

    msg_handler.tasks.put(time.time()+CODE_MAX_AGE)
    return code


def checkVerify(code, *, uid, nickname=None, avatar=None, bio=None):
    if not pool.get(code):
        return False
    detail = pool.get(code)
    detail['isAuthed'] = True
    pool.set(code, {
            **detail,
            'uid': uid,
            'nickname': nickname,
            'avatar': avatar,
            'bio': bio,
        },
        expire=86400
    )
    return True


def getVerifyInfo(code):
    return pool.get(code)

def createToken(code):
    data = pool.get(code)
    if data is None or data.get('tkn'):
        return None 
    token = secrets.token_urlsafe(24)
    data['code'] = code
    data['token'] = token
    pool.set(code, data, expire=86400)
    pool.set(f'tkn.{token}', data, expire=86400)
    return token

def tokenQuery(token):
    return pool.get(f'tkn.{token}')

def revokeVerify(code, uid):
    data = pool.get(code)
    if data is None or data.get('uid') != uid:
        return False

    token = pool.get('token')
    if token:
        pool.delete(f'tkn.{token}')

    return pool.delete(code)
