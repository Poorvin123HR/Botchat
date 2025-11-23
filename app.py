import streamlit as st
import random, json, os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from gtts import gTTS
import tempfile
import base64

# --- Setup ---
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

st.set_page_config(page_title="AgriBot Chatbot", layout="centered")

# --- CSS Theme ---
st.markdown("""
<style>
.stApp {background: linear-gradient(to right, #e0f7fa, #f1f8e9); font-family: 'Verdana', sans-serif;}
h1,h2,h3 {color:#2e7d32; text-align:center; text-shadow:2px 2px 4px #a5d6a7;}
.stChatMessage {border-radius:15px; padding:12px; margin:8px 0; box-shadow:0 4px 12px rgba(0,0,0,0.2);}
.stChatMessage[data-testid="stChatMessage-user"] {background-color:#c8e6c9; color:#1b5e20;}
.stChatMessage[data-testid="stChatMessage-assistant"] {background-color:#ffffff; border:2px solid #2e7d32; color:#33691e;}
section[data-testid="stSidebar"] {background: linear-gradient(to bottom,#f1f8e9,#e0f7fa); border-left:3px solid #2e7d32; padding:20px;}
.sidebar-header {font-weight:700; font-size:18px; color:#1b5e20; margin-bottom:12px; text-align:center; text-shadow:1px 1px 2px #a5d6a7;}
.sidebar-phone {font-size:14px; color:#33691e; background:#c8e6c9; padding:8px; border-radius:8px; margin-bottom:12px; text-align:center; font-weight:600;}
section[data-testid="stSidebar"] button {background-color:#2e7d32 !important; color:white !important; border-radius:8px !important; padding:8px 14px !important; font-size:14px !important; margin-bottom:10px; width:100%;}
section[data-testid="stSidebar"] button:hover {background-color:#1b5e20 !important;}
</style>
""", unsafe_allow_html=True)

