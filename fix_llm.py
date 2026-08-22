content = """import os
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq

load_dotenv(find_dotenv(), override=True)

MODEL_NAME = "qwen/qwen3.6-27b"

_llm = None


def get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file.")
        _llm = ChatGroq(
            model=MODEL_NAME,
            api_key=api_key,
            temperature=0.1,
            max_tokens=4096
        )
        print(f"LLM connected: {MODEL_NAME} via Groq")
    return _llm
"""

with open("backend/core/rag/llm.py", "w", encoding="utf-8") as f:
    f.write(content)
print("llm.py fixed successfully")

# Verify line 32 area
lines = open("backend/core/rag/llm.py").readlines()
print("Total lines: " + str(len(lines)))
for i, l in enumerate(lines, 1):
    print(str(i) + ": " + l.rstrip())
