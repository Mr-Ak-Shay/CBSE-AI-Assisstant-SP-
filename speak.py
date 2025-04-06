from gtts import gTTS
from io import BytesIO
import streamlit as st

text = "Hello, this is a test message."
tts = gTTS(text)
with BytesIO() as audio:
    tts.write_to_fp(audio)
    audio.seek(0)
    st.audio(audio.read(), format='audio/mp3')
