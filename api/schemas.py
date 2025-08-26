from datetime import datetime
from pydantic import BaseModel, EmailStr
from models import RiskLevel

class InvestmentCreate(BaseModel):
    username: str
    email: EmailStr
    amount: float
    risk_level: RiskLevel

class PortfolioOutput(BaseModel):
    id: int
    username: str
    email: str
    amount: float
    risk_level: RiskLevel
    created_at: datetime

class InvestmentOutput(BaseModel):
    id: int
    username: str
    email: str
    previous_amount: float = 0
    new_amount: float
    total_amount: float
    risk_level: RiskLevel
    created_at: datetime

class SellInput(BaseModel):
    email: EmailStr
    weightToSell: float

class SellOutput(BaseModel):
    id: int
    username: str
    email: str
    previous_amount: float
    sold_amount: float
    total_amount: float
    risk_level: RiskLevel
    created_at: datetime

class GoldHoldingsOutput(BaseModel):
    email: str
    username: str
    investment_amount: float
    current_gold_rate_per_100g: float
    gold_holdings_grams: float
    risk_level: RiskLevel
    last_updated: datetime
