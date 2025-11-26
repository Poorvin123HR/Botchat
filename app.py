import streamlit as st
import random, json, os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from gtts import gTTS
import tempfile

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
    },
    "Hindi": {
        "title":"🤖 कृषि चैटबॉट 🌱",
        "enter_phone":"📱 अपना फोन नंबर दर्ज करें:",
        "send_otp":"OTP भेजें",
        "enter_otp":"🔐 OTP दर्ज करें:",
        "verify_otp":"OTP सत्यापित करें",
        "reset_otp":"🔄 OTP रीसेट / पुनः प्रयास करें",
        "verified":"✅ सत्यापित! स्वागत है।",
        "invalid_otp":"❌ अमान्य OTP।",
        "say_something":"कुछ कहें...",
        "clear_history":"🗑️ चैट इतिहास साफ़ करें",
        "change_phone":"🔁 फोन नंबर बदलें"
    },
    "Telugu": {
        "title":"🤖 వ్యవసాయ చాట్‌బాట్ 🌱",
        "enter_phone":"📱 మీ ఫోన్ నంబర్ నమోదు చేయండి:",
        "send_otp":"OTP పంపండి",
        "enter_otp":"🔐 OTP నమోదు చేయండి:",
        "verify_otp":"OTP నిర్ధారించండి",
        "reset_otp":"🔄 OTP రీసెట్ / మళ్లీ ప్రయత్నించండి",
        "verified":"✅ ధృవీకరించబడింది! స్వాగతం.",
        "invalid_otp":"❌ అమాన్య OTP.",
        "say_something":"ఏదైనా చెప్పండి...",
        "clear_history":"🗑️ చాట్ చరిత్రను తొలగించండి",
        "change_phone":"🔁 ఫోన్ నంబర్ మార్చండి"
    },
    "Tamil": {
        "title":"🤖 வேளாண் சாட்பாட் 🌱",
        "enter_phone":"📱 உங்கள் தொலைபேசி எண்ணை உள்ளிடவும்:",
        "send_otp":"OTP அனுப்பு",
        "enter_otp":"🔐 OTP ஐ உள்ளிடவும்:",
        "verify_otp":"OTP ஐ சரிபார்க்கவும்",
        "reset_otp":"🔄 OTP மீட்டமைக்கவும் / மீண்டும் முயற்சி செய்க",
        "verified":"✅ சரிபார்க்கப்பட்டது! வரவேற்பு.",
        "invalid_otp":"❌ தவறான OTP.",
        "say_something":"எதாவது சொல்லுங்கள்...",
        "clear_history":"🗑️ உரையாடல்கள் வரலாரை அழிக்கவும்",
        "change_phone":"🔁 தொலைபேசி எண்ணை மாற்றவும்"
    }
}

# Map display language name to language code for translate_text and gTTS
language_codes = {
    "English": "en",
    "Kannada": "kn",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta"
}

# --- Translation helper using Gemini ---
def translate_text(text, target_lang="en"):
    """
    target_lang should be a language code like 'en','kn','hi','te','ta'
    """
    try:
        prompt = f"Translate the following text into language code '{target_lang}':\n\n{text}"
        result = llm.invoke([HumanMessage(content=prompt)])
        return result.content
    except Exception:
        return text

# --- Session state init ---
for key in ["otp_sent","verified","current_phone","chat_histories","confirm_clear","show_html","generated_otp"]:
    if key not in st.session_state:
        st.session_state[key] = False if key in ["otp_sent","verified","confirm_clear","show_html"] else ({} if key=="chat_histories" else "")

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">🌾 Controls</div>', unsafe_allow_html=True)
    
    # Show language names in their native script to the user
    lang_display_options = ["English", "ಕನ್ನಡ", "हिन्दी", "తెలుగు", "தமிழ்"]
    hist_display_options = ["English", "ಕನ್ನಡ", "हिन्दी", "తెలుగు", "தமிழ்"]

    lang_choice_display = st.radio("🌐 Language", lang_display_options)
    history_lang_display = st.radio("📖 Chat History Language", hist_display_options)

    # Map displayed script names back to internal English keys used in translations dict
    lang_map = {
        "English": "English",
        "ಕನ್ನಡ": "Kannada",
        "हिन्दी": "Hindi",
        "తెలుగు": "Telugu",
        "தமிழ்": "Tamil"
    }

    # Convert to internal keys
    lang_choice = lang_map[lang_choice_display]
    history_lang = lang_map[history_lang_display]

    t = translations[lang_choice]

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
    content_key_map = {
        "English": "content_en",
        "Kannada": "content_kn",
        "Hindi": "content_hi",
        "Telugu": "content_te",
        "Tamil": "content_ta"
    }
    chosen_content_key = content_key_map.get(history_lang, "content_en")

    for m in chat_history:
        content = m.get(chosen_content_key) or m.get("content_en") or ""
        st.chat_message("user" if m["role"]=="user" else "assistant").markdown(content)

    # User input
    user_input = st.chat_input(t["say_something"])
    if user_input:
        user_lang_code = language_codes.get(lang_choice, "en")
        if user_lang_code != "en":
            translated_input_en = translate_text(user_input, "en")
        else:
            translated_input_en = user_input

        # Call LLM with English prompt
        result = llm.invoke([HumanMessage(content=translated_input_en)])
        response_en = result.content

        # Translate LLM response into supported languages
        response_kn = translate_text(response_en, "kn")
        response_hi = translate_text(response_en, "hi")
        response_te = translate_text(response_en, "te")
        response_ta = translate_text(response_en, "ta")

        display_text = {
            "en": response_en,
            "kn": response_kn,
            "hi": response_hi,
            "te": response_te,
            "ta": response_ta
        }.get(user_lang_code, response_en)

        # Store user and assistant multilingual entries
        chat_entry_user = {
            "role": "user",
            "content_en": translated_input_en,
            "content_kn": translate_text(translated_input_en, "kn"),
            "content_hi": translate_text(translated_input_en, "hi"),
            "content_te": translate_text(translated_input_en, "te"),
            "content_ta": translate_text(translated_input_en, "ta")
        }
        # preserve original user text in its language field if applicable
        if user_lang_code == "kn":
            chat_entry_user["content_kn"] = user_input
        elif user_lang_code == "hi":
            chat_entry_user["content_hi"] = user_input
        elif user_lang_code == "te":
            chat_entry_user["content_te"] = user_input
        elif user_lang_code == "ta":
            chat_entry_user["content_ta"] = user_input
        elif user_lang_code == "en":
            chat_entry_user["content_en"] = user_input

        chat_entry_assistant = {
            "role": "assistant",
            "content_en": response_en,
            "content_kn": response_kn,
            "content_hi": response_hi,
            "content_te": response_te,
            "content_ta": response_ta
        }

        chat_history.append(chat_entry_user)
        chat_history.append(chat_entry_assistant)

        # Show chat messages in UI
        st.chat_message("user").markdown(user_input)
        st.chat_message("assistant").markdown(display_text)

        # Save history to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)

        # --- Optional: Voice output ---
        gtts_lang_code = user_lang_code if user_lang_code in ["en","kn","hi","te","ta"] else "en"
        tts = gTTS(text=display_text, lang=gtts_lang_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            audio_bytes = open(tmpfile.name, "rb").read()
            st.audio(audio_bytes, format="audio/mp3")
