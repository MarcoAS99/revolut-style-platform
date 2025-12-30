# Local Development

## Prerequisites
- Docker + Docker Compose
- Python 3.11+

## Services (Docker)
- PostgreSQL
- Kafka (single broker)

## How to run (high level)
1. Start dependencies (Postgres + Kafka) with Docker Compose
2. Run `api-service`
3. Run `risk-consumer`
4. Produce a transaction via API and verify:
   - transaction stored in DB
   - `TransactionCreated` published to Kafka
   - risk assessment stored after consumer processes the event

## Common Troubleshooting
- Kafka not ready: wait for broker health to be OK before producing/consuming
- DB connection errors: check env vars and container ports