# --- Translations ---
translations = {
    "English": {
        "title":"🤖 AGRICULTURE CHATBOT 🌱",
        "enter_phone":"📱 Enter your phone number:",
        "send_otp":"Send OTP",
        "enter_otp":"🔐 Enter OTP:",
        "verify_otp":"Verify OTP",
        "reset_otp":"🔄 Reset OTP / Try Again",
        "verified":"✅ Verified! Welcome back.",
        "invalid_otp":"❌ Invalid OTP.",
        "say_something":"Say something...",
        "clear_history":"🗑️ Clear Chat History",
        "change_phone":"🔁 Change Phone Number"
    },
    "Kannada": {
        "title":"🤖 ಕೃಷಿ ಚಾಟ್‌ಬಾಟ್ 🌱",
        "enter_phone":"📱 ನಿಮ್ಮ ಫೋನ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ:",
        "send_otp":"OTP ಕಳುಹಿಸಿ",
        "enter_otp":"🔐 OTP ನಮೂದಿಸಿ:",
        "verify_otp":"OTP ಪರಿಶೀಲಿಸಿ",
        "reset_otp":"🔄 OTP ಮರುಹೊಂದಿಸಿ / ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",
        "verified":"✅ ಪರಿಶೀಲಿಸಲಾಗಿದೆ! ಮತ್ತೆ ಸ್ವಾಗತ.",
        "invalid_otp":"❌ ತಪ್ಪಾದ OTP.",
        "say_something":"ಏನಾದರೂ ಹೇಳಿ...",
        "clear_history":"🗑️ ಚಾಟ್ ಇತಿಹಾಸವನ್ನು ಅಳಿಸಿ",
        "change_phone":"🔁 ಫೋನ್ ಸಂಖ್ಯೆಯನ್ನು ಬದಲಿಸಿ"
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

# --- Session state init ---
for key in ["otp_sent","verified","current_phone","chat_histories","confirm_clear","show_html"]:
    if key not in st.session_state:
        st.session_state[key] = False if key in ["otp_sent","verified","confirm_clear","show_html"] else ({} if key=="chat_histories" else "")

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">🌾 Controls</div>', unsafe_allow_html=True)
    
    lang_choice = st.radio("🌐 Language", ["English","Kannada"])
    t = translations[lang_choice]

    history_lang = st.radio("📖 Chat History Language", ["English","Kannada"])

    phone_status = st.session_state.current_phone
    st.markdown(f'<div class="sidebar-phone">📱 {"Logged in: "+phone_status if phone_status else "No phone number entered"}</div>', unsafe_allow_html=True)

    if st.button(t["change_phone"]):
        st.session_state.update({"otp_sent":False,"verified":False,"current_phone":"","confirm_clear":False,"show_html":False})
        st.experimental_rerun()
    if st.button(t["clear_history"]):
        st.session_state.confirm_clear = True

# --- Title ---
st.title(t["title"])

# --- Phone + OTP flow ---
if not st.session_state.verified:
    phone = st.text_input(t["enter_phone"], max_chars=10, value=st.session_state.current_phone)
    st.session_state.current_phone = phone

    if phone and not st.session_state.otp_sent:
        if st.button(t["send_otp"]):
            st.session_state.generated_otp = str(random.randint(1000,9999))
            st.session_state.otp_sent = True
            st.info(f"Mock OTP (demo): {st.session_state.generated_otp}")

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
else:
    phone = st.session_state.current_phone
    if phone not in st.session_state.chat_histories:
        st.session_state.chat_histories[phone] = []

    chat_history = st.session_state.chat_histories[phone]

    # Clear history confirmation
    if st.session_state.confirm_clear:
        st.warning("⚠️ Are you sure you want to clear your chat history?")
        col1,col2 = st.columns(2)
        with col1:
            if st.button("Yes, clear history"):
                st.session_state.chat_histories[phone] = []
                filename = f"chat_{phone}.json"
                if os.path.exists(filename): os.remove(filename)
                st.session_state.confirm_clear = False
                st.success("Chat history cleared!")
        with col2:
            if st.button("Cancel"):
                st.session_state.confirm_clear = False
                st.info("Clear cancelled.")

    # Load saved history if exists
    filename = f"chat_{phone}.json"
    if not chat_history and os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            st.session_state.chat_histories[phone] = json.load(f)
        chat_history = st.session_state.chat_histories[phone]

    # Display history
    for m in chat_history:
        content = m.get("content_kn") if history_lang=="Kannada" else m.get("content_en")
        st.chat_message("user" if m["role"]=="user" else "assistant").markdown(content)

    # User input
    user_input = st.chat_input(t["say_something"])
    if user_input:
        if lang_choice=="Kannada":
            translated_input = translate_text(user_input, "en")
            result = llm.invoke([HumanMessage(content=translated_input)])
            response_en = result.content
            response_kn = translate_text(response_en, "kn")
            chat_history.append({"role":"user","content_en":translated_input,"content_kn":user_input})
            chat_history.append({"role":"assistant","content_en":response_en,"content_kn":response_kn})
            st.chat_message("user").markdown(user_input)
            st.chat_message("assistant").markdown(response_kn)
        else:
            result = llm.invoke([HumanMessage(content=user_input)])
            response_en = result.content
            response_kn = translate_text(response_en, "kn")
            chat_history.append({"role":"user","content_en":user_input,"content_kn":response_kn})
            chat_history.append({"role":"assistant","content_en":response_en,"content_kn":response_kn})
            st.chat_message("user").markdown(user_input)
            st.chat_message("assistant").markdown(response_en)

        # Save history to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, ensure_ascii=False)

        # --- Optional: Voice output ---
        tts = gTTS(text=response_en if lang_choice=="English" else response_kn, lang='en' if lang_choice=="English" else 'kn')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            audio_bytes = open(tmpfile.name, "rb").read()
            st.audio(audio_bytes, format="audio/mp3")
