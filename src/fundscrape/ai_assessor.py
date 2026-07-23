import os
import json
from openai import OpenAI
from pathlib import Path
from hashlib import sha256
from urllib.parse import urlparse
from pathlib import PurePosixPath

# probably we need to abstract this at some point but lets keep this simple for now
# we are using deepseek because it's cheap
class AIAssessor:

    def get_response_to_query(self,message_list):
        # send the request
        response = self.ai_client.chat.completions.create(
            model=self.ai_params["model"],
            messages=message_list,
            stream=(self.ai_params["stream"]=="True"),
            reasoning_effort=self.ai_params["reasoning_effort"],
            extra_body=self.ai_params["extra_body"]
        )
        return response.choices[0].message.content


    def make_ai_summary_of_funding_detail_page(self,funding_details,force_reload=False):
        funding_id = PurePosixPath(urlparse(funding_details.funding_card.link).path).name
        cached_fn = Path(f"data/cache/{funding_id}_ai_summary.json")

        if not force_reload and cached_fn.exists():
            with cached_fn.open(encoding="utf-8") as file:
                return json.load(file)

        # construct the message list
        summary_prompt = self.ai_prompts["summary_prompt"].replace("FUNDING_DETAILS",str(funding_details))
        ai_message_list=[
            {"role": "system", "content": self.ai_prompts["system_prompt"]},
            {"role": "user", "content": summary_prompt},
        ]
        ai_response = self.get_response_to_query(ai_message_list)

        response_json = {
            "card_details" : str(funding_details.funding_card),
            "response" : ai_response
        }

        with cached_fn.open("w",encoding="utf-8") as file:
            json.dump(response_json,file)

        return response_json

    def make_ai_summary_of_funding_detail_pages(self):
        # test
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
        api_key = api_key_path.read_text()

        self.ai_client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")


