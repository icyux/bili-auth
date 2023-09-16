#!/bin/python3

import sqlite3

db = sqlite3.connect('./bili-auth.db3')
with open('./schema_sqlite3.sql') as f:
	schema = f.read()
db.executescript(schema)
db.close()
