from datetime import datetime
import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from schemas import InvestmentCreate, InvestmentOutput
from models import Investor
from database import get_db, create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        create_tables()
        print("Database connected successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("API will run without database functionality")
    
    yield
    
    print("Shutting down...")



# FastAPI app instance
app = FastAPI(
    title="Money Agent API",
    description="A FastAPI application for the Money Agent project",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint that returns a welcome message"""
    return {"message": "Welcome to Money Agent API"}

gold_rate = [99987.72, 99945.50, 99923.80, 99967.25, 99912.40, 99978.90, 99934.15, 99956.70, 99901.30, 99989.45, 99967.88]

@app.get("/gold_rate")
async def get_gold_rate():
    """Route to get the gold rate"""
    price = random.choice(gold_rate)
    return {"price": price}

@app.post("/investment", response_model=InvestmentOutput)
async def create_investment(investment: InvestmentCreate, db: Session = Depends(get_db)):
    """Route to create a new investment or add to existing one"""
    try:
        # Check if user already exists
        existing_investor = db.query(Investor).filter(Investor.email == investment.email).first()
        
        if existing_investor:
            # User exists, add new amount to existing amount
            old_amount = existing_investor.amount
            existing_investor.amount += investment.amount
            db.commit()
            db.refresh(existing_investor)
            
            return {
                "message": "Investment updated successfully",
                "id": existing_investor.id,
                "username": existing_investor.username,
                "previous_amount": old_amount,
                "new_amount": investment.amount,
                "total_amount": existing_investor.amount
            }
        else:
            # New user, create new investment
            new_investment = Investor(**investment.model_dump())
            db.add(new_investment)
            db.commit()
            db.refresh(new_investment)
            
            return new_investment
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing investment: {str(e)}")

@app.get("/investments", response_model=list[InvestmentOutput])
async def get_investments(db: Session = Depends(get_db)):
    """Route to get all investments"""
    try:
        investments = db.query(Investor).all()
        return investments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching investments: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
