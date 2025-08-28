# Money Agent

A gold investment management system with AI-powered agent tools.

## Features

- **Gold Investment API**: Buy, sell, track gold investments and holdings with Conservative, balanced, and aggressive risk levels
- **AI Agent**: LangGraph-based agent with tools for investment operations

## Tech Stack

- **Backend**: FastAPI with SQLAlchemy + PostgreSQL database
- **AI Agent**: LangGraph + LangChain for intelligent investment operations
- **Python**: 3.12+ with modern dependency management

## Project Structure

```
moneyAgent/
├── agent/           # AI agent tools and logic
├── api/            # FastAPI backend server
├── pyproject.toml  # Project dependencies and configuration
├── poetry.lock     # Locked dependency versions
└── uv.lock         # Alternative dependency lock file
```

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- OpenAI API key

## Installation & Setup

### Option 1: Using pip 

1. **Clone the repository:**
```bash
git clone <repository-url>
cd moneyAgent
```

2. **Install the project and dependencies:**
```bash
pip install -e .
```

3. **Set environment variables:**
```bash
# Create a .env file in the project root
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/moneyagent
```

### Option 2: Using Poetry (Recommended)

1. **Install Poetry** (if not already installed):
```bash
pip install poetry
```

2. **Install dependencies:**
```bash
poetry install
```

3. **Activate the virtual environment:**
```bash
poetry env activate
```

### Option 3: Using uv

1. **Install uv** (if not already installed):
```bash
pip install uv
```

2. **Install dependencies:**
```bash
uv sync
```

## Running the Application

### 1. Although the FastAPI BAckend is deployed, if you want to start the FastAPI Backend locally

```bash
# From the project root
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Run the AI Agent Tools

```bash
# From the project root
cd agent
python tools.py
```


## API Endpoints

- `GET /gold_rate` - Get current gold price
- `POST /buy_gold` - Purchase gold
- `GET /portfolio/{email}` - View user portfolio
- `GET /gold_holdings/{email}` - Check gold holdings
- `POST /sell_gold` - Sell gold


### Project Configuration

The project uses `pyproject.toml` for configuration, which provides:
- Dependency management
- Python version requirements
- Project metadata
- Build system configuration

## Troubleshooting

- **Database Connection**: Ensure PostgreSQL is running and the connection string is correct
- **API Keys**: Verify your OpenAI API key is valid and has sufficient credits
- **Python Version**: Ensure you're using Python 3.12 or higher


