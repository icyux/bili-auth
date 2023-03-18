CREATE TABLE `app` (
	`cid`	CHAR(8) NOT NULL,
	`sec`	VARCHAR(30) NOT NULL,
	`name`	VARCHAR(60),
	`url`	VARCHAR(100),
	`desc`	VARCHAR(100),
	`icon`	VARCHAR(100),
	PRIMARY KEY(`cid`)
);

CREATE TABLE `verify` (
	`vid`		CHAR(8) NOT NULL,
	`create`	INTEGER NOT NULL,
	`expire`	INTEGER NOT NULL,
	`ua`		VARCHAR(40),
	`uid`		BIGINT,
	PRIMARY KEY(`vid`)
);

CREATE TABLE `session` (
	`sid`		INTEGER NOT NULL AUTO_INCREMENT,
	`vid`		CHAR(8) NOT NULL,
	`uid`		BIGINT NOT NULL,
	`cid`		CHAR(8) NOT NULL,
	`create`	INTEGER NOT NULL,
	`accCode`	VARCHAR(30),
	`token`		VARCHAR(32),
	PRIMARY KEY(`sid`)
);
