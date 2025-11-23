import streamlit as st
import random, json, os
from gtts import gTTS
import speech_recognition as sr
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- Setup LLM ---
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# --- Page config ---
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
        "say_something": "Type or speak something..."
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
        "say_something": "ಟೈಪ್ ಅಥವಾ ಮಾತನಾಡಿ..."
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
for key in ["otp_sent","verified","current_phone","chat_histories","confirm_clear"]:
    if key not in st.session_state: st.session_state[key] = False if key in ["otp_sent","verified","confirm_clear"] else ""

if "chat_histories" not in st.session_state: st.session_state.chat_histories = {}

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">🌾 Controls</div>', unsafe_allow_html=True)

    lang_choice = st.radio("🌐 Language", ["English","Kannada"])
    t = translations[lang_choice]

    history_lang = st.radio("📖 Chat History Language", ["Kannada","English"])

    if st.session_state.current_phone:
        st.markdown(f'<div class="sidebar-phone">📱 Logged in: {st.session_state.current_phone}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-phone">📱 No phone number entered</div>', unsafe_allow_html=True)

    if st.button("🔁 Change Phone Number"):
        st.session_state.otp_sent = False
        st.session_state.verified = False
        st.session_state.current_phone = ""
        st.rerun()

    if st.button("🗑️ Clear Chat History"):
        phone = st.session_state.current_phone
        if phone in st.session_state.chat_histories:
            st.session_state.chat_histories[phone] = []
            st.success("Chat history cleared!")

# --- Title ---
st.title(t["title"])

# --- OTP Flow ---
if not st.session_state.verified:
    phone = st.text_input(t["enter_phone"], max_chars=10, value=st.session_state.current_phone)
    if phone != st.session_state.current_phone:
        st.session_state.current_phone = phone

    if st.session_state.current_phone and not st.session_state.otp_sent:
        if st.button(t["send_otp"]):
            st.session_state.generated_otp = str(random.randint(1000,9999))
            st.session_state.otp_sent = True
            st.info(f"Mock OTP: {st.session_state.generated_otp}")

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

# --- Chat with Voice --- 
else:
    phone = st.session_state.current_phone
    if phone not in st.session_state.chat_histories:
        st.session_state.chat_histories[phone] = []

    chat_history = st.session_state.chat_histories[phone]

    # Display history
    for m in chat_history:
        content = m.get("content_kn") if history_lang=="Kannada" else m.get("content_en")
        st.chat_message("user" if m["role"]=="user" else "assistant").markdown(content)

    # User input: text
    user_input = st.chat_input(t["say_something"])
    # User input: voice
    uploaded_audio = st.file_uploader("🎤 Record/Upload voice", type=["wav","mp3","ogg"])

    user_text = ""
    if uploaded_audio:
        recognizer = sr.Recognizer()
        with sr.AudioFile(uploaded_audio) as source:
            audio = recognizer.record(source)
            try:
                user_text = recognizer.recognize_google(audio, language="en-IN")
                st.info(f"You said: {user_text}")
            except Exception as e:
                st.error("Could not recognize audio.")

    if user_input: user_text = user_input

    if user_text:
        # Translation if Kannada
        if lang_choice=="Kannada":
            translated_input = translate_text(user_text,"en")
            result = llm.invoke([HumanMessage(content=translated_input)])
            response = result.content
            response_kn = translate_text(response,"kn")

            chat_history.append({"role":"user","content_en":translated_input,"content_kn":user_text})
            chat_history.append({"role":"assistant","content_en":response,"content_kn":response_kn})

            st.chat_message("user").markdown(user_text)
            st.chat_message("assistant").markdown(response_kn)

            # TTS
            tts = gTTS(response_kn, lang="kn")
        else:
            result = llm.invoke([HumanMessage(content=user_text)])
            response = result.content
            chat_history.append({"role":"user","content_en":user_text,"content_kn":translate_text(user_text,"kn")})
            chat_history.append({"role":"assistant","content_en":response,"content_kn":translate_text(response,"kn")})

            st.chat_message("user").markdown(user_text)
            st.chat_message("assistant").markdown(response)

            tts = gTTS(response, lang="en")

        # Play audio
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        st.audio(mp3_fp, format="audio/mp3")

    # Save history
    filename = f"chat_{phone}.json"
    with open(filename,"w",encoding="utf-8") as f:
        json.dump(chat_history,f,ensure_ascii=False)
