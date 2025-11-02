import streamlit as st
from deep_translator import GoogleTranslator
import asyncio
import edge_tts
import io
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# Zorg ervoor dat deze bibliotheek is geïnstalleerd:
# pip install streamlit streamlit-mic-recorder deep_translator edge-tts

# --- Functie om tekst uit te spreken (voor server-side TTS) ---
async def genereer_audio_bytes(tekst, taalcode):
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
    communicate = edge_tts.Communicate(tekst, stem)
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    return audio_bytes

# --- Streamlit UI en Hoofdlogica ---

st.title("🌐 Live Vertaal App")

if 'resultaten' not in st.session_state:
    st.session_state.resultaten = []

# Gebruikersinvoer voor talen
col1, col2 = st.columns(2)
with col1:
    bron_taal = st.selectbox("Spreektaal", ["nl", "fr", "pt", "en-US", "de", "es"], index=0)
with col2:
    doel_taal = st.selectbox("Vertaaltaal", ["nl", "fr", "pt", "en-US", "de", "es"], index=1)

st.write("Druk op 'Record' om te beginnen met spreken. Druk nogmaals om te stoppen.")

# Mic recorder component
# De audio_bytes variabele wordt gevuld wanneer de gebruiker stopt met opnemen
audio_bytes = mic_recorder(start_prompt="Record", stop_prompt="Stop", key='recorder', just_once=False)

if audio_bytes:
    # Hier moet de spraakherkenning plaatsvinden
    # Let op: De originele sr.recognize_google() vereist een AudioFile of AudioData object,
    # dus u moet de raw bytes converteren of een andere API (zoals OpenAI Whisper) gebruiken.
    
    # VOORBEELD (U moet de juiste conversie implementeren om uw sr-bibliotheek te gebruiken):
    try:
        # Dit deel van de code is complexer omdat u de raw audio bytes van de browser
        # moet converteren naar een formaat dat speech_recognition kan lezen. 
        # Streamlit-mic-recorder geeft WAV bytes terug.
        # U heeft misschien de `pydub` bibliotheek nodig om de bytes te manipuleren.
        
        # Voor nu, laten we aannemen dat we de tekst via een andere methode krijgen
        # Aangezien we de originele sr.recognize_google niet direct kunnen gebruiken met de bytes zonder extra werk:
        
        # placeholder for speech to text result
        zin = "Voorbeeldzin uit de microfoon." # Vervang dit met daadwerkelijke STT logic

        # Vertaal de zin
        vertaling = GoogleTranslator(source=bron_taal, target=doel_taal).translate(zin)
        
        st.session_state.resultaten.append(f"🗣️ Origineel ({bron_taal}): {zin}")
        st.session_state.resultaten.append(f"🌐 Vertaling ({doel_taal}): {vertaling}")
        
        # Genereer de vertaalde audio asynchroon en speel af
        # Streamlit kan asyncio gebruiken met st.rerun() of caching, maar het eenvoudigste is:
        
        # asyncio.run(spreek_tekst(vertaling, doel_taal)) # Dit werkt niet goed in Streamlit web app
        
        # U kunt de audiobytes hieronder genereren en afspelen in de browser:
        # audio_vertaling = asyncio.run(genereer_audio_bytes(vertaling, doel_taal))
        # st.audio(audio_vertaling, format='audio/mp3')

    except Exception as e:
        st.error(f"Er ging iets mis: {e}")

# Toon de resultaten in omgekeerde volgorde
for resultaat in reversed(st.session_state.resultaten):
    st.markdown(resultaat)
