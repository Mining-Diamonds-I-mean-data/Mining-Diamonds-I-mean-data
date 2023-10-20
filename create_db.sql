CREATE TABLE "packages" (
	"id"	SERIAL PRIMARY KEY,
	"package"	TEXT NOT NULL UNIQUE
);
CREATE TABLE "import_names" (
	"id"	SERIAL PRIMARY KEY,
	"importName"	TEXT NOT NULL,
	"packageName"	TEXT NOT NULL,
	"version"	TEXT NOT NULL
);
CREATE TABLE "failed_libraries" (
	"id"	SERIAL PRIMARY KEY,
	"package"	TEXT NOT NULL,
	"version"	TEXT NOT NULL,
	"reason"	TEXT NOT NULL
);
