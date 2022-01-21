CREATE TABLE "app" (
	"cid"	TEXT NOT NULL UNIQUE,
	"name"	TEXT,
	"url"	TEXT,
	"sec"	TEXT NOT NULL,
	PRIMARY KEY("cid")
)
