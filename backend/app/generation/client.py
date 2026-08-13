import os

from google import genai


class GeminiClient:

    def __init__(
        self,
        model: str = "gemini-3.1-flash-lite",
    ) -> None:

        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self._client = genai.Client(
            api_key=api_key
        )

        self._model = model

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text