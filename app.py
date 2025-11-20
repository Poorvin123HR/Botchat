import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os

# Set API key
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Set up Streamlit page
st.set_page_config(page_title="Gemini Chatbot", layout="centered")

# Inject AgriBot theme CSS
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #e0f7fa, #f1f8e9);
        font-family: 'Verdana', sans-serif;
    }
    .stApp {
        background: linear-gradient(to right, #e0f7fa, #f1f8e9);
    }
    h1, h2, h3 {
        color: #2e7d32;
        text-align: center;
        text-shadow: 2px 2px 4px #a5d6a7;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stChatMessage[data-testid="stChatMessage-user"] {
        background-color: #c8e6c9;
        color: #1b5e20;
    }
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background-color: #ffffff;
        border: 2px solid #2e7d32;
        color: #33691e;
    }
    .stTextInput, .stChatInput {
        border-radius: 10px;
        border: 1px solid #a5d6a7;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 AGRICULTURE CHATBOT 🌱")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content="You are a helpful assistant.")
    ]

# Display past messages
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").markdown(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").markdown(msg.content)

# User input
user_input = st.chat_input("Say something...")
if user_input:
    # Append user message
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    st.chat_message("user").markdown(user_input)

    # Get response from Gemini
    result = llm.invoke(st.session_state.chat_history)
    response = result.content

    # Append AI response
    st.session_state.chat_history.append(AIMessage(content=response))
    st.chat_message("assistant").markdown(response)
