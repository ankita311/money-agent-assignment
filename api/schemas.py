from datetime import datetime
from pydantic import BaseModel, EmailStr

class InvestmentCreate(BaseModel):
    username: str
    email: EmailStr
    amount: float

class InvestmentOutput(BaseModel):
    id: int
    username: str
    email: str
    previous_amount: float = 0
    new_amount: float
    total_amount: float
    created_at: datetime