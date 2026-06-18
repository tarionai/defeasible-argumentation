"""Boundary adapters that make the vendor SDKs satisfy `LlmClient`.

Each imports its SDK lazily inside `__init__`, so this module imports cleanly
with neither `anthropic` nor `openai` installed. Install them with the `[llm]`
extra and set the corresponding API key only when you actually want to run the
population pipeline; the build and test path never construct these.
"""

from __future__ import annotations


class AnthropicClient:
    """`LlmClient` over the Anthropic Messages API."""

    def __init__(self, model_name: str = "claude-opus-4-8", *, max_tokens: int = 2048,
                 api_key: str | None = None) -> None:
        import anthropic

        self.model_name = model_name
        self._max_tokens = max_tokens
        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self.model_name,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content
                       if getattr(block, "type", None) == "text")


class OpenAIClient:
    """`LlmClient` over the OpenAI Chat Completions API (the independent
    cross-check model)."""

    def __init__(self, model_name: str = "gpt-4o", *, api_key: str | None = None) -> None:
        import openai

        self.model_name = model_name
        self._client = openai.OpenAI(api_key=api_key)

    def complete(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
