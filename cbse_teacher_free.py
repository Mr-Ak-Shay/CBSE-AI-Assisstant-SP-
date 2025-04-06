import streamlit as st
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import requests
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr

# OpenRouter API key
OPENROUTER_API_KEY = "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"

# --- PAGE CONFIG ---
st.set_page_config(page_title="📘 CBSE Teacher AI Assistant", layout="centered")
st.sidebar.title("🎓 CBSE Teacher Assistant")
st.sidebar.markdown("Built for Class 12 Computer Science students and teachers.\nFree, fast & fully open-source!")

# --- FUNCTIONS ---

def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "".join([page.extract_text() or "" for page in reader.pages])
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    return ""

def extract_text_from_image(image_file):
    image = Image.open(image_file)
    return pytesseract.image_to_string(image)

def query_openrouter(prompt):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful CBSE Class 12 Computer Science teacher."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Error reaching AI: {str(e)}"

def speak_text(text):
    try:
        tts = gTTS(text)
        audio = BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio
    except Exception as e:
        st.error(f"TTS generation failed: {e}")
        return None

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("🎤 Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand your voice."
    except sr.RequestError:
        return "Speech recognition service is unavailable."

# --- SESSION STATE ---
if "question" not in st.session_state:
    st.session_state.question = ""

# --- UI ---

st.title("📘 CBSE Class 12 - Teacher AI Assistant")
st.caption("Upload notes, ask CS questions, use voice, or even scan a question image 📸")

uploaded_file = st.file_uploader("📄 Upload Notes (PDF or TXT)", type=["pdf", "txt"])
image_file = st.file_uploader("🖼️ Upload Image of a CS Question", type=["jpg", "jpeg", "png"])

# Extract context
context = ""
if uploaded_file:
    context = extract_text(uploaded_file)
    with st.expander("📄 Extracted Text from File"):
        st.write(context[:2000] + "..." if len(context) > 2000 else context)

if image_file:
    image_text = extract_text_from_image(image_file)
    with st.expander("📝 Extracted Text from Image"):
        st.write(image_text)
    context += "\n" + image_text

# Search inside context
if context:
    keyword = st.text_input("🔍 Search inside uploaded notes (optional)", placeholder="e.g. list, file handling")
    if keyword:
        found = "\n".join([line for line in context.split('\n') if keyword.lower() in line.lower()])
        st.markdown("#### 🔎 Results:")
        st.text(found if found else "❌ No matches found.")

typed_input = st.text_input("💬 Type your question below", value=st.session_state.question)
if typed_input != st.session_state.question:
    st.session_state.question = typed_input

if st.button("🎙️ Record Voice Input"):
    spoken = recognize_speech_from_mic()
    st.success(f"🗣️ You said: {spoken}")
    st.session_state.question = spoken

# ✅ New Checkbox to toggle speech
speak_answer = st.checkbox("🔊 Speak the answer out loud?")

# --- Get Answer ---
if st.button("🚀 Get Answer"):
    question = st.session_state.question
    if not question.strip():
        st.warning("Please type or speak a question.")
    else:
        full_prompt = f"""You are a CBSE Class 12 Computer Science teacher. Use the provided context if needed.

Context:
{context}

Question: {question}
"""
        with st.spinner("Talking to AI..."):
            answer = query_openrouter(full_prompt)

        st.success("✅ Answer Generated")
        st.markdown("### 📘 Answer:")
        st.write(answer)

        # 🔊 Only speak if checkbox is checked
        if speak_answer:
            audio_data = speak_text(answer)
            if audio_data:
                st.markdown("🔊 **Listen to the Answer:**")
                st.audio(audio_data, format='audio/mp3')
            else:
                st.warning("⚠️ Could not generate audio.")

# --- Footer ---
st.markdown("---")
st.caption("👨‍🏫 Made with ❤️ by Akshay | Fully free for CBSE schools.")
