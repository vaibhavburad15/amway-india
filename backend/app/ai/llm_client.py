"""
Groq LLM client wrapper.
Uses Llama 3.3 70B for high-quality responses.
"""
from groq import Groq
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.startswith("gsk_your"):
            logger.warning("⚠️  GROQ_API_KEY not configured. AI features will return mock responses.")
            self.client = None
        else:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def chat(self, system_prompt: str, user_message: str, temperature: float = 0.4) -> str:
        if self.client is None:
            return self._mock_response(user_message)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "I'm temporarily unable to process this request. Please try again later."

    def _mock_response(self, msg: str) -> str:
        return (
            "🤖 [Mock AI Response — Configure GROQ_API_KEY in .env for real AI]\n\n"
            f"You asked: '{msg[:80]}...'\n\n"
            "In production, I would analyze your query using Llama 3.3 and our supplement knowledge base "
            "to provide an evidence-based, personalized response.\n\n"
            "⚠️ Always consult a healthcare professional for medical advice."
        )


llm_client = LLMClient()
