import pyaudio
import wave
import os
import logging
import speech_recognition as sr
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("poc_speech.log"),
        logging.StreamHandler(),
    ],
)


def record_audio(
    rate: int = 16000,
    chunk: int = 1024,
    channels: int = 1,
    format: int = pyaudio.paInt16,
    seconds: int = 5,
    output_filename: str = "input.wav",
) -> None:
    """
    Record audio from the microphone and save it to a file.

    Args:
        - rate (int): Sampling rate in Hz
        - chunk (int): Buffer size in samples
        - channels (int): Number of audio channels
        - format (int): Audio format
        - seconds (int): Duration of recording in seconds
        - output_filename (str): Output file path to save the recorded audio
    """
    audio = pyaudio.PyAudio()

    # Open the stream
    stream = audio.open(
        format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk
    )
    logging.info({"message": "Recording audio..."})

    frames = []

    # Record the audio in chunks
    for _ in range(0, int(rate / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a file
    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))

    logging.info({"message": "Audio recording complete."})


def detect_speech(rate: int = 16000, chunk: int = 1024, energy_threshold: int = 300) -> bool:
    """
    Detects speech using Voice Activity Detection (VAD) from the speech_recognition library.

    Args:
        - rate (int): Sampling rate in Hz
        - chunk (int): Buffer size in samples
        - energy_threshold (int): Minimum energy level for considering a sound as speech

    Returns:
        - bool: True if speech is detected, False otherwise
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = energy_threshold

    # Use the default microphone as the audio source
    with sr.Microphone(sample_rate=rate, chunk_size=chunk) as source:
        logging.info({"message": "Adjusting for ambient noise. Please wait."})
        recognizer.adjust_for_ambient_noise(
            source
        )  # Adjust sensitivity to ambient noise

        logging.info({"message": "Listening for speech..."})
        try:
            # Listen for speech; this will raise a `WaitTimeoutError` if no speech is detected within the timeout
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=2)
            logging.info({"message": "Speech detected, starting recording..."})
            return True

        except sr.WaitTimeoutError:
            logging.info("No speech detected within the timeout period.")
            return False
        except Exception as e:
            logging.error(
                {
                    "message": "An error occurred during speech detection",
                    "error": str(e),
                }
            )
            return False


def transcribe_audio(output_filename: str = "input.wav") -> str:
    """
    Transcribe audio using OpenAI's Speech-to-Text API.

    Args:
        - output_filename (str): Path to the audio file to transcribe

    Returns:
        - transcription (str): Transcribed text from the audio file
    """
    logging.info({"message": "Transcribing audio..."})

    with open(output_filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
    return transcription.text


def generate_response(prompt: str = "Good job.") -> str:
    """
    Generate a response using OpenAI's GPT model.

    Args:
        - prompt (str): Input prompt to generate a response

    Returns:
        - response (str): Generated response to the prompt
    """
    logging.info({"message": "Generating response for prompt", "prompt": prompt})

    content = f"""
    Make a concise response to the following prompt:
    {prompt}
    """

    response = client.chat.completions.create(
        model="gpt-4",  # Use your preferred model
        messages=[{"role": "user", "content": content}],
    )
    return response.choices[0].message.content


def text_to_speech(text: Optional[str] = None) -> Path:
    """
    Convert text to speech using OpenAI's Text-to-Speech API.

    Args:
        - text (str): Input text to convert to speech

    Returns:
        - speech_file_path (Path): Path to the generated speech
    """
    logging.info({"message": "Converting text to speech...", "text": text})

    # Define the output file path for the TTS result
    speech_file_path = Path(__file__).parent / "output_speech.mp3"

    # Create a speech response using OpenAI's TTS model
    response = client.audio.speech.create(
        model="tts-1", voice="alloy", input=text  # Replace with preferred voice
    )

    # Stream the generated speech to an output file
    response.stream_to_file(speech_file_path)

    logging.info({"message": "Audio response saved as", "file_path": speech_file_path})
    return speech_file_path


def play_audio(file_path: Optional[str] = None) -> None:
    """
    Play audio file using pydub.

    Args:
        - file_path (str): Path to the audio file to play
    """
    logging.info({"message": "Playing audio from file", "file_path": file_path})

    # Load the audio file
    audio = AudioSegment.from_file(file_path)

    # Play the audio
    play(audio)


if __name__ == "__main__":
    openai_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_key)

    # Audio recording parameters
    # TODO: off-load to config file
    format = pyaudio.paInt16  # Audio format
    channels = 1  # Mono audio
    rate = 16000  # Sampling rate
    chunk = 1024  # Buffer size
    record_seconds = 5
    output_filename = "input.wav"

    while True:
        if detect_speech(rate=rate, chunk=chunk):
            # Step 1: Record audio
            record_audio(
                rate=rate,
                chunk=chunk,
                channels=channels,
                format=format,
                seconds=record_seconds,
                output_filename=output_filename,
            )

            # Step 2: Transcribe the audio to text
            transcribed_text = transcribe_audio(output_filename=output_filename)
            logging.info({"message": "Transcribed text", "text": transcribed_text})

            # Step 3: Generate response from GPT model
            response_text = generate_response(prompt=transcribed_text)
            logging.info({"message": "Generated response", "response": response_text})

            # Step 4: Convert response text to speech
            speech_file_path = text_to_speech(text=response_text)

            # Step 5: Play the generated speech audio
            play_audio(file_path=str(speech_file_path))
