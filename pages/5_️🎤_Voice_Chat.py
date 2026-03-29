import streamlit as st
import asyncio
from services.audio import record_audio, transcribe_audio, generate_gpt_response, speak_text
import helpers.sidebar

# UI Components
st.set_page_config(
    page_title="Voice Chat",
    page_icon="🎤",
    layout="wide"
)

helpers.sidebar.show()

st.header("Voice Chat")

st.write("Get instant answers to your software development and coding questions using the microphone.")


# Function to handle the audio recording, transcription, and response generation
async def handle_audio_interaction():
    with st.spinner('Recording...'):
        record_audio()

    with st.spinner('Transcribing audio...'):
        transcription = transcribe_audio()
        st.write(f"Transcription: {transcription}")

    with st.spinner('Generating response...'):
        response = generate_gpt_response(transcription)
        st.write(f"Response: {response}")

    # Speak the response
    speak_text(response)


if st.button("Record for 5 Seconds"):
    asyncio.run(handle_audio_interaction())
