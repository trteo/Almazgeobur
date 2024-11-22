from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "sales_reports" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sales_date" DATE,
    "preprocessed_sales" TEXT,
    "analysis" TEXT,
    "status" VARCHAR(22) NOT NULL  DEFAULT 'registered',
    "last_log" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "sales_reports"."status" IS 'REGISTERED: registered\nPARSING_STARTED: parsing_started\nPARSED: parsed\nLLM_RESPONSE_GENERATED: llm_response_generated\nFAILED: failed';
CREATE TABLE IF NOT EXISTS "sales" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "product_id" INT NOT NULL,
    "product_name" VARCHAR(255) NOT NULL,
    "quantity" INT NOT NULL,
    "price" DOUBLE PRECISION NOT NULL,
    "category" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "sales_report_id" INT NOT NULL REFERENCES "sales_reports" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
