from openai import OpenAI
from pydantic import BaseModel

import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = "https://api.lambda.ai/v1"

client = OpenAI(api_key=openai_api_key)

model = "gpt-4o-mini"

def model_call_structured(system_message, user_message, text_format=None):

    response = client.responses.parse(
        model=model,
        input=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ],
        text_format=text_format
    )
    return response.output_parsed
    
def model_call_unstructured(system_message, user_message):
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    return response.output
