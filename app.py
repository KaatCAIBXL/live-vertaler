import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av

# 🧠 Dummy audioverwerker (nodig om webrtc te laten werken)
class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Hier kun je later spraakherkenning toevoegen
        return frame

# 🚀 Streamlit interface
st.title("🌍 Live Spraakvertaler voor de Prediking")

st.markdown("🎙️ Klik hieronder om live te spreken via je microfoon:")

webrtc_ctx = webrtc_streamer(
    key="live-vertaler",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

if webrtc_ctx.audio_receiver:
    st.success("✅ Microfoon werkt! Je spreekt live.")
else:
    st.info("ℹ️ Wacht op microfoonverbinding...")
