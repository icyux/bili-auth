import secrets
import time

import model


def initDB():
    global db
    db = model.db


def query(cid):
    cur = db.cursor()
    cur.execute(
        'SELECT * FROM app WHERE cid=?',
        (cid, ),
    )
    try:
        cols = [desc[0] for desc in cur.description]
        row = cur.fetchone()
        if row is None:
            return None

        result = {cols[i]:row[i] for i in range(len(cols))}
        return result

    except IndexError:
        return None
    finally:
        cur.close()


def updateApp(*, uid, name, icon, link, desc, prefix):
    curTs = int(time.time())

    # retry at most 3 times
    for _ in range(3):
        cid = secrets.token_hex(4)
        if query(cid) is None:
            break
    else:
        return None

    csec = secrets.token_urlsafe(18)

    cur = db.cursor()
    cur.execute(
        'REPLACE INTO app \
        (cid, sec, name, ownerUid, createTs, link, prefix, `desc`, icon) \
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (cid, csec, name, uid, curTs, link, prefix, desc, icon),
    )
    affected = cur.rowcount
    cur.close()
    db.commit()
    
    if affected == 1:
        return {
            'cid': cid,
            'csec': csec,
        }
    else:
        return None


def getAuthorizedApps(uid):
    cur = db.cursor()
    cur.execute(
        'SELECT cid, name, link, `desc`, icon FROM app WHERE cid = (SELECT cid FROM session WHERE uid = ?)',
        (uid, ),
    )
    appsInfo = cur.fetchall()
    cur.close()

    result = [
        {
            'cid': info[0],
            'name': info[1],
            'link': info[2],
            'desc': info[3],
            'icon': info[4],
        }
        for info in appsInfo
    ]

    return result


def getCreatedApps(uid):
    cur = db.cursor()
    cur.execute(
        'SELECT cid, name, link, `desc`, icon FROM app WHERE ownerUid = ?',
        (uid, ),
    )
    appsInfo = cur.fetchall()
    cur.close()

    result = [
        {
            'cid': info[0],
            'name': info[1],
            'link': info[2],
            'desc': info[3],
            'icon': info[4],
        }
        for info in appsInfo
    ]

    return result


def revokeAuthorization(*, cid, uid):
    cur = db.cursor()
    cur.execute(
        'DELETE FROM session WHERE uid = ? AND cid = ?',
        (uid, cid),
    )
    affected = cur.rowcount
    cur.close()
    db.commit()

    return affected > 0


def deleteApplication(cid):
    cur = db.cursor()
    cur.execute(
        'DELETE FROM app WHERE cid = ?',
        (cid, ),
    )
    affected = cur.rowcount
    cur.close()
    db.commit()

    return affected > 0
