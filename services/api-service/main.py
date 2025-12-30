from fastapi import FastAPI

from app.api.routes.transactions import router as transactions_router
from app.api.routes.accounts import router as accounts_router

app = FastAPI(title="Event-Driven Transaction Platform")

app.include_router(transactions_router, prefix="/api", tags=["transactions"])
app.include_router(accounts_router, prefix="/api", tags=["accounts"])
