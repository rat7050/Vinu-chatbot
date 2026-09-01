import os
from dotenv import load_dotenv

from langchain.agents import create_agent # type: ignore
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver

# -----------------------------
# 1. Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# 2. Create Groq LLM
# -----------------------------
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

memory = MemorySaver()

# -----------------------------
# 3. Create Tavily Search Tool
# -----------------------------
search_tool = TavilySearch(
    max_results=5,
    topic="general",
    api_key=os.getenv("TAVILY_API_KEY")
)

# -----------------------------
# 4. Create Agent
# -----------------------------
agent = create_agent( # pyright: ignore[reportUnknownVariableType]
    model=llm,
    tools=[search_tool],
    checkpointer=memory
    
)

# -----------------------------
# 5. coutinues searching until user stops
# -----------------------------
while True:
    query = input("user: ")
    if query.lower() == 'exit':
        print("Goodbye!")
        break
    response = agent.invoke( # pyright: ignore[reportUnknownMemberType]
        {"messages": [{"role": "user", "content": query}]},
        {"configurable": {"thread_id": "1"}}) # type: ignore
    
    print("Agent Response:", response["messages"][-1].content)
