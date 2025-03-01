from pathlib import Path
from openai import OpenAI
import os
import random
import json
import sounddevice as sd
from pprint import pprint
from dotenv import load_dotenv
from pydub import AudioSegment
import langflow_api
import numpy as np

# Load environment variables from a .env file
load_dotenv(dotenv_path=Path(__file__).parent / "ASTRA_OPENAI.env")


class PodcastTalk:
    def __init__(self,file='sample_podcast.json'):
        self.podcast = self.load_podcast(file)
        self.hosts = {}
        self.transcript = self.podcast["podcast"]["transcript"]
        self.client = OpenAI(api_key=os.getenv("ASTRA_OPENAI"))

    def load_podcast(self, file):
        try:
            with open(file, 'r') as f:
                podcast_data = json.load(f)
            return podcast_data
        except Exception as e:
            print(f"Error loading podcast file: {e}")
            return None

    def generate_hosts(self,transcript):
        voices = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]
        for content in transcript:
            if content["host"] not in self.hosts:
                randomizer = random.randint(len(voices))
                self.hosts[content["host"]] = voices[randomizer]
                voices.remove(voices[randomizer])

    def generate_podcast(self,input):
        try:
            print("Attempting to generate podcast...")
            print("Using langflow")
            transcript_output = langflow_api.run_flow(message=input)
            # Parse transcript
            # print(transcript_output)
            # self.podcast = json.load(transcript_output["outputs"]["text"])
            # self.transcript = self.podcast["podcast"]["transcript"]
            return transcript_output
        except Exception as e:
            print(f"Error generating podcast: {e}")

    def merge_clips(self,speech_files):
        sound = None
        for speech_file in speech_files:
            if not sound:
                sound = AudioSegment.from_file(speech_file,format="mp3")
            else:
                sound += AudioSegment.from_file(speech_file,format="mp3")
        sound.export("podcast.mp3", format="mp3")

    def generate_talk(self):
        count = 0
        speech_files = []
        for content in self.transcript:
            speech_file_path = Path(__file__).parent / f"speech-{count}.mp3"
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.hosts[content["host"]],
                input=content["content"],
            )
            response.stream_to_file(speech_file_path)
            speech_files.append(speech_file_path)
            count += 1

        return speech_files
    
    def stream_podcast(self):
        """Streams text-to-speech audio and plays it in real-time using sounddevice."""
        try:
            for content in self.transcript:
                with self.client.audio.speech.with_streaming_response.create(
                    model="tts-1",
                    voice=self.hosts[content["host"]],
                    response_format="pcm",
                    input=content["content"],
                ) as response:
                    audio_data = b''.join(response.iter_bytes())
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    sd.play(audio_array, samplerate=24000)
                    sd.wait()
        except Exception as e:
            print(f"Error during streaming or playback: {e}")


podcast = PodcastTalk()
<<<<<<< HEAD
print(podcast.generate_podcast("rightwing-happy-memes"))
=======
print(podcast.generate_podcast("leftwing-sad-sports"))
>>>>>>> bc67803 (Langflow api call and podcast generator)
