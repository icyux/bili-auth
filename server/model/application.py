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


def createApp(*, uid, name, icon=None, link, desc, prefix):
    curTs = int(time.time())
    cid = secrets.token_hex(4)
    csec = secrets.token_urlsafe(18)

    cur = db.cursor()
    cur.execute(
        'INSERT INTO app \
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


def updateApp(cid, *, name, link, desc, prefix, icon=None):
    cur = db.cursor()
    if icon is None:
        cur.execute(
            'UPDATE app \
            SET name = ?, link = ?, prefix = ?, `desc` = ? \
            WHERE cid = ?',
            (name, link, prefix, desc, cid),
        )
    else:
        cur.execute(
           'UPDATE app \
           SET name = ?, link = ?, prefix = ?, `desc` = ?, icon = ? \
           WHERE cid = ?',
           (name, link, prefix, desc, icon, cid),
        )
    affected = cur.rowcount
    cur.close()
    db.commit()
    
    return affected == 1


def updateAppIcon(cid, icon):
    cur = db.cursor()
    cur.execute(
        'UPDATE app \
        SET icon = ? \
        WHERE cid = ?',
        (icon, cid),
    )
    affected = cur.rowcount
    cur.close()
    db.commit()

    return affected == 1


def removeAppIcon(cid):
    cur = db.cursor()
    cur.execute(
        'UPDATE app \
        SET icon = NULL \
        WHERE cid = ?',
        (cid, ),
    )
    affected = cur.rowcount
    cur.close()
    db.commit()

    return affected == 1


def getAuthorizedApps(uid):
    cur = db.cursor()
    cur.execute(
        'SELECT cid, name, link, `desc` FROM app WHERE cid = ANY(SELECT cid FROM session WHERE uid = ?)',
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
            'icon': f'/oauth/application/{info[0]}/icon'
        }
        for info in appsInfo
    ]

    return result


def getCreatedApps(uid):
    cur = db.cursor()
    cur.execute(
        'SELECT cid, name, link, `desc` FROM app WHERE ownerUid = ?',
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
            'icon': f'/oauth/application/{info[0]}/icon'
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
