import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Account, Transaction, OutboxEvent
from app.db.session import get_session
from app.schemas.transactions import TransactionCreate, TransactionOut

router = APIRouter()


@router.post("/transactions", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
) -> TransactionOut:
    # First: try a fast read for existing (idempotent replay)
    existing = await session.execute(
        select(Transaction).where(
            Transaction.account_id == payload.account_id,
            Transaction.idempotency_key == idempotency_key,
        )
    )
    tx = existing.scalar_one_or_none()
    if tx:
        return tx

    # Ensure account exists (simple approach for v1)
    acc = await session.get(Account, payload.account_id)
    if not acc:
        acc = Account(id=payload.account_id)
        session.add(acc)

    # Create tx + outbox in ONE DB transaction
    tx = Transaction(
        account_id=payload.account_id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        country=payload.country.upper(),
        idempotency_key=idempotency_key,
    )
    session.add(tx)

    event_payload = {
        "event_id": str(uuid.uuid4()),
        "event_type": "TransactionCreated",
        "event_version": 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "transaction_id": None,  # filled after flush
        "account_id": str(payload.account_id),
        "amount": str(payload.amount),
        "currency": payload.currency.upper(),
        "country": payload.country.upper(),
    }

    try:
        async with session.begin():
            await session.flush()  # ensures tx.id exists
            event_payload["transaction_id"] = str(tx.id)
            session.add(OutboxEvent(event_type="TransactionCreated", payload=event_payload))

    except IntegrityError:
        # Race condition: another request created it first.
        await session.rollback()
        again = await session.execute(
            select(Transaction).where(
                Transaction.account_id == payload.account_id,
                Transaction.idempotency_key == idempotency_key,
            )
        )
        tx2 = again.scalar_one_or_none()
        if tx2:
            return tx2
        raise HTTPException(status_code=409, detail="Idempotency conflict")

    return tx
