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
    cur.close()
    db.commit()
