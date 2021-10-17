-- upgrade --
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "notemodel" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sign" VARCHAR(255) NOT NULL UNIQUE,
    "name" VARCHAR(200) NOT NULL,
    "content_type" VARCHAR(200) NOT NULL,
    "max_number_visits" INT,
    "current_number_visits" INT NOT NULL  DEFAULT 0,
    "is_encrypted" BOOL NOT NULL  DEFAULT False,
    "encrypt_password_hash" TEXT,
    "encrypt_metadata" BYTEA,
    "text" BYTEA NOT NULL
);
COMMENT ON COLUMN "notemodel"."content_type" IS 'text: text';
COMMENT ON TABLE "notemodel" IS 'Model for notes purpose.';
