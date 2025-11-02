import streamlit as st
from deep_translator import GoogleTranslator
import edge_tts
import asyncio
import tempfile
import speech_recognition as sr

st.title("🌍 Spraakvertaler voor Telefoon en PC")
st.markdown("🎙️ Neem een korte boodschap op, vertaal en beluister het resultaat.")

bron_taal = st.selectbox("Welke taal spreek je?", ["fr", "pt", "nl", "zh-CN", "ln", "en-US", "es", "de"])
doel_taal = st.selectbox("Welke taal wil je horen?", ["nl", "fr", "pt", "zh-CN", "ln", "en-US", "es", "de"])

audio_file = st.file_uploader("📎 Neem een audiofragment op (MP3 of WAV)", type=["mp3", "wav"])

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

if st.button("🔁 Vertaal en spreek"):
    if audio_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=audio_file.name[-4:]) as tmp:
            tmp.write(audio_file.read())
            tmp_path = tmp.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)

        try:
            zin = recognizer.recognize_google(audio, language=bron_taal)
            st.write(f"🗣️ Origineel: {zin}")
            vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
            st.write(f"🌐 Vertaling: {vertaling}")
            audiobestand = asyncio.run(spreek_tekst(vertaling, doel_taal))
            with open(audiobestand, "rb") as af:
                st.audio(af.read(), format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Fout bij verwerking: {e}")
    else:
        st.warning("📎 Upload eerst een audiobestand.")
