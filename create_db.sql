CREATE TABLE "packages" (
	"id"	SERIAL PRIMARY KEY,
	"package"	TEXT NOT NULL UNIQUE
);
CREATE TABLE "packages_not_picked" (
	"id"	SERIAL PRIMARY KEY,
	"package"	TEXT NOT NULL UNIQUE
);
CREATE TABLE "import_names" (
	"id"	SERIAL PRIMARY KEY,
	"import_name"	TEXT NOT NULL,
	"package_name"	TEXT NOT NULL,
	"version"	TEXT NOT NULL
);
CREATE TABLE "failed_libraries" (
	"id"	SERIAL PRIMARY KEY,
	"package"	TEXT NOT NULL,
	"version"	TEXT NOT NULL,
	"reason"	TEXT NOT NULL
);
