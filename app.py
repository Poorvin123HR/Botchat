import streamlit as st
import json, os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Set API key
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Set up Streamlit page
st.set_page_config(page_title="Gemini Chatbot", layout="centered")
st.title("🤖 AGRICULTURE CHATBOT 🌱")

# --- Login with phone number ---
phone = st.text_input("📱 Enter your phone number to start:", max_chars=10)
if not phone:
    st.stop()  # wait until phone number is entered

# --- Load chat history from file if exists ---
filename = f"chat_{phone}.json"
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

if phone not in st.session_state.chat_histories:
    if os.path.exists(filename):
        # Reload saved chat
        with open(filename, "r") as f:
            saved = json.load(f)
        # Convert back to LangChain message objects
        history = []
        for i, content in enumerate(saved):
            if i == 0 and content.startswith("You are a helpful assistant"):
                history.append(SystemMessage(content=content))
            elif i % 2 == 0:  # crude assumption: even index = user
                history.append(HumanMessage(content=content))
            else:             # odd index = assistant
                history.append(AIMessage(content=content))
        st.session_state.chat_histories[phone] = history
    else:
        # Start fresh
        st.session_state.chat_histories[phone] = [SystemMessage(content="You are a helpful assistant.")]

# --- Display past messages ---
for msg in st.session_state.chat_histories[phone]:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").markdown(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").markdown(msg.content)

# --- User input ---
user_input = st.chat_input("Say something...")
if user_input:
    # Append user message
    st.session_state.chat_histories[phone].append(HumanMessage(content=user_input))
    st.chat_message("user").markdown(user_input)

    # Get response from Gemini
    result = llm.invoke(st.session_state.chat_histories[phone])
    response = result.content

    # Append AI response
    st.session_state.chat_histories[phone].append(AIMessage(content=response))
    st.chat_message("assistant").markdown(response)

    # --- Save updated chat to file ---
    with open(filename, "w") as f:
        json.dump([msg.content for msg in st.session_state.chat_histories[phone]], f)
