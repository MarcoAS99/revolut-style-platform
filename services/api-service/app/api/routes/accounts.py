import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Transaction
from app.db.session import get_session
from app.schemas.accounts import BalanceOut

router = APIRouter()


@router.get("/accounts/{account_id}/balance", response_model=BalanceOut)
async def get_balance(
    account_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> BalanceOut:
    result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.account_id == account_id)
    )
    balance = result.scalar_one()
    return BalanceOut(account_id=account_id, balance=Decimal(balance))
