# Money Agent

A gold investment management system with AI-powered agent tools.

## Features

- **Gold Investment API**: Buy, sell, track gold investments and holdings, Conservative, balanced, and aggressive risk levels
- **AI Agent**: LangGraph-based agent with tools for investment operations

## Tech Stack

- FastAPI backend
- LangGraph + LangChain for AI agent
- SQLAlchemy + PostgreSQL database
- Python 3.12+

## Quick Start

1. Install dependencies:
```bash
pip install -r api/requirements.txt
```

2. Set environment variables:
```bash
OPENAI_API_KEY=your_key_here
```

3. Run the API:
```bash
cd api
uvicorn main:app --reload
```

4. Use the AI agent tools for investment operations.

```bash
cd agent
python tools.py
```

## API Endpoints

- `GET /gold_rate` - Current gold price
- `POST /buy_gold` - Purchase gold
- `GET /portfolio/{email}` - View portfolio
- `GET /gold_holdings/{email}` - Check holdings
- `POST /sell_gold` - Sell gold
