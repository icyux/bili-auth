from misc.selenium_utils import ChromeDriver
import bili.utils

def seleniumSelfTest():
    try:
        with ChromeDriver() as d:
            d.get('https://www.bilibili.com')

        print('selenium self-test ok')
        return True

    except Exception as e:
        print(f'selenium self-test FAILED: {repr(e)}')
        return False

def biliApiSelfTest():
    try:
        bili.utils.getUserInfo(uid=362062895)
        print('bili api self-test ok')
        return True

    except Exception as e:
        print(f'bili api self-test FAILED: {repr(e)}')
        return False
