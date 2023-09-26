CREATE TABLE "packages" (
	"id"	INTEGER UNIQUE,
	"package"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id")
);
CREATE TABLE "importNames" (
	"id"	INTEGER UNIQUE,
	"importName"	TEXT NOT NULL,
	"packageName"	TEXT NOT NULL,
	"version"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE "crying_junk" (
	"id"	INTEGER UNIQUE,
	"package"	TEXT NOT NULL,
	"version"	TEXT NOT NULL,
	"reason"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
