CREATE TABLE "app" (
	"cid"	TEXT NOT NULL UNIQUE,
	"sec"	TEXT NOT NULL,
	"name"	TEXT,
	"url"	TEXT,
	"desc"	TEXT,
	"icon"	TEXT,
	PRIMARY KEY("cid")
);

CREATE TABLE "verify" (
	"vid"		INTEGER NOT NULL UNIQUE,
	"clgCode"	TEXT NOT NULL UNIQUE,
	"create"	INTEGER NOT NULL,
	"expire"	INTEGER NOT NULL,
	"uid"		INTEGER,
	PRIMARY KEY("vid")
);

CREATE TABLE "session" (
	"sid"		INTEGER NOT NULL UNIQUE,
	"vid"		INTEGER NOT NULL,
	"uid"		INTEGER NOT NULL,
	"cid"		INTEGER NOT NULL,
	"create"	INTEGER NOT NULL,
	"accCode"	TEXT,
	"token"		TEXT,
	PRIMARY KEY("sid" AUTOINCREMENT)
);
