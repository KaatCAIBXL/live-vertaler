import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import tempfile
import av
import openai_whisper as whisper

# 🌍 Taalinstellingen
bron_taal = st.selectbox("Welke taal spreekt de pastoor?", ["fr", "pt", "nl", "zh", "en", "es", "de"])
doel_taal = st.selectbox("Welke taal wil je horen?", ["nl", "fr", "pt", "zh", "ln", "en", "es", "de"])

# 🎧 Tekst uitspreken
async def spreek_tekst(tekst, taalcode):
    stemmap = {
        "nl": "nl-NL-MaartenNeural",
        "fr": "fr-FR-DeniseNeural",
        "pt": "pt-BR-AntonioNeural",
        "zh": "zh-CN-XiaoxiaoNeural",
        "es": "es-ES-AlvaroNeural",
        "de": "de-DE-ConradNeural",
        "en": "en-US-AriaNeural",
        "ln": "pt-BR-AntonioNeural",
    }
    stem = stemmap.get(taalcode, "en-US-AriaNeural")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        await edge_tts.Communicate(tekst, stem).save(tmpfile.name)
        return tmpfile.name

# 🧠 Audioverwerker
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.model = whisper.load_model("base")
        self.buffer = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        self.buffer += audio.tobytes()

        if len(self.buffer) > 16000 * 5:  # 5 seconden audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(self.buffer)
                f.flush()
                result = self.model.transcribe(f.name, language=bron_taal)
                zin = result["text"].strip()
                vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
                st.write(f"🗣️ Origineel: {zin}")
                st.write(f"🌐 Vertaling: {vertaling}")
                audiobestand = asyncio.run(spreek_tekst(vertaling, doel_taal))
                with open(audiobestand, "rb") as af:
                    st.audio(af.read(), format="audio/mp3")
            self.buffer = b""

        return frame

# 🚀 Streamlit interface
st.title("🌍 Live Spraakvertaler voor de Prediking")
st.markdown("🎙️ Spreek live via je microfoon. Vertaling wordt automatisch weergegeven en uitgesproken.")

webrtc_streamer(
    key="live-vertaler",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)
