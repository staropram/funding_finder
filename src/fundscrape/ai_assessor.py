import os
import json
from openai import OpenAI
from pathlib import Path

# probably we need to abstract this at some point but lets keep this simple for now
# we are using deepseek because it's cheap
class AIAssessor:

    def get_response_to_query(self,ai_query):
        ai_message_list=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What is the capital of France?"},
        ]
        # do this with flash only
        response = client.chat.completions.create(
            model=self.ai_params["model"]
            messages=ai_message_list,
            stream=self.ai_params["stream"],
            reasoning_effort=self.ai_params["reasoning_effort"],
            extra_body=self.ai_params["extra_body"]
        )
        return response.choices[0].message.content


    def make_ai_summary_of_funding_detail(self):
        return None

    def make_ai_summary_of_funding_details(self):
        # iterate through
        return None


    def __init__(self,funding_details,ai_params_path,ai_prompts_path):
        self.fd = funding_details
        # load in the ai params
        with Path(ai_params_path).open(encoding="utf-8") as file:
            self.ai_params = json.load(file)

        with Path(ai_prompts_path).open(encoding="utf-8") as file:
            self.ai_prompts = json.load(file)

        api_key_path = Path("/home/ash/dsapi.txt")
        with api_key_path.open(encoding="utf-8") as file:
            api_key = file.read_text()

        self.ai_client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")


