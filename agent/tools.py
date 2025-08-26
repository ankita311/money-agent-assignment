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
        return response.json()
    else:
        return f"Error: {response.status_code} - {response.text}"

# @tool
# def buy_gold(amount: float) -> str:
#     response = requests.post(f"{API_URL}/buy_gold", json={"amount": amount})
#     if response.status_code == 200:
#         return response.json()
#     else:

tools = [get_gold_rate]

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
            if user_content in ['quit', 'exit', 'bye', 'goodbye']:
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

