from model import application, session, verify_request


db = None


def initDB(mainDB):
	global db
	db = mainDB
	application.initDB()
	session.initDB()
	verify_request.initDB()
