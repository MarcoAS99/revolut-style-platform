# Event-Driven Transaction & Risk Platform — Architecture

## Purpose
Build a production-style, event-driven backend platform that:
- accepts financial transactions via an HTTP API
- stores them in a ledger-like database model with idempotency guarantees
- emits immutable transaction events
- consumes events to compute risk assessments
- runs periodic analytics pipelines
- is deployable with Docker/Kubernetes, automated via Ansible, and observable with metrics/alerts

## Goals (What this project demonstrates)
- Python backend engineering (async APIs, validation, error handling)
- Distributed systems fundamentals (event-driven design, idempotency, retries)
- Data engineering basics (ETL-style jobs, analytics modeling)
- Production readiness (Docker, Kubernetes, monitoring/alerting)
- Delivery tooling (TeamCity pipeline)
- Cloud exposure (GCP: GKE + Cloud SQL, optional Pub/Sub)

## Technology Choices (v1)
- Language: Python 3.11+
- API: FastAPI (async)
- Database: PostgreSQL
- ORM: SQLAlchemy 2.x (async) + asyncpg driver
- Migrations: Alembic
- Broker: Kafka (Docker container for local dev)
- Observability: Prometheus + Grafana + OpenTelemetry
- Local runtime: Docker Compose
- Deployment: Kubernetes (later: GKE)
- Automation: Ansible
- CI/CD: TeamCity

## Non-goals
- User authentication/authorization (can be added later)
- Full double-entry accounting (we model a simplified ledger)
- Complex ML risk models (risk scoring is rule-based for clarity)

## System Components

### 1) API Service (`api-service`)
Responsibilities:
- REST endpoints:
  - `POST /transactions` (idempotent)
  - `GET /accounts/{id}/balance`
  - `GET /transactions` (filtering by account + time range)
- validates input using Pydantic
- writes ledger records to PostgreSQL
- publishes a `TransactionCreated` event (reliably; Outbox pattern)

Key properties:
- idempotency: repeated requests with same key do not create duplicates
- correctness: DB commit and event publication are consistent

### 2) Event Broker (Kafka)
Responsibilities:
- stores events in topic(s) (starting with `transactions.v1`)
- enables horizontal scaling for consumers via consumer groups
- decouples producers and consumers

Local development:
- Kafka runs in Docker via Docker Compose (with a single broker for simplicity)


### 3) Risk Consumer (`risk-consumer`)
Responsibilities:
- consumes `TransactionCreated` events
- computes `risk_score` and `reasons` (rule-based)
- writes results to `risk_assessments`
- optionally publishes `RiskAssessed`

Key properties:
- at-least-once processing
- consumer idempotency (safe on re-delivery)
- retry and dead-letter handling

### 4) Pipeline Worker (`pipeline-worker`)
Responsibilities:
- scheduled job that aggregates data for analytics
- produces a denormalized fact table (or exports Parquet/CSV)
- runs as:
  - local scheduled job (dev)
  - Kubernetes CronJob (prod)

### 5) Observability
- Metrics: Prometheus
- Dashboards + Alerts: Grafana
- Tracing: OpenTelemetry (API -> broker -> consumer)

### 6) Platform & Delivery
- Docker for local build/run
- Kubernetes for deployment (local k3d/kind, and GKE for cloud exposure)
- Ansible for provisioning/bootstrap
- TeamCity for CI/CD (lint, typecheck, tests, docker build, deploy)

## High-level Data Flow
1. Client sends `POST /transactions` with an `Idempotency-Key`
2. API validates and stores the transaction in PostgreSQL
3. API emits `TransactionCreated.v1` event (via Outbox)
4. Risk consumer processes event and stores risk assessment
5. Pipeline worker periodically aggregates transactions for analytics
6. Observability stack collects metrics/traces and triggers alerts if unhealthy

## Reliability & Consistency Strategy
- Idempotency on the API using `(account_id, idempotency_key)` unique constraint
- At-least-once event processing; consumers deduplicate via unique constraints
- Outbox pattern for reliable event publication (publish after DB commit)

## Security Considerations (Later)
- Basic rate limiting and request validation
- Secrets managed via Kubernetes Secrets / GCP Secret Manager (optional)

## Scalability Considerations
- API scales horizontally behind a service/load balancer
- Kafka topic partitioning enables consumer scaling
- Consumers scale via consumer groups

## Environments
- Local: Docker Compose
- Kubernetes: k3d/kind (optional) and GKE (GCP)

## Local Development Topology (Docker Compose)
Local environment runs:
- PostgreSQL
- Kafka broker (single node)
- optional Kafka UI (for inspecting topics)
- api-service
- risk-consumer
- pipeline-worker (manual run at first; later scheduled)
- Prometheus + Grafana (later milestone)

This provides production-like integration while keeping local setup simple.
