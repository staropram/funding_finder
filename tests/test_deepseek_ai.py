import os
from openai import OpenAI
from pathlib import Path

def test_deepseek_api():
    api_key_path = Path("/home/ash/dsapi.txt")
    api_key = api_key_path.read_text()
    client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")

    # do this with flash only
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What is the capital of France?"},
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "disabled"}}
    )

    response_text = response.choices[0].message.content
    print(response_text)
    
    assert "Paris" in response_text

if __name__ == "__main__":
    test_deepseek_api()