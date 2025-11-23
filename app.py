import streamlit as st
import random, json, os
from io import BytesIO
from gtts import gTTS
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- Setup ---
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

st.set_page_config(page_title="AgriBot Voice Chatbot", layout="centered")

# --- CSS ---
st.markdown("""
<style>
.stApp {background: linear-gradient(to right, #e0f7fa, #f1f8e9); font-family: 'Verdana', sans-serif;}
h1,h2,h3 {color: #2e7d32; text-align:center; text-shadow:2px 2px 4px #a5d6a7;}
.stChatMessage {border-radius:15px; padding:12px; margin:8px 0; box-shadow:0 4px 12px rgba(0,0,0,0.2);}
.stChatMessage[data-testid="stChatMessage-user"] {background-color:#c8e6c9; color:#1b5e20;}
.stChatMessage[data-testid="stChatMessage-assistant"] {background-color:#ffffff; border:2px solid #2e7d32; color:#33691e;}
section[data-testid="stSidebar"] {background:linear-gradient(to bottom, #f1f8e9, #e0f7fa); border-left:3px solid #2e7d32; padding:20px;}
.sidebar-header {font-weight:700; font-size:18px; color:#1b5e20; margin-bottom:12px; text-align:center; text-shadow:1px 1px 2px #a5d6a7;}
.sidebar-phone {font-size:14px; color:#33691e; background:#c8e6c9; padding:8px; border-radius:8px; margin-bottom:12px; text-align:center; font-weight:600;}
section[data-testid="stSidebar"] button {background-color:#2e7d32 !important; color:white !important; border-radius:8px !important; padding:8px 14px !important; font-size:14px !important; margin-bottom:10px; width:100%;}
section[data-testid="stSidebar"] button:hover {background-color:#1b5e20 !important;}
</style>
""", unsafe_allow_html=True)

# --- Translations ---
translations = {
    "English": {
        "title": "🤖 AGRICULTURE VOICE CHATBOT 🌱",
        "enter_phone": "📱 Enter your phone number:",
        "send_otp": "Send OTP",
        "enter_otp": "🔐 Enter OTP:",
        "verify_otp": "Verify OTP",
        "reset_otp": "🔄 Reset OTP / Try Again",
        "verified": "✅ Verified! Welcome back.",
        "invalid_otp": "❌ Invalid OTP.",
        "say_something": "Type something...",
        "voice_input": "🎤 Speak below"
    },
    "Kannada": {
        "title": "🤖 ಕೃಷಿ ವಾಯ್ಸ್ ಚಾಟ್‌ಬಾಟ್ 🌱",
        "enter_phone": "📱 ನಿಮ್ಮ ಫೋನ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ:",
        "send_otp": "OTP ಕಳುಹಿಸಿ",
        "enter_otp": "🔐 OTP ನಮೂದಿಸಿ:",
        "verify_otp": "OTP ಪರಿಶೀಲಿಸಿ",
        "reset_otp": "🔄 OTP ಮರುಹೊಂದಿಸಿ / ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",
        "verified": "✅ ಪರಿಶೀಲಿಸಲಾಗಿದೆ! ಮತ್ತೆ ಸ್ವಾಗತ.",
        "invalid_otp": "❌ ತಪ್ಪಾದ OTP.",
        "say_something": "ಎನಾದರೂ ಟೈಪ್ ಮಾಡಿ...",
        "voice_input": "🎤 ಕೆಳಗೆ ಮಾತನಾಡಿ"
    }
}

# --- Translation helper ---
def translate_text(text, target_lang="kn"):
    try:
        prompt = f"Translate the following text into {target_lang}:\n\n{text}"
        result = llm.invoke([HumanMessage(content=prompt)])
        return result.content
    except Exception:
        return text

