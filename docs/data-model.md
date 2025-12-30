# Data Model (Draft)

## Database: PostgreSQL

## Tables

### `accounts`
- `id` UUID PRIMARY KEY
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()

### `transactions`
- `id` UUID PRIMARY KEY
- `account_id` UUID NOT NULL REFERENCES accounts(id)
- `amount` NUMERIC(18, 2) NOT NULL
- `currency` CHAR(3) NOT NULL
- `country` CHAR(2) NOT NULL
- `idempotency_key` TEXT NOT NULL
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()

Constraints:
- UNIQUE (`account_id`, `idempotency_key`)

Indexes:
- (`account_id`, `created_at`)
- (`created_at`)

### `outbox_events`
- `id` UUID PRIMARY KEY
- `event_type` TEXT NOT NULL
- `payload` JSONB NOT NULL
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `published_at` TIMESTAMP WITH TIME ZONE NULL

Indexes:
- (`published_at`) with focus on NULL values (implementation detail)

### `risk_assessments`
- `id` UUID PRIMARY KEY
- `transaction_id` UUID NOT NULL REFERENCES transactions(id)
- `risk_score` INTEGER NOT NULL
- `reasons` JSONB NOT NULL
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()

Constraints:
- UNIQUE (`transaction_id`)

## Notes
- Idempotency is enforced at the database level for correctness.
- Consumer idempotency is enforced via unique constraints on transaction_id.
- Outbox supports reliable publishing even if broker is temporarily unavailable.
- 
## Access Pattern (SQLAlchemy Async)
- API and workers use SQLAlchemy 2.x async engine with `asyncpg`.
- All DB operations are executed within explicit async sessions/transactions.
- Outbox insertion and transaction insertion occur in the same DB transaction to ensure consistency.
