import os
from dotenv import load_dotenv
from langgraph.checkpoint import memory # type: ignore
load_dotenv()


from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain.agents import create_agent # type: ignore
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    streaming=True,
    temperature=0
)


search_tool = TavilySearch(
    max_results=5,
    topic="general",
    api_key=os.getenv("TAVILY_API_KEY")
)

if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()
    st.session_state.history = []


agent = create_agent( # type: ignore
    model=llm, 
    tools=[search_tool],
    checkpointer=st.session_state.memory,
    system_prompt="you are a helpful ai agent and you can search on web as well"
)

st.subheader("Ask any question to the agent")

for message in st.session_state.history: # type: ignore
    st.chat_message(message["role"]).markdown(message["content"]) # type: ignore

query = st.chat_input("Ask anything ?")

if query:
    st.chat_message("user").markdown(query)
    st.session_state.history.append({"role": "user", "content": query}) # type: ignore

    response = agent.stream(  # type: ignore
            {"messages": [{"role": "user", "content": query}]},
            config={"configurable": {"thread_id": "1"}},
            stream_mode="messages"

    )

    
    ai_container = st.chat_message("assistant")
    with ai_container:
        space=st.empty()
        answer = ""

        for chunk in response:
            answer = answer + chunk[0].content # type: ignore
            space.write(answer)

    st.session_state.history.append({"role": "assistant", "content": answer}) # type: ignore


