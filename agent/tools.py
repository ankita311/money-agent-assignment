from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage, trim_messages
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
import requests

API_URL = "http://localhost:8000"
history = ""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool 
def get_gold_rate() -> str:
    """Get gold rate from the API"""
    response = requests.get(f"{API_URL}/gold_rate")
    if response.status_code == 200:
        data = response.json()
        return f"The current gold rate is ₹{data['price']} per 100 grams. This rate was recorded on date {data['date']} at time {data['time']} {data['timezone']}."
    else:   
        return f"Error: {response.status_code} - {response.text}"

@tool
def buy_gold(username: str, email: str, amount: float, risk_level: str) -> str:
    """Buy gold from the API. Requires amount, username, email, and risk_level.
    Amount is the rupees to invest in gold and risk_level must be one of the following: conservative, moderate, aggressive."""

    valid_risk_levels = ["conservative", "moderate", "aggressive"]
    if risk_level.lower() not in valid_risk_levels:
        return "Invalid risk level. Please choose from: conservative, moderate, aggressive."
    
    if amount <= 0:
        return "Amount must be greater than 0."
    
    payload = {
        "username": username,
        "email": email,
        "amount": amount,
        "risk_level": risk_level.lower()
    }

    response = requests.post(f"{API_URL}/buy_gold", json=payload)
    if response.status_code == 200:
        data= response.json()
        if "previous_amount" in data and data["previous_amount"] > 0:
            return f"Investment updated successfully! Your previous investment was Rs. {data['previous_amount']}, and you've added Rs. {data['new_amount']}. Your total investment is now Rs. {data['total_amount']}. Your risk level is {data['risk_level']}."
        else:
            return f"New investment created successfully! You've invested Rs. {data['new_amount']} in gold with a {data['risk_level']} risk level. Your total investment is Rs.{data['total_amount']}."
    else:
        return f"Error: {response.status_code} - {response.text}"

@tool
def get_gold_holdings(email: str) -> str:
    """Get gold holdings from the API. Requires email."""
    response = requests.get(f"{API_URL}/gold_holdings/{email}")
    if response.status_code == 200:
        data = response.json()
        return f"Your gold holdings are {data['gold_holdings_grams']} grams. Your current gold rate is Rs. {data['current_gold_rate_per_100g']} per 100 grams. Your total investment is Rs. {data['total_amount']}. Your risk level is {data['risk_level']}."
    
    else:
        return f"Error: {response.status_code} - {response.text}"

@tool
def sell_gold(email: str, weight_to_sell: float) -> str:
    """Sell gold from the API. Requires email and weight_to_sell."""
    if weight_to_sell <= 0:
        return "Weight to sell must be greater than 0."
    
    payload = {
        "email": email,
        "weightToSell": weight_to_sell
    }                               

    response = requests.post(f"{API_URL}/sell_gold", json=payload)
    if response.status_code == 200:
        data = response.json()
        return f"Gold sale completed successfully! You sold {weight_to_sell} grams of gold. Your previous investment amount was Rs. {data['previous_amount']}, and you received Rs. {data['sold_amount']} from the sale. Your remaining investment is now Rs. {data['total_amount']}."
    else:
        return f"Error: {response.status_code} - {response.text}"

@tool
def get_portfolio(email: str) -> str:
    """Get portfolio from the API. Requires email."""
    response = requests.get(f"{API_URL}/portfolio/{email}")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            portfolio_summary = f"Your investment portfolio:\n"
            total_investment = 0
            
            for investment in data:
                portfolio_summary += f"• Investment ID: {investment['id']}\n"
                portfolio_summary += f"  Amount: Rs. {investment['amount']}\n"
                portfolio_summary += f"  Risk Level: {investment['risk_level']}\n"
                portfolio_summary += f"  Created: {investment['created_at']}\n\n"
                total_investment += investment['amount']
            
            portfolio_summary += f"Total Investment: Rs. {total_investment}"
            return portfolio_summary
        else:
            return "No investments found in your portfolio."
    else:
        return f"Error: {response.status_code} - {response.text}"


tools = [get_gold_rate, buy_gold, get_gold_holdings, sell_gold, get_portfolio]

model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

def our_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="""You are a helpful financial advisor. 
    You are given a list of tools to use to help the user. 
    You are given a list of tools to use to help the user. 
    You are to use the tools to help the user.
    
    - if a user asks for gold rate, use the get_gold_rate tool""")

    if not state['messages']:
        user_input = "I'm ready to help you with your financial needs. What would you like to know?"
        user_message = HumanMessage(content=user_input)
        
    else:
        # Get user input
        user_input = input("\nWhat would you like to know or would you like to invest in some digital gold? ")
        print(f"\nUSER: {user_input}")
        user_message = HumanMessage(content=user_input)

        
    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = model.invoke(all_messages)
    
    print(f"\nAI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")
    
    return {"messages": state['messages'] + [user_message, response]}

def should_continue(state: AgentState) -> str:
    """Determines if the conversation should continue or end"""

    messages = state['messages']
    if not messages:
        return "continue"
    
    if len(messages) >= 2:
        user_message = messages[-2]  # get user message before AI response
        if isinstance(user_message, HumanMessage):
            user_content = user_message.content.lower()
            if user_content in ['quit', 'exit', 'bye', 'goodbye','leave']:
                return "end"

    return "continue"

def print_messages(messages):
    """Function to print the messages in a more readable format"""
    if not messages:
        return 

    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n TOOL RESULT: {message.content}")


graph = StateGraph(AgentState)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")
graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "agent",
        "end": END
    }
)

app = graph.compile()

def run_money_agent():
    print("\n =====Simplify Money Agent=====")
    state = {"messages": []}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    print("\n=====END=====")

if __name__ == "__main__":
    run_money_agent()

