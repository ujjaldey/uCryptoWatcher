CREATE TABLE "alerts" (
	"id"	INTEGER NOT NULL UNIQUE,
	"chat_id"	INTEGER NOT NULL,
	"crypto"	TEXT NOT NULL,
	"condition"	TEXT NOT NULL,
	"alert_price"	NUMERIC NOT NULL,
	"base_ccy"	TEXT NOT NULL,
	"max_alert_count"	INTEGER,
	"alert_count"	INTEGER DEFAULT 0,
	"active"	TEXT,
	"last_alert_at"	TEXT,
	"created_at"	TEXT,
	"updated_at"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);