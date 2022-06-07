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
