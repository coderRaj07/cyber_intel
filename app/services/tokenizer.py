import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

MAX_TOKENS = 3000   # Safe chunk size for Cerebras llama-3.1-70b

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))