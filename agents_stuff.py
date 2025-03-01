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

def build_html_from_posts(posts: str, template: Optional[str] = None) -> str:
    """
    Build HTML content from social media posts.
    
    Args:
        posts (str): Social media posts to convert to HTML
        template (Optional[str]): Optional HTML template to use for formatting
        
    Returns:
        str: Generated HTML content
    """
    tweaks = {
        "TextInput-8fyZk": {"input_value": template} if template else {},
        "TextInput-qQTzX": {"input_value": posts} if posts else {},
        "ChatInput-tbWNG": {},
        "OpenAIModel-4zPqb": {},
        "ChatOutput-nSI1W": {},
        "CombineText-P2Nrl": {}
    }
    
    message = "You are a good html programmer. Given a piece of template, and the 3 social media posts. Replicate the html code and give it back. Only give html code and nothing else. Do not give explaination of the code. Also, if there are names, randomize the names to make it more personal."
    response = run_flow(
        message=message,
        endpoint="build-html",
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
