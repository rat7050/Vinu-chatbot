from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import load_prompt
import streamlit as st


import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = st.secrets["GROQ_API_KEY"]

model= ChatGroq(temperature=0, model_name="openai/gpt-oss-20b")


st.title("Vinu Chatbot")
st.markdown("<h5 style='text-align; color: Black;'>Ask anything to Vinu</h3>", unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []

for messages in st.session_state.messages:
    role = messages["role"]
    content = messages["content"]
    st.chat_message(role).markdown(content)


query = st.chat_input("Ask your question here: ")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    st.chat_message("user").write(query)
    response = model.invoke(query)
    st.chat_message("assistant").write(response.content.strip())
    st.session_state.messages.append({"role": "assistant", "content": response.content.strip()})