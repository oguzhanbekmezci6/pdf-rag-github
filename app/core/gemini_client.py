from google import genai
from google.genai import types

from app.config import Settings


class GeminiGenerationError(RuntimeError):
    """Raised when Gemini cannot produce a usable response."""


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = (
            genai.Client(api_key=settings.gemini_api_key)
            if settings.gemini_api_key
            else None
        )

    @property
    def is_configured(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str) -> str:
        if self.client is None:
            return (
                "Gemini API anahtarı eklenmedi. Sistem ilgili kaynakları buldu; "
                "aşağıdaki kaynak bölümlerini doğrudan inceleyebilirsin."
            )

        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=900,
                ),
            )
        except Exception as exc:  # SDK error types can vary between releases.
            message = str(exc)
            normalized = message.lower()
            if "401" in normalized or "unauthenticated" in normalized:
                raise GeminiGenerationError(
                    "Gemini kimlik doğrulaması başarısız. Google AI Studio'dan alınmış "
                    "geçerli bir GEMINI_API_KEY kullan ve uygulamayı yeniden başlat."
                ) from exc
            if "429" in normalized or "resource_exhausted" in normalized:
                raise GeminiGenerationError(
                    "Gemini kullanım limiti aşıldı. Bir süre bekleyip tekrar dene."
                ) from exc
            raise GeminiGenerationError("Gemini isteği tamamlanamadı.") from exc

        text = (response.text or "").strip()
        if not text:
            raise GeminiGenerationError("Gemini boş cevap döndürdü.")
        return text