# --- State init ---
for key in ["otp_sent", "verified", "current_phone", "chat_histories", "confirm_clear", "show_html"]:
    if key not in st.session_state: st.session_state[key] = False if key != "chat_histories" else {}

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">🌾 Controls</div>', unsafe_allow_html=True)
    lang_choice = st.radio("🌐 Language", ["English", "Kannada"])
    t = translations[lang_choice]
    history_lang = st.radio("📖 Chat History Language", ["Kannada", "English"])

    if st.session_state.current_phone:
        st.markdown(f'<div class="sidebar-phone">📱 Logged in: {st.session_state.current_phone}</div>', unsafe_allow_html=True)
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

# --- Title ---
st.title(t["title"])

# --- Phone + OTP flow ---
if not st.session_state.verified:
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

    # Load history safely
    if phone not in st.session_state.chat_histories:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    st.session_state.chat_histories[phone] = json.load(f)
            except (json.JSONDecodeError, TypeError):
                st.session_state.chat_histories[phone] = []
                st.warning("Previous chat history corrupted, starting fresh.")
        else:
            st.session_state.chat_histories[phone] = []

    chat_history = st.session_state.chat_histories[phone]

    # Display history in chosen language
    for m in chat_history:
        content = m.get("content_kn") if history_lang == "Kannada" else m.get("content_en")
        st.chat_message(m["role"]).markdown(content)

    st.markdown("---")
    st.markdown("🎤 **Voice Input:** (Click mic icon and speak)")

    # --- Streamlit WebRTC for mic input ---
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
    import av
    import numpy as np
    import tempfile
    import soundfile as sf

    class AudioProcessor:
        def __init__(self):
            self.audio_data = None

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            array = frame.to_ndarray()
            self.audio_data = array
            return frame

    ctx = webrtc_streamer(
        key="agri_voice",
        mode=WebRtcMode.SENDONLY,
        client_settings=ClientSettings(
            media_stream_constraints={"audio": True, "video": False},
            async_processing=True,
        ),
        audio_processor_factory=AudioProcessor,
    )

    if ctx.state.playing and ctx.audio_processor:
        audio_array = ctx.audio_processor.audio_data
        if audio_array is not None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                sf.write(tmpfile.name, audio_array.T, 44100)
                tmpfile.flush()
                st.session_state.user_audio_file = tmpfile.name
                st.info("Audio captured! Click 'Process Voice' to send.")

    if st.button("Process Voice"):
        if "user_audio_file" in st.session_state:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(st.session_state.user_audio_file) as source:
                audio_data = r.record(source)
                try:
                    user_input = r.recognize_google(audio_data, language="kn-IN" if lang_choice=="Kannada" else "en-US")
                    st.info(f"You said: {user_input}")
                except sr.UnknownValueError:
                    st.warning("Could not understand audio.")
                    user_input = ""
        else:
            user_input = st.chat_input(t["say_something"])

        if user_input:
            # LLM processing
            if lang_choice == "Kannada":
                translated_input = translate_text(user_input, "en")
                result = llm.invoke([HumanMessage(content=translated_input)])
                response = result.content
                response_kn = translate_text(response, "kn")

                chat_history.append({"role": "user", "content_en": translated_input, "content_kn": user_input})
                chat_history.append({"role": "assistant", "content_en": response, "content_kn": response_kn})

                st.chat_message("user").markdown(user_input)
                st.chat_message("assistant").markdown(response_kn)
                tts = gTTS(response_kn, lang='kn')
            else:
                result = llm.invoke([HumanMessage(content=user_input)])
                response = result.content

                chat_history.append({"role": "user", "content_en": user_input, "content_kn": translate_text(user_input, "kn")})
                chat_history.append({"role": "assistant", "content_en": response, "content_kn": translate_text(response, "kn")})

                st.chat_message("user").markdown(user_input)
                st.chat_message("assistant").markdown(response)
                tts = gTTS(response, lang='en')

            # Play TTS
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            st.audio(audio_bytes.getvalue(), format='audio/mp3')

            # Save history
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
