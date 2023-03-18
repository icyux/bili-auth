from pymysql.connections import Connection
from pymysql.cursors import Cursor


# convert "?" in SQL statement to "%s", in order to be compatible with pymysql
class WrappedMysqlConn(Connection):
	def __init__(self, **kw):
		super().__init__(**kw)

	def cursor(self):
		return WrappedCursor(self)


class WrappedCursor(Cursor):
	def execute(self, stmt, args=None):
		return super().execute(stmt.replace('?', '%s'), args)
