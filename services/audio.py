import os
import threading
import time
import wave
import pyaudio
import pygame
from gtts import gTTS
from openai import OpenAI
from services import llm
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize the OpenAI client with the modern API pattern

openai_model = os.getenv('OPENAI_API_MODEL')
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE_URL', 'http://aitools.cs.vt.edu:7860/openai/v1')
)

# Initialize pygame speech mixer with explicit parameters for robustness
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)


# Set up audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper supports 16kHz for best results
CHUNK = 1024
RECORD_SECONDS = 5  # Adjust as needed
WAVE_OUTPUT_FILENAME = "data/audio/voice_chat.wav"
AUDIO_RESPONSE_FILENAME = "data/audio/speech_output.mp3"


def record_audio():
    audio = pyaudio.PyAudio()

    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Finished recording.")

    # Stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data as a WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def transcribe_audio():
    model = "whisper-1"

    # Transcribe the audio file
    current_directory = os.getcwd()
    audio_file_path = os.path.join(current_directory, WAVE_OUTPUT_FILENAME)
    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    print(transcription.text)
    return transcription.text


def generate_gpt_response(prompt, messages: list[dict] = None):
    if messages is None:
        messages = []
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        messages=messages,
        model=openai_model,
        max_tokens=3000,
        temperature=0).choices[0].message.content

    # Uncomment the following lines if you want to add the response to the messages list
    # messages.append({"role": "assistant", "content": response})

    return response


def speak_text(text, lang="en"):
    """
    Convert text to speech using gTTS and play the audio file using pygame.

    Args:
        text (str): The text to be spoken.
        lang (str): Language for speech (default is "en" for English).
    """

    project_dir = os.path.dirname(os.path.dirname(__file__))
    temp_dir = os.path.join(project_dir, "data/audio")

    def _cleanup_temp_files(temp_dir):
        """Remove all audio files in the temp directory."""
        for filename in os.listdir(temp_dir):
            if filename.endswith(".mp3"):
                try:
                    os.remove(os.path.join(temp_dir, filename))
                    print(f"Removed old audio file: {filename}")
                except Exception as e:
                    print(f"Error removing file {filename}: {e}")

    _cleanup_temp_files(temp_dir)

    def _speak():
        os.makedirs(temp_dir, exist_ok=True)

        try:
            print("Converting text to speech...")
            tts = gTTS(text=text, lang=lang)

            # Create a unique filename based on the current time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file_name = f"speech_output_{timestamp}.mp3"
            audio_file_path = os.path.join(temp_dir, audio_file_name)

            print("Saving audio file...")
            tts.save(audio_file_path)
            print(f"Saved audio file: {audio_file_path}")

            # Load and play the speech using pygame
            print("Loading audio file...")
            pygame.mixer.music.load(audio_file_path)
            print("Playing audio...")
            pygame.mixer.music.play()

            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            print("Audio finished playing.")

            # Wait a moment to ensure it's fully released
            time.sleep(3)

        except Exception as e:
            print(f"Error in speak_text: {e}")

    # Run the speech process in a separate thread to prevent blocking
    thread = threading.Thread(target=_speak)
    thread.daemon = True
    thread.start()

