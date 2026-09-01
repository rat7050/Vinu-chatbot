import os
from dotenv import load_dotenv

from langchain.agents import create_agent # type: ignore
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq

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
agent = create_agent( # type: ignore
    model=llm,
    tools=[search_tool]
)

# -----------------------------
# 5. Run Agent
# -----------------------------
response = agent.invoke({ # type: ignore
    "messages": [
        {
            "role": "user",
            "content": "location of SIRTE college"
        }
    ]
})

# -----------------------------
# 6. Print final response
# -----------------------------
print(response["messages"][-1].content)