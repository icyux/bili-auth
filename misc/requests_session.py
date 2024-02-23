import misc
import requests


session = requests.Session()
noAuthSession = requests.Session()
noAuthSession.headers = {
	'User-Agent': misc.config['bili']['user_agent'],
}
