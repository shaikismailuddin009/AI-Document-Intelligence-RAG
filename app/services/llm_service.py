import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Lazily create the OpenAI client on first real use.

    Keeping this out of module import time means importing llm_service (or
    anything that imports it, like rag_service) never requires
    OPENAI_API_KEY to be set — only actually calling generate_answer does.
    That keeps unit tests and CI free of needing a real API key.
    """
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        _client = OpenAI(api_key=api_key)

    return _client


def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a helpful AI document assistant.

Answer the user's question using ONLY the provided document context.

If the answer cannot be found in the context, say:
"I could not find the answer in the provided document."

Do not make up information.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""

    client = _get_client()

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
    )

    return response.output_text
