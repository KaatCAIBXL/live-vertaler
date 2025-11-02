import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import tempfile
import av
import numpy as np
import io
import speech_recognition as sr
import wave

# 🌍 Taalinstellingen
bron_taal = st.selectbox("Welke taal spreek je?", ["fr", "pt", "nl", "zh-CN", "ln", "en-US", "es", "de"])
doel_taal = st.selectbox("Welke taal wil je horen?", ["nl", "fr", "pt", "zh-CN", "ln", "en-US", "es", "de"])

# 🎧 Tekst uitspreken
async def spreek_tekst(tekst, taalcode):
    stemmap = {
        "nl": "nl-NL-MaartenNeural",
        "fr": "fr-FR-DeniseNeural",
        "pt": "pt-BR-AntonioNeural",
        "zh-CN": "zh-CN-XiaoxiaoNeural",
        "es": "es-ES-AlvaroNeural",
        "de": "de-DE-ConradNeural",
        "en-US": "en-US-AriaNeural",
        "ln": "pt-BR-AntonioNeural",
    }
    stem = stemmap.get(taalcode, "en-US-AriaNeural")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        await edge_tts.Communicate(tekst, stem).save(tmpfile.name)
        return tmpfile.name

# 🧠 Audioverwerker
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        audio_bytes = audio.tobytes()
        self.buffer += audio_bytes

        if len(self.buffer) > 16000 * 5:  # 5 seconden audio
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(self.buffer)
            wav_io.seek(0)

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_io) as source:
                audio_data = recognizer.record(source)
                try:
                    zin = recognizer.recognize_google(audio_data, language=bron_taal)
                    st.write(f"🗣️ Origineel: {zin}")
                    vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
                    st.write(f"🌐 Vertaling: {vertaling}")
                    audiobestand = asyncio.run(spreek_tekst(vertaling, doel_taal))
                    with open(audiobestand, "rb") as af:
                        st.audio(af.read(), format="audio/mp3")
                except Exception as e:
                    st.warning(f"⚠️ Spraakherkenning mislukt: {e}")
            self.buffer = b""

        return frame

# 🚀 Streamlit interface
st.title("🌍 Live Spraakvertaler voor Telefoon en PC")
st.markdown("🎙️ Spreek live via je microfoon. Vertaling verschijnt automatisch en wordt uitgesproken.")

webrtc_streamer(
    key="live-vertaler",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)
