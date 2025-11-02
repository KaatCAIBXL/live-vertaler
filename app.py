import streamlit as st
from deep_translator import GoogleTranslator
import speech_recognition as sr
import edge_tts
import asyncio
import tempfile
from datetime import datetime

# --------------------------
# 🎧 Tekst uitspreken via browser
# --------------------------

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

# --------------------------
# 🧠 Hoofdprogramma
# --------------------------

def start_luisteren(bron_taal, doel_taal):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    st.info("🎙️ Begin met spreken. Klik op 'Stop' om te eindigen.")
    resultaten = []

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        for _ in range(5):  # Luister 5 zinnen (of pas dit aan)
            st.write("⏳ Luisteren...")
            try:
                audio = recognizer.listen(source, phrase_time_limit=10)
                zin = recognizer.recognize_google(audio, language=bron_taal).strip()
                st.write(f"🗣️ Origineel ({bron_taal}): {zin}")

                try:
                    vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
                except Exception as e:
                    st.warning(f"⚠️ Vertaling mislukt: {e}")
                    vertaling = zin

                st.write(f"🌐 Vertaling ({doel_taal}): {vertaling}")

                audiobestand = asyncio.run(spreek_tekst(vertaling, doel_taal))
                with open(audiobestand, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")

                tijd = datetime.now().strftime("%H:%M:%S")
                resultaten.append(f"[{tijd}] Origineel: {zin}\n[{tijd}] Vertaling: {vertaling}\n")

            except sr.UnknownValueError:
                st.warning("⚠️ Niet verstaan. Probeer opnieuw.")
            except sr.RequestError as e:
                st.error(f"❌ Fout bij spraakherkenning: {e}")
                break

    if resultaten:
        with open("vertaling_resultaat.txt", "w", encoding="utf-8") as bestand:
            bestand.writelines(resultaten)
        st.success("✅ Vertaling voltooid. Resultaat opgeslagen.")

# --------------------------
# 🚀 Streamlit Interface
# --------------------------

st.title("🌍 Live Spraakvertaler voor de Prediking")

bron_taal = st.selectbox("Welke taal spreekt de pastoor?", ["fr", "pt", "nl", "zh-CN", "en-US", "es", "de"])
doel_taal = st.selectbox("Welke taal wil je horen?", ["nl", "fr", "pt", "zh-CN", "ln", "en-US", "es", "de"])

if st.button("🎧 Start live vertaling"):
    start_luisteren(bron_taal, doel_taal)
