import streamlit as st
from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import tempfile

st.title("🌍 Spraakvertaler voor Telefoon en PC")
st.markdown("🎙️ Neem een korte boodschap op, upload het bestand, en hoor de vertaling.")

bron_taal = st.selectbox("Welke taal spreek je?", ["fr", "pt", "nl", "zh-CN", "ln", "en", "es", "de"])
doel_taal = st.selectbox("Welke taal wil je horen?", ["nl", "fr", "pt", "zh-CN", "ln", "en", "es", "de"])

audio_file = st.file_uploader("📎 Upload een audiobestand (MP3 of WAV)", type=["mp3", "wav"])

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

if audio_file is not None:
    st.audio(audio_file, format="audio/mp3")
    st.markdown("🧠 Herkenning en vertaling volgt...")

    # Simulatie van herkenning (jij vult dit aan met echte tekst)
    zin = "Bonjour tout le monde"  # ← vervang dit met echte herkenning als je wil
    st.write(f"🗣️ Origineel: {zin}")
    vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
    st.write(f"🌐 Vertaling: {vertaling}")
    audiobestand = asyncio.run(spreek_tekst(vertaling, doel_taal))
    with open(audiobestand, "rb") as af:
        st.audio(af.read(), format="audio/mp3")
