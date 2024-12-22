import urllib.parse


def dumpCookies(cookieDict):
	return '; '.join([f'{urllib.parse.quote(k)}={urllib.parse.quote(v)}' for k, v in cookieDict.items()])


def loadCookies(cookieStr):
	return {
		urllib.parse.unquote(parsed[0]): urllib.parse.unquote(parsed[1])
		for parsed in [s.split('=') for s in cookieStr.split('; ')]
	}
