import bili.msg_handler
from service import app
from datetime import datetime, timedelta


lastErrorTime = None


@app.after_request
def errorHandler(response):
	global lastErrorTime
	if 500 <= response.status_code < 600:
		lastErrorTime = datetime.now()
	return response


@app.context_processor
def injectStatus():
    return {
        'serviceStatus': getCurrentStatus(),
    }


@app.route('/api/status')
def showServiceStatus():
	return getCurrentStatus()


def getCurrentStatus():
	lastMsgAckElapsed = datetime.now() - datetime.fromtimestamp(bili.msg_handler.ackMts / 1_000_000)
	if lastMsgAckElapsed > timedelta(minutes=10):
		return {
			'status': 'degraded',
			'msg': 'failed to fetch messages',
		}

	if lastErrorTime is not None and datetime.now() - lastErrorTime <= timedelta(minutes=10):
		return {
			'status': 'degraded',
			'msg': '5xx errors occurred in last 10 minutes',
		}

	return {
		'status': 'up',
		'msg': 'ok',
	}
