# Event Contracts

## Principles
- Events are immutable facts about something that happened.
- Events are versioned (`event_version`) to support evolution.
- Producers must not break consumers; add fields in a backward-compatible way.
- Use ISO timestamps (UTC) and UUIDs for identifiers.

## Topic: `transactions.v1`

**Partitioning / Key**
- Producer uses `account_id` as the Kafka message key.
- This preserves ordering for events belonging to the same account (within a partition).

## Compatibility Rules
- Producers may add optional fields (backward compatible).
- Producers must not remove or rename existing fields in the same major version.
- If breaking changes are needed, publish a new major version topic (e.g. `transactions.v2`).

### Event: `TransactionCreated` (v1)

**When emitted**
After a transaction is durably written to the database.

**Schema**
- `event_id` (uuid)
- `event_type` (string) = "TransactionCreated"
- `event_version` (int) = 1
- `occurred_at` (string, ISO-8601 UTC)
- `transaction_id` (uuid)
- `account_id` (uuid)
- `amount` (string/decimal)
- `currency` (string, ISO 4217, e.g. "EUR")
- `country` (string, ISO 3166-1 alpha-2, e.g. "DE")

**Example**
```json
{
  "event_id": "c8a7e1f1-1b84-4fa5-9bbf-8edc2c4a5a3f",
  "event_type": "TransactionCreated",
  "event_version": 1,
  "occurred_at": "2025-01-01T12:00:00Z",
  "transaction_id": "c2f1b7aa-6a9c-4c4a-bd21-028b4f1a5c87",
  "account_id": "b7c6c77c-6f76-4a3f-9a2d-1a00d6f3f2ce",
  "amount": "125.50",
  "currency": "EUR",
  "country": "DE"
}
```