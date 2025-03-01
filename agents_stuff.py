import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
from dotenv import load_dotenv
import os

MESSAGE='based upon the personality data given, create 3 personas that this user would like to interact with. Then use the News data and use it to create some social media posts. Create one post each. These posts will be used by other AI agents. Only provide posts, do not provide any other text including the personas'


load_dotenv()

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "http://127.0.0.1:7860"
FLOW_ID = "0d44668a-cfe2-4dcb-b59e-58f6e7217037"
ENDPOINT = "post-gen" # The endpoint name of the flow

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "TextInput-8a4Ef": {"input_value": "# News Data Entertainment News:1. Robert Morse, star of Mad Men and Broadway, dies aged 90 - The GuardianSource: The GuardianDescription: The actor is best known for playing Bert Cooper in the hit drama, and twice won Tony awards for stage roles2. Queen Elizabeth celebrates 96th birthday in milestone jubilee year - CNNSource: CNNDescription: Britain's Queen Elizabeth II celebrated her 96th birthday on Thursday, in the same year thatmarks her 70 years on the throne.3. Prince Harry Dodging Question About Missing Prince William & Charles Sparks Royal Rift Debate | GMB - Good Morning BritainSource: YouTubeDescription: Prince Harry has avoided answering a question on whether he misses his brother Prince William and father Prince Charles -instead saying his focus is on the I...4. Johnny Depp trial – live: Actor describes Amber Heard fights, horrific finger injury and faeces on bed- The IndependentSource: IndependentDescription: Johnny Depp - Amber Heard trial5. A$AP Rocky arrested in connection with shooting - BBC.comSource: BBC NewsDescription: The rapper was taken into custody at Los Angeles airport as he returned from a holiday with Rihanna.General News:1. Russia-Ukraine War Live News: Mariupol, Putin and the Latest Updates - The New York TimesSource: New York TimesDescription: Vladimir Putin said it was "impractical" to attack the plant where Ukrainian forces were holding out, and offered them another chance to surrender. As he claimed success in Mariupol, where Russia suffered heavy losses, his forces pushed an offensive in easter…2. FAA to review as parachute stunt triggers Capitol evacuation - WTOPSource: WTOPDescription: he Federal Aviation Administration says it's reviewing an apparent communications breakdown that led police to think an aircraft carrying military parachutists for a baseball stadium stunt was "a probable threat," prompting an alert and urgent evacuation of t…3. Queen Elizabeth celebrates 96th birthday in milestone jubilee year - CNNSource: CNNDescription: Britain's Queen Elizabeth II celebrated her 96th birthday on Thursday, in the same year thatmarks her 70 years on the throne.4. American forecasts second-quarter profit on soaring travel demand, stock surges 10% - CNBCSource: CNBCDescription: American expects to fly as much as 94% of its 2019 schedule, more than competitors Delta AirLines and United Airlines.5. Eagles News: Deebo Samuel trade proposal - Bleeding Green NationSource: Bleeding Green NationDescription: Philadelphia Eagles news and links for 4/21/22."},
  "TextInput-PfHai": {"input_value": "# personality data happy: 3/10tired: 7/10 left-leaning: 3/10relationship: single"},
  "CombineText-BBJix": {},
  "OpenAIModel-wvwF1": {},
  "TextInput-Q2T03": {},
  "ChatInput-SjChs": {},
  "ChatOutput-oAMDi": {}
}

def run_flow(message: str,
  endpoint: str = ENDPOINT,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def generate_social_posts(news_data: str, personality_data: str) -> str:
    """
    Generate social media posts based on news and personality data.
    
    Args:
        news_data (str): News data in formatted string
        personality_data (str): Personality traits in formatted string
        
    Returns:
        str: Generated social media posts
    """
    tweaks = {
        "TextInput-8a4Ef": {"input_value": news_data},
        "TextInput-PfHai": {"input_value": personality_data},
        "CombineText-BBJix": {},
        "OpenAIModel-wvwF1": {},
        "TextInput-Q2T03": {},
        "ChatInput-SjChs": {},
        "ChatOutput-oAMDi": {}
    }
    
    response = run_flow(
        message=MESSAGE,
        endpoint=ENDPOINT,
        tweaks=tweaks
    )
    
    return response['outputs'][0]['outputs'][0]['results']['message']['data']['text']

def main():
    parser = argparse.ArgumentParser(description="""Run a flow with a given message and optional tweaks.
Run it like: python <your file>.py "your message here" --endpoint "your_endpoint" --tweaks '{"key": "value"}'""",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("--endpoint", type=str, default=ENDPOINT or FLOW_ID, help="The ID or the endpoint name of the flow")
    parser.add_argument("--tweaks", type=str, help="JSON string representing the tweaks to customize the flow", default=json.dumps(TWEAKS))
    parser.add_argument("--api_key", type=str, help="API key for authentication", default=None)
    parser.add_argument("--output_type", type=str, default="chat", help="The output type")
    parser.add_argument("--input_type", type=str, default="chat", help="The input type")
    parser.add_argument("--upload_file", type=str, help="Path to the file to upload", default=None)
    parser.add_argument("--components", type=str, help="Components to upload the file to", default=None)

    args = parser.parse_args()
    try:
      tweaks = json.loads(args.tweaks)
    except json.JSONDecodeError:
      raise ValueError("Invalid tweaks JSON string")

    if args.upload_file:
        if not upload_file:
            raise ImportError("Langflow is not installed. Please install it to use the upload_file function.")
        elif not args.components:
            raise ValueError("You need to provide the components to upload the file to.")
        tweaks = upload_file(file_path=args.upload_file, host=BASE_API_URL, flow_id=args.endpoint, components=[args.components], tweaks=tweaks)

    response = run_flow(
        message=MESSAGE,
        tweaks=TWEAKS
    )

    print(response['outputs'][0]['outputs'][0]['results']['message']['data']['text'])

if __name__ == "__main__":
    main()
