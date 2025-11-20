import streamlit as st
import random, json, os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

st.set_page_config(page_title="AgriBot Chatbot", layout="centered")
st.title("🤖 AGRICULTURE CHATBOT 🌱")

# --- Step 1: Phone number input ---
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "verified" not in st.session_state:
    st.session_state.verified = False

phone = st.text_input("📱 Enter your phone number:", max_chars=10)

if phone and not st.session_state.otp_sent:
    if st.button("Send OTP"):
        st.session_state.generated_otp = str(random.randint(1000, 9999))  # mock OTP
        st.session_state.otp_sent = True
        st.info(f"Mock OTP (for demo): {st.session_state.generated_otp}")  
        # In production, send via SMS API like Twilio/Firebase instead of showing it

# --- Step 2: OTP verification ---
if st.session_state.otp_sent and not st.session_state.verified:
    otp_input = st.text_input("🔐 Enter OTP:", type="password")
    if st.button("Verify OTP"):
        if otp_input == st.session_state.generated_otp:
            st.session_state.verified = True
            st.success("✅ Verified! Welcome back.")
        else:
            st.error("❌ Invalid OTP. Try again.")

# --- Step 3: Load chat if verified ---
if st.session_state.verified:
    filename = f"chat_{phone}.json"
    if "chat_history" not in st.session_state:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                saved = json.load(f)
            st.session_state.chat_history = [
                HumanMessage(content=m["content"]) if m["role"]=="user" else
                AIMessage(content=m["content"]) if m["role"]=="assistant" else
                SystemMessage(content=m["content"]) for m in saved
            ]
        else:
            st.session_state.chat_history = [SystemMessage(content="You are a helpful assistant.")]

    # Display past messages
    for msg in st.session_state.chat_history:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)

    # User input
    user_input = st.chat_input("Say something...")
    if user_input:
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        st.chat_message("user").markdown(user_input)

        result = llm.invoke(st.session_state.chat_history)
        response = result.content

        st.session_state.chat_history.append(AIMessage(content=response))
        st.chat_message("assistant").markdown(response)

        # Save with role + content
        with open(filename, "w") as f:
            json.dump([{"role": "user" if isinstance(m, HumanMessage) else
                        "assistant" if isinstance(m, AIMessage) else "system",
                        "content": m.content} for m in st.session_state.chat_history], f)
