from typing import List
from src.config import settings
from src.models.query import SearchResultItem


class LLMService:
    """Manages grounded response synthesis from retrieved document context."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_key = settings.OPENAI_API_KEY

    def synthesize_answer(self, question: str, contexts: List[SearchResultItem]) -> str:
        """Synthesize a factual, grounded answer using retrieved contexts."""
        if not contexts:
            return "Informasi yang diminta tidak ditemukan dalam dokumen pengetahuan sistem."

        if self.provider == "mock" or not self.api_key:
            # Deterministic, grounded mock answer for offline development and tests
            titles = list(dict.fromkeys([c.title for c in contexts]))
            top_snippet = contexts[0].snippet[:180] + "..." if len(contexts[0].snippet) > 180 else contexts[0].snippet
            return (
                f"Berdasarkan dokumen resmi yang tersedia ({', '.join(titles)}): "
                f"{top_snippet}"
            )

        # Real LLM call via OpenAI or Gemini (OpenAI compatibility)
        try:
            import random
            from openai import OpenAI
            
            # Rotate API keys randomly per request to avoid free-tier rate limits
            active_key = random.choice(settings.api_keys_list) if settings.api_keys_list else self.api_key
            
            kwargs = {"api_key": active_key}
            if self.provider == "gemini":
                kwargs["base_url"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
                
            client = OpenAI(**kwargs)
            
            context_block = "\n\n".join(
                [f"[{i+1}] Dokumen: {c.title} (ID: {c.external_id})\n{c.snippet}" for i, c in enumerate(contexts)]
            )
            
            system_prompt = (
                "Anda adalah asisten AI resmi yang menjawab secara faktual dan tepat hanya berdasarkan konteks dokumen yang diberikan. "
                "Jika informasi tidak terdapat dalam konteks, jawab dengan jujur bahwa informasi tidak ditemukan."
            )
            
            user_prompt = f"Konteks Dokumen:\n{context_block}\n\nPertanyaan: {question}\n\nJawaban terperinci:"
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content or "Tidak dapat menghasilkan jawaban."
        except Exception as e:
            return f"Error saat menghubungi LLM ({str(e)}). Mengembalikan kutipan dokumen langsung: {contexts[0].snippet}"


llm_service = LLMService()
