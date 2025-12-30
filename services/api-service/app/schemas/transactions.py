import uuid
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    account_id: uuid.UUID
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    country: str = Field(min_length=2, max_length=2)


class TransactionOut(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    amount: Decimal
    currency: str
    country: str
    idempotency_key: str
    created_at: datetime

    class Config:
        from_attributes = True
