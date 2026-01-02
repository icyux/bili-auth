import bili.utils


def biliApiSelfTest():
    try:
        bili.checkUserAgent()
        bili.utils.getUserInfo(uid=362062895)
        print('bili api self-test ok')
        return True

    except Exception as e:
        print(f'bili api self-test FAILED: {repr(e)}')
        return False
