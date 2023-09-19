CREATE TABLE "packages" (
	"id"	INTEGER UNIQUE,
	"package"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id")
);
CREATE TABLE "importNames" (
	"id"	INTEGER UNIQUE,
	"importName"	TEXT NOT NULL,
	"packageName"	INTEGER NOT NULL,
	PRIMARY KEY("id")
);