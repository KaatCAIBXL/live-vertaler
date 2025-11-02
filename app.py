import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import tempfile
import platform

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

# 🧠 Audioverwerker voor gsm (lichte simulatie)
class LightAudioProcessor(AudioProcessorBase):
    def recv(self, frame):
        zin = "Bonjour tout le monde"  # Simulatie of vervang met API-herkenning
        st.write(f"🗣️ Origineel: {zin}")
        vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
        st.write(f"🌐 Vertaling: {vertaling}")
        audiobestand = asyncio.run(spreek_tekst(vertaling, doel_taal))
        with open(audiobestand, "rb") as af:
            st.audio(af.read(), format="audio/mp3")
        return frame

# 🧠 Audioverwerker voor pc (Whisper)
class WhisperAudioProcessor(AudioProcessorBase):
    def __init__(self):
        import whisper
        self.model = whisper.load_model("base")
        self.buffer = b""

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.buffer += audio.tobytes()

        if len(self.buffer) > 16000 * 5:
            import numpy as np
            import soundfile as sf
            import io

            audio_array = np.frombuffer(self.buffer, dtype=np.int16).astype(np.float32) / 32768.0
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                sf.write(tmp.name, audio_array, 16000)
                result = self.model.transcribe(tmp.name, language=bron_taal)
                zin = result["text"]
                st.write(f"🗣️ Origineel: {zin}")
                vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
                st.write(f"🌐 Vertaling: {vertaling}")
                audiobestand = asyncio.run(spreek_tekst(vertaling, doel_taal))
                with open(audiobestand, "rb") as af:
                    st.audio(af.read(), format="audio/mp3")
            self.buffer = b""
        return frame

# 🚀 Streamlit interface
st.title("🌍 Hybride Live Spraakvertaler")
st.markdown("🎙️ Spreek live via je microfoon. De app kiest automatisch tussen lichte of krachtige herkenning.")

# 🔍 Detectie: pc of gsm
is_pc = platform.system() in ["Windows", "Darwin", "Linux"]

if is_pc:
    st.success("🖥️ PC gedetecteerd: Whisper wordt gebruikt voor herkenning.")
    webrtc_streamer(
        key="pc-stream",
        audio_processor_factory=WhisperAudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )
else:
    st.info("📱 Mobiel apparaat gedetecteerd: lichte herkenning wordt gebruikt.")
    webrtc_streamer(
        key="gsm-stream",
        audio_processor_factory=LightAudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )

