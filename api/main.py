import uvicorn
from datetime import datetime
import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from schemas import GoldHoldingsOutput, InvestmentCreate, InvestmentOutput, PortfolioOutput, SellInput, SellOutput
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



app = FastAPI(
    title="Money Agent API",
    description="A FastAPI application for Gold Investment project",
    version="1.0.0",
    lifespan=lifespan
)

current_user = {}

@app.get("/")
async def root():
    """Root endpoint that returns a welcome message"""
    return {"message": "Welcome to Money Agent API"}

gold_rate = [99987.72, 99945.50, 99923.80, 99967.25, 99912.40, 99978.90, 99934.15, 99956.70, 99901.30, 99989.45, 99967.88]

@app.get("/gold_rate")
async def get_gold_rate():
    """Route to get the gold rate"""
    price = random.choice(gold_rate)
    return {"price": price,
     "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
     "time": datetime.now().strftime("%H:%M:%S"),
     "timezone": datetime.now().strftime("%Z"),
     "unit": "per 100 gram",
    }

@app.post("/buy_gold", response_model=InvestmentOutput)
async def create_investment(investment: InvestmentCreate, db: Session = Depends(get_db)):
    """Route to create a new investment or add to existing one"""
    try:
        existing_investor = db.query(Investor).filter(Investor.email == investment.email).first()
        
        if existing_investor:
            old_amount = existing_investor.amount
            existing_investor.amount += investment.amount
            db.commit()
            db.refresh(existing_investor)
            
            return {
                "id": existing_investor.id,
                "username": existing_investor.username,
                "email": existing_investor.email,
                "previous_amount": old_amount,
                "new_amount": investment.amount,
                "total_amount": existing_investor.amount,
                "risk_level": existing_investor.risk_level,
                "created_at": existing_investor.created_at
            }

        else:
            new_investment = Investor(**investment.model_dump())
            db.add(new_investment)
            db.commit()
            db.refresh(new_investment)
            
            return {
                "id": new_investment.id,
                "username": new_investment.username,
                "email": new_investment.email,
                "previous_amount": 0,
                "new_amount": investment.amount,
                "total_amount": new_investment.amount,
                "risk_level": new_investment.risk_level,
                "created_at": new_investment.created_at
            }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing investment: {str(e)}")
        

@app.get("/portfolio/{email}", response_model=list[PortfolioOutput])
async def get_investments(email: str, db: Session = Depends(get_db)):
    """Route to get all investments for a specific email"""
    try:
        investments = db.query(Investor).filter(Investor.email == email).all()

        if not investments:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail="No investments found for this email")
        
        return investments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching investments: {str(e)}")

@app.post("/sell_gold", response_model=SellOutput)
async def sell_gold(selling_info: SellInput, db: Session = Depends(get_db)):
    """Route to sell gold"""
    try:
        investor = db.query(Investor).filter(Investor.email == selling_info.email).first()
        
        if not investor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investor not found")

        # calculate how much gold weight the investor has based on their investment amount
        current_gold_rate = random.choice(gold_rate)
        acquired_weight = (investor.amount / current_gold_rate) * 100  # Convert to grams

        if selling_info.weightToSell > acquired_weight:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient gold weight to sell")

        # calculate the sell amount based on current gold rate
        sell_amount = (selling_info.weightToSell / 100) * current_gold_rate
        prev_amount = investor.amount 
        investor.amount -= sell_amount
        
        if investor.amount < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient investment amount")
        
        db.commit()
        db.refresh(investor)

        return {
            "id": investor.id,
            "username": investor.username,
            "email": investor.email,
            "previous_amount": prev_amount,
            "sold_amount": sell_amount,  
            "total_amount": investor.amount,
            "risk_level": investor.risk_level,
            "created_at": investor.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing gold sale: {str(e)}")

@app.get("/gold_holdings/{email}", response_model=GoldHoldingsOutput)
async def get_gold_holdings(email: str, db: Session = Depends(get_db)):
    """Route to get user's gold holdings in grams based on current gold price"""
    try:
        # Get the investor's information
        investor = db.query(Investor).filter(Investor.email == email).first()
        
        if not investor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Investor not found"
            )
        
        current_gold_rate = random.choice(gold_rate)
        gold_grams = (investor.amount / current_gold_rate) * 100
        current_value = investor.amount
        
        return {
            "email": investor.email,
            "username": investor.username,
            "investment_amount": investor.amount,
            "current_gold_rate_per_100g": current_gold_rate,
            "gold_holdings_grams": round(gold_grams, 2),
            "risk_level": investor.risk_level,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculating gold holdings: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
