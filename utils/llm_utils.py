from openai import OpenAI
from pydantic import BaseModel

import os
from dotenv import load_dotenv

load_dotenv()

lambda_api_key = os.getenv("LAMBDA_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = "https://api.lambda.ai/v1"

client = OpenAI(api_key=lambda_api_key, base_url=openai_api_base)

def model_call_structured(user_message, output_format, model = "llama3.1-8b-instruct"):
    # print(user_message)
    completion = client.chat.completions.create(
        model= model,
        messages=[
            {
                "role": "user", "content": user_message
            }
        ],
        max_tokens=1500,
        temperature=0.7,
        response_format=output_format
    )
    return str(completion.choices[0].message.content)

def model_call_unstructured(system_message, user_message, model = "llama3.1-8b-instruct"):
    completion = client.chat.completions.create(
        model= model,
        messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    return str(completion.choices[0].message.content)

def get_text_embedding(text, model="text-embedding-3-small"):
    print(openai_api_key)
    client = OpenAI(api_key=openai_api_key)
    response = client.embeddings.create(
    input=text,
    model=model
)
    embedding = response.data[0].embedding
    return embedding

import json, re

def _strip_code_fences(s: str) -> str:
    # If the model put the JSON in ```json ... ``` fences, grab the inside
    m = re.search(r"```(?:json5?|javascript|js)?\s*([\s\S]*?)```", s, re.I)
    return m.group(1).strip() if m else s

def _extract_first_json_block(s: str) -> str:
    # Trim to the first {...} or [...]
    i = min([x for x in [s.find('{'), s.find('[')] if x != -1] or [0])
    s = s[i:]
    # Walk and stop after the matching close (even if later text exists)
    stack = []
    in_str = False
    esc = False
    quote = ''
    for idx, ch in enumerate(s):
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                in_str = False
        else:
            if ch in ('"', "'"):
                in_str = True; quote = ch
            elif ch in '{[':
                stack.append(ch)
            elif ch in '}]':
                if not stack: break
                top = stack.pop()
                if (top, ch) not in {('{','}'), ('[',']')}:
                    # mismatched, stop
                    break
                if not stack:
                    return s[:idx+1]
    # If we get here, it's truncated: return what we have
    return s

def _remove_comments_and_trailing_commas(s: str) -> str:
    # Remove //... and /* ... */ comments
    s = re.sub(r"//[^\n\r]*", "", s)
    s = re.sub(r"/\*[\s\S]*?\*/", "", s)
    # Remove trailing commas before } or ]
    s = re.sub(r",\s*(?=[}\]])", "", s)
    return s

def _fix_numbers_and_bools(s: str) -> str:
    # JSON5 tokens → JSON
    s = re.sub(r"\bNaN\b", "null", s)
    s = re.sub(r"\bInfinity\b", "null", s)
    s = re.sub(r"\b- Infinity\b", "null", s)
    # Allow unquoted object keys by quoting them (best-effort, safe-ish)
    s = re.sub(r'([{\s,])([A-Za-z_][A-Za-z0-9_\-]*)(\s*):', r'\1"\2"\3:', s)
    return s

def _autoclose_brackets(s: str) -> str:
    # Append missing closing ] or } if truncated
    stack = []
    in_str = False; esc = False; quote = ''
    for ch in s:
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == quote: in_str = False
        else:
            if ch in ('"', "'"): in_str = True; quote = ch
            elif ch in '{[': stack.append(ch)
            elif ch in '}]' and stack:
                top = stack[-1]
                if (top == '{' and ch == '}') or (top == '[' and ch == ']'):
                    stack.pop()
    closing = ''.join('}' if ch=='{' else ']' for ch in reversed(stack))
    return s + closing

def parse_model_json(text: str):
    raw = _strip_code_fences(text)
    raw = _extract_first_json_block(raw)
    cleaned = _remove_comments_and_trailing_commas(raw)
    cleaned = _fix_numbers_and_bools(cleaned)
    cleaned = _autoclose_brackets(cleaned)
    # Try strict JSON first
    try:
        return json.loads(cleaned)
    except Exception:
        # Try json5 if available
        try:
            import json5
            return json5.loads(raw)  # try original first
        except Exception:
            try:
                import json5
                return json5.loads(cleaned)
            except Exception as e2:
                # Last resort: attempt a gentle single-quote → double-quote within strings only
                sq = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', cleaned)
                return json.loads(sq)

# Example:
# data = parse_model_json(model_output_text)
