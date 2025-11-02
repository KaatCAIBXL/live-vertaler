import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import tempfile
import av

# 🌍 Taalinstellingen
bron_taal = st.selectbox("Welke taal spreek je?", ["fr", "pt", "nl", "zh-CN", "ln", "en", "es", "de"])
doel_taal = st.selectbox("Welke taal wil je horen?", ["nl", "fr", "pt", "zh-CN", "ln", "en", "es", "de"])

# 🎧 Tekst uitspreken
async def spreek_tekst(tekst, taalcode):
    stemmap = {
        "nl": "nl-NL-MaartenNeural",
        "fr": "fr-FR-DeniseNeural",
        "pt": "pt-BR-AntonioNeural",
        "zh-CN": "zh-CN-XiaoxiaoNeural",
        "es": "es-ES-AlvaroNeural",
        "de": "de-DE-ConradNeural",
        "en": "en-US-AriaNeural",
        "ln": "pt-BR-AntonioNeural",
    }
    stem = stemmap.get(taalcode, "en-US-AriaNeural")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        await edge_tts.Communicate(tekst, stem).save(tmpfile.name)
        return tmpfile.name

# 🧠 Audioverwerker (simuleert zin, vervang later met echte herkenning via API)
class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        zin = "Bonjour tout le monde"  # ← vervang dit later met echte herkenning
        st.write(f"🗣️ Origineel: {zin}")
        vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
        st.write(f"🌐 Vertaling: {vertaling}")
        audiobestand = asyncio.run(spreek_tekst(vertaling, doel_taal))
        with open(audiobestand, "rb") as af:
            st.audio(af.read(), format="audio/mp3")
        return frame

# 🚀 Streamlit interface
st.title("🌍 Live Spraakvertaler voor Telefoon en PC")
st.markdown("🎙️ Spreek live via je microfoon. Vertaling verschijnt automatisch en wordt uitgesproken.")

webrtc_streamer(
    key="live-stream",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)
