import streamlit as st
import random, json, os
import streamlit.components.v1 as components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- Setup ---
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

st.set_page_config(page_title="AgriBot Chatbot", layout="centered")

# --- Theme CSS ---
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
    /* Sidebar full background */
section[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #f1f8e9, #e0f7fa);
    border-left: 3px solid #2e7d32;
    padding: 20px;
}

/* Sidebar header */
.sidebar-header {
    font-weight: 700;
    font-size: 18px;
    color: #1b5e20;
    margin-bottom: 12px;
    text-align: center;
    text-shadow: 1px 1px 2px #a5d6a7;
}

/* Phone status box */
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

/* Sidebar buttons */
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

# --- Translations ---
translations = {
    "English": {
        "title": "🤖 AGRICULTURE CHATBOT 🌱",
        "enter_phone": "📱 Enter your phone number:",
        "send_otp": "Send OTP",
        "enter_otp": "🔐 Enter OTP:",
        "verify_otp": "Verify OTP",
        "reset_otp": "🔄 Reset OTP / Try Again",
        "verified": "✅ Verified! Welcome back.",
        "invalid_otp": "❌ Invalid OTP.",
        "say_something": "Say something..."
    },
    "Kannada": {
        "title": "🤖 ಕೃಷಿ ಚಾಟ್‌ಬಾಟ್ 🌱",
        "enter_phone": "📱 ನಿಮ್ಮ ಫೋನ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ:",
        "send_otp": "OTP ಕಳುಹಿಸಿ",
        "enter_otp": "🔐 OTP ನಮೂದಿಸಿ:",
        "verify_otp": "OTP ಪರಿಶೀಲಿಸಿ",
        "reset_otp": "🔄 OTP ಮರುಹೊಂದಿಸಿ / ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",
        "verified": "✅ ಪರಿಶೀಲಿಸಲಾಗಿದೆ! ಮತ್ತೆ ಸ್ವಾಗತ.",
        "invalid_otp": "❌ ತಪ್ಪಾದ OTP.",
        "say_something": "ಏನಾದರೂ ಹೇಳಿ..."
    }
}

# --- Translation helper using Gemini ---
def translate_text(text, target_lang="kn"):
    try:
        prompt = f"Translate the following text into {target_lang}:\n\n{text}"
        result = llm.invoke([HumanMessage(content=prompt)])
        return result.content
    except Exception:
        return text

# --- State init ---
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "verified" not in st.session_state: st.session_state.verified = False
if "current_phone" not in st.session_state: st.session_state.current_phone = ""
if "chat_histories" not in st.session_state: st.session_state.chat_histories = {}
if "confirm_clear" not in st.session_state: st.session_state.confirm_clear = False
if "show_html" not in st.session_state: st.session_state.show_html = False

# --- Sidebar controls (merged old + new + Kannada keyboard) ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">🌾 Controls</div>', unsafe_allow_html=True)

    # Language toggle
    lang_choice = st.radio("🌐 Language", ["English", "Kannada"])
    t = translations[lang_choice]

    # History language toggle
    history_lang = st.radio("📖 Chat History Language", ["Kannada", "English"])

    # Phone status
    if st.session_state.current_phone:
        st.markdown(
            f'<div class="sidebar-phone">📱 Logged in: {st.session_state.current_phone}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="sidebar-phone">📱 No phone number entered</div>', unsafe_allow_html=True)

    # Old sidebar buttons
    if st.button("🔁 Change Phone Number"):
        st.session_state.otp_sent = False
        st.session_state.verified = False
        st.session_state.current_phone = ""
        st.session_state.confirm_clear = False
        st.session_state.show_html = False
        st.rerun()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.confirm_clear = True

    if st.button("Other Features"):
        st.session_state.show_html = True

    if st.session_state.show_html:
        if st.button("⬅️ Back to Chatbot"):
            st.session_state.show_html = False
            st.rerun()

# --- Title ---
st.title(t["title"])

# --- Redirect to external page ---
if st.session_state.show_html:
    st.markdown(
        '<a href="http://localhost:8080/mini/1.html" target="_blank">Home Page</a>',
        unsafe_allow_html=True
    )

# --- Phone + OTP flow ---
elif not st.session_state.verified:
    phone = st.text_input(t["enter_phone"], max_chars=10, value=st.session_state.current_phone)
    if phone != st.session_state.current_phone:
        st.session_state.current_phone = phone

    if st.session_state.current_phone and not st.session_state.otp_sent:
        if st.button(t["send_otp"]):
            st.session_state.generated_otp = str(random.randint(1000, 9999))
            st.session_state.otp_sent = True
            st.info(f"Mock OTP (for demo): {st.session_state.generated_otp}")

    if st.session_state.otp_sent and not st.session_state.verified:
        otp_input = st.text_input(t["enter_otp"], type="password")
        if st.button(t["verify_otp"]):
            if otp_input == st.session_state.generated_otp:
                st.session_state.verified = True
                st.success(t["verified"])
            else:
                st.error(t["invalid_otp"])
        if st.button(t["reset_otp"]):
            st.session_state.otp_sent = False
            st.info("You can request a new OTP now.")

# --- Chat UI ---
elif st.session_state.verified and st.session_state.current_phone:
    phone = st.session_state.current_phone
    filename = f"chat_{phone}.json"

    # Clear history confirmation
    if st.session_state.confirm_clear:
        st.warning("⚠️ Are you sure you want to clear your chat history?")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Yes, clear history"):
                st.session_state.chat_histories[phone] = []
                if os.path.exists(filename):
                    os.remove(filename)
                st.session_state.confirm_clear = False
                st.success("Chat history cleared!")
        with col2:
            if st.button("Cancel"):
                st.session_state.confirm_clear = False
                st.info("Clear history cancelled.")

    # Load history
    if phone not in st.session_state.chat_histories:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                st.session_state.chat_histories[phone] = json.load(f)
        else:
            st.session_state.chat_histories[phone] = []

    chat_history = st.session_state.chat_histories[phone]

    # Display history in chosen language
    for m in chat_history:
        content = m.get("content_kn") if history_lang == "Kannada" else m.get("content_en")
        if m["role"] == "user":
            st.chat_message("user").markdown(content)
        elif m["role"] == "assistant":
            st.chat_message("assistant").markdown(content)

    # User input
    user_input = st.chat_input(t["say_something"])
    if user_input:
        if lang_choice == "Kannada":
            translated_input = translate_text(user_input, "en")
            result = llm.invoke([HumanMessage(content=translated_input)])
            response = result.content
            response_kn = translate_text(response, "kn")

            chat_history.append({"role": "user", "content_en": translated_input, "content_kn": user_input})
            chat_history.append({"role": "assistant", "content_en": response, "content_kn": response_kn})

            st.chat_message("user").markdown(user_input)
            st.chat_message("assistant").markdown(response_kn)
        else:
            result = llm.invoke([HumanMessage(content=user_input)])
            response = result.content

            chat_history.append({"role": "user", "content_en": user_input, "content_kn": translate_text(user_input, "kn")})
            chat_history.append({"role": "assistant", "content_en": response, "content_kn": translate_text(response, "kn")})

            st.chat_message("user").markdown(user_input)
            st.chat_message("assistant").markdown(response)

        # Save history
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, ensure_ascii=False)
