# Core Sequence — Create Transaction

## Actors
- Client
- API Service (`api-service`)
- PostgreSQL
- Broker (Kafka/Redpanda)
- Risk Consumer (`risk-consumer`)

## Sequence (Happy Path)
1. Client sends `POST /transactions` with headers:
   - `Idempotency-Key: <uuid or unique string>`
2. API validates request payload (Pydantic)
3. API begins DB transaction
4. API inserts transaction row into `transactions`
5. API inserts event row into `outbox_events` (same DB transaction)
6. API commits DB transaction
7. Background publisher reads `outbox_events` where `published_at IS NULL`
8. Publisher emits `TransactionCreated.v1` to Kafka topic `transactions.v1`
   - Message key: `account_id` (keeps related events ordered per account)
9. Publisher marks `outbox_events.published_at = now()`
10. Risk consumer receives event
11. Risk consumer calculates `risk_score` + `reasons`
12. Risk consumer inserts into `risk_assessments` (unique on `transaction_id`)
13. Consumer commits offset (or equivalent acknowledgement)

## Idempotency Cases
### Client retries the same request
- API attempts insert with same `(account_id, idempotency_key)`
- DB unique constraint prevents duplicate
- API returns the previously created transaction

### Broker redelivers the same event
- Consumer insert into `risk_assessments` is protected by unique constraint on `transaction_id`
- Consumer treats duplicate as a no-op and continues safely

## Ordering Note
Ordering is guaranteed per Kafka partition. By using `account_id` as the message key,
events for the same account are routed to the same partition, preserving per-account order.

## Failure Cases (Handled later)
- DB commit succeeds but broker publish fails -> resolved by Outbox retry loop
- Consumer processing fails -> retry/backoff, then DLQ after max attempts
