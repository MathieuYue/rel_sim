from openai import OpenAI
from pydantic import BaseModel

import os
from dotenv import load_dotenv

load_dotenv()

# openai_api_key = os.getenv("OPENAI_API_KEY")
lambda_api_key = os.getenv("LAMBDA_API_KEY")
openai_api_base = "https://api.lambda.ai/v1"

client = OpenAI(api_key=lambda_api_key, base_url=openai_api_base)

def model_call_structured(user_message, output_format):
    # print(user_message)
    completion = client.chat.completions.create(
        model="llama-4-maverick-17b-128e-instruct-fp8",
        messages=[
            {
                "role": "user", "content": user_message,
            }
        ],
        max_tokens=1500,
        temperature=0.7,
        response_format=output_format
    )
    return str(completion.choices[0].message.content)

def model_call_unstructured(system_message, user_message):
    completion = client.chat.completions.create(
        model="llama-4-maverick-17b-128e-instruct-fp8",
        messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    return str(completion.choices[0].message.content)
