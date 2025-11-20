import streamlit as st
import random, json, os
import streamlit.components.v1 as components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Setup
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

st.set_page_config(page_title="AgriBot Chatbot", layout="centered")

# Theme CSS including sidebar styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #e0f7fa, #f1f8e9);
        font-family: 'Verdana', sans-serif;
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
    .stTextInput input, .stChatInput textarea {
        border-radius: 10px;
        border: 1px solid #a5d6a7;
        padding: 10px;
        font-size: 14px;
    }
    button, .stButton>button {
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        font-size: 14px !important;
    }
    .stButton>button:hover {
        background-color: #1b5e20 !important;
    }
    .stAlert {
        border-radius: 10px;
        padding: 10px;
    }
    /* Sidebar container */
    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #f1f8e9, #e0f7fa);
        border-left: 3px solid #2e7d32;
        padding: 20px;
    }
    .sidebar-header {
        font-weight: 700;
        font-size: 18px;
        color: #1b5e20;
        margin-bottom: 12px;
        text-align: center;
        text-shadow: 1px 1px 2px #a5d6a7;
    }
    .sidebar-phone {
        font-size: 14px;
        color: #33691e;
        background: #c8e6c9;
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 12px;
        text-align: center;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] button {
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        font-size: 14px !important;
        margin-bottom: 10px;
        width: 100%;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #1b5e20 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AGRICULTURE CHATBOT 🌱")

# --- State init ---
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "verified" not in st.session_state: st.session_state.verified = False
if "current_phone" not in st.session_state: st.session_state.current_phone = ""
if "chat_histories" not in st.session_state: st.session_state.chat_histories = {}
if "confirm_clear" not in st.session_state: st.session_state.confirm_clear = False
if "show_html" not in st.session_state: st.session_state.show_html = False  # HTML view toggle

# --- Sidebar controls ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">🌾 Controls</div>', unsafe_allow_html=True)

    if st.session_state.current_phone:
        st.markdown(
            f'<div class="sidebar-phone">📱 Logged in: {st.session_state.current_phone}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="sidebar-phone">📱 No phone number entered</div>', unsafe_allow_html=True)

    if st.button("🔁 Change Phone Number"):
        st.session_state.otp_sent = False
        st.session_state.verified = False
        st.session_state.current_phone = ""
        st.session_state.confirm_clear = False
        st.session_state.show_html = False
        st.rerun()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.confirm_clear = True

    if st.button("📄 Open HTML Page"):
        st.session_state.show_html = True

    if st.session_state.show_html:
        if st.button("⬅️ Back to Chatbot"):
            st.session_state.show_html = False
            st.rerun()

# --- Show HTML page if requested ---
if st.session_state.show_html:
    try:
        with open(r"C:\Users\mithu\eclipse-workspace\mini\src\main\webapp\1.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=600, scrolling=True)
    except Exception as e:
        st.error(f"Could not load HTML file: {e}")

# --- Phone + OTP flow ---
elif not st.session_state.verified:
    phone = st.text_input("📱 Enter your phone number:", max_chars=10, value=st.session_state.current_phone)
    if phone != st.session_state.current_phone:
        st.session_state.current_phone = phone

    if st.session_state.current_phone and not st.session_state.otp_sent:
        if st.button("Send OTP"):
            st.session_state.generated_otp = str(random.randint(1000, 9999))  # mock OTP for demo
            st.session_state.otp_sent = True
            st.info(f"Mock OTP (for demo): {st.session_state.generated_otp}")

    if st.session_state.otp_sent and not st.session_state.verified:
        otp_input = st.text_input("🔐 Enter OTP:", type="password")
        if st.button("Verify OTP"):
            if otp_input == st.session_state.generated_otp:
                st.session_state.verified = True
                st.success("✅ Verified! Welcome back.")
            else:
                st.error("❌ Invalid OTP.")
        if st.button("🔄 Reset OTP / Try Again"):
            st.session_state.otp_sent = False
            st.info("You can request a new OTP now.")

# --- After verification: chat UI ---
elif st.session_state.verified and st.session_state.current_phone:
    phone = st.session_state.current_phone
    filename = f"chat_{phone}.json"

    # Clear history confirmation
    if st.session_state.confirm_clear:
        st.warning("⚠️ Are you sure you want to clear your chat history?")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Yes, clear history"):
                st.session_state.chat_histories[phone] = [SystemMessage(content="You are a helpful assistant.")]
                if os.path.exists(filename):
                    os.remove(filename)
                st.session_state.confirm_clear = False
                st.success("Chat history cleared!")
        with col2:
            if st.button("Cancel"):
                st.session_state.confirm_clear = False
                st.info("Clear history cancelled.")

    # Load chat history for this phone if not present
    if phone not in st.session_state.chat_histories:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                saved = json.load(f)
            history = []
            for m in saved:
                if isinstance(m, dict) and "role" in m and "content" in m:
                    if m["role"] == "user":
                        history.append(HumanMessage(content=m["content"]))
                    elif m["role"] == "assistant":
                        history.append(AIMessage(content=m["content"]))
                    else:
                        history.append(SystemMessage(content=m["content"]))
                elif isinstance(m, str):
                    history.append(HumanMessage(content=m))
            st.session_state.chat_histories[phone] = history
        else:
            st.session_state.chat_histories[phone] = [SystemMessage(content="You are a helpful assistant.")]

    # Use the session state's chat history
    chat_history = st.session_state.chat_histories[phone]

    # Display past messages
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)

    # User input
    user_input = st.chat_input("Say something...")
    if user_input:
        chat_history.append(HumanMessage(content=user_input))
        st.chat_message("user").markdown(user_input)

        result = llm.invoke(chat_history)
        response = result.content

        chat_history.append(AIMessage(content=response))
        st.chat_message("assistant").markdown(response)

        # Save with role + content
        with open(filename, "w") as f:
            json.dump([
                {
                    "role": "user" if isinstance(m, HumanMessage) else
                            "assistant" if isinstance(m, AIMessage) else "system",
                    "content": m.content
                }
                for m in chat_history
            ], f)
