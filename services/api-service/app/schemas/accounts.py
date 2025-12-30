import uuid
from decimal import Decimal

from pydantic import BaseModel


class BalanceOut(BaseModel):
    account_id: uuid.UUID
    balance: Decimal
