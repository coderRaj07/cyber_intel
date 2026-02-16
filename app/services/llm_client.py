from cerebras.cloud.sdk import Cerebras
from app.config import CEREBRAS_API_KEY, CEREBRAS_MODEL

client = Cerebras(api_key=CEREBRAS_API_KEY)


def call_cerebras(prompt: str) -> str:

    response = client.chat.completions.create(
        model=CEREBRAS_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a strict economic data extraction engine."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.0
    )

    return response.choices[0].message.content