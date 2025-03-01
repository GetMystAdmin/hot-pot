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
import time

# Load environment variables from a .env file
load_dotenv(dotenv_path=Path(__file__).parent / "ASTRA_OPENAI.env")
PODCASTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'podcasts')
os.makedirs(PODCASTS_DIR, exist_ok=True)

class PodcastTalk:
    def __init__(self,file='sample_podcast.json'):
        self.podcast = self.load_podcast(file)
        self.hosts = {}
        self.title = self.podcast["podcast"]["title"]
        self.transcript = self.podcast["podcast"]["transcript"]
        self.client = OpenAI(api_key=os.getenv("ASTRA_OPENAI"))
        self.audio_array = None

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
                randomizer = random.randint(0, len(voices) - 1)
                self.hosts[content["host"]] = voices[randomizer]
                voices.remove(voices[randomizer])
        print(self.hosts)

    def generate_podcast(self,input):
        try:
            print("Attempting to generate podcast...")
            start_time = time.time()
            # Your code here
            print("Using langflow")
            transcript_output = langflow_api.run_flow(message=input)
            end_time = time.time()
            print(f"Time taken to generate podcast: {end_time - start_time} seconds")
            print("Processing podcast metadata")
            output = transcript_output["outputs"][0]["outputs"][0]['results']['message']['data']['text'].replace("```json", "").replace("```", "")
            self.podcast = json.loads(output)
            print("Getting podcast title")
            self.title = self.podcast["podcast"]["title"]
            print(f"{self.title}")
            print("Generating hosts")
            self.generate_hosts(self.podcast["podcast"]["transcript"])
            print(f"{self.hosts}")
            print("Getting transcript")
            self.transcript = self.podcast["podcast"]["transcript"]
            return transcript_output
        except Exception as e:
            print(f"Error generating podcast: {e}")
            with open('test.json', 'w') as f:
                f.write(json.dumps(transcript_output, indent=4))
            end_time = time.time()
            print(f"Exception caught. Time taken to generate podcast: {end_time - start_time} seconds")
            return None

    def merge_clips(self,speech_files):
        sound = None
        for speech_file in speech_files:
            if not sound:
                sound = AudioSegment.from_file(speech_file,format="mp3")
            else:
                sound += AudioSegment.from_file(speech_file,format="mp3")
        sound.export(os.path.join(PODCASTS_DIR,f"Echo Chamber {random.randint(0,999)}.mp3"), format="mp3")

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
            print("Running stream")
            print(self.transcript)
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

if __name__ == "__main__":
    podcast = PodcastTalk()
    output = podcast.generate_podcast("rightwing-happy-memes")
    if output:
        podcast.stream_podcast()
