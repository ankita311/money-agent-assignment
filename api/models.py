from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from database import Base

class RiskLevel(enum.Enum):
    """Enum for risk level options"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

class Investor(Base):
    __tablename__ = "investors"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Integer, default=1)  # 1 - active, 0 - inactive
