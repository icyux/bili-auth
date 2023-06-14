CREATE TABLE "app" (
	"cid"		TEXT NOT NULL UNIQUE,
	"sec"		TEXT NOT NULL,
	"name"		TEXT,
	"createTs"	BIGINT UNSIGNED,
	"ownerUid"	BIGINT UNSIGNED,
	"url"		TEXT,
	"desc"		TEXT,
	"icon"		TEXT,
	PRIMARY KEY("cid")
);

CREATE TABLE "verify" (
	"vid"		TEXT NOT NULL UNIQUE,
	"create"	INTEGER NOT NULL,
	"expire"	INTEGER NOT NULL,
	"ua"		TEXT,
	"uid"		INTEGER,
	PRIMARY KEY("vid")
);

CREATE TABLE "session" (
	"sid"		INTEGER NOT NULL UNIQUE,
	"vid"		TEXT NOT NULL,
	"uid"		INTEGER NOT NULL,
	"cid"		INTEGER NOT NULL,
	"create"	INTEGER NOT NULL,
	"accCode"	TEXT,
	"token"		TEXT,
	PRIMARY KEY("sid" AUTOINCREMENT)
);

CREATE TABLE "users" (
	"uid"		INTEGER NOT NULL UNIQUE,
	"name"		TEXT,
	"bio"		TEXT,
	"avatar"	TEXT,
	"updateTs"	INTEGER NOT NULL,
	PRIMARY KEY("uid")
);
