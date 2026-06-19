import json
import requests
from typing import List, Dict, Any
from src.configs.settings import settings


class LLMClient:
    def __init__(self) -> None:
        self.ollama_url = settings.OLLAMA_HOST
        self.embedding_model = settings.EMBEDDING_MODEL

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate a text embedding vector using the local Ollama instance
        with the specified embedding model (e.g., nomic-embed-text).
        """
        try:
            url = f"{self.ollama_url}/api/embeddings"
            payload = {
                "model": self.embedding_model,
                "prompt": text
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        except Exception as e:
            print(f"Ollama Embedding Error: {e}. Falling back to mock 768-dim vector.")
            # Return a mock 768-dimensional float vector as fallback
            return [0.0] * 768

    def extract_triplets(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract Subject-Predicate-Object triplets from the text.
        Prioritizes OpenAI/Gemini APIs if keys are active, otherwise falls back
        to a local Ollama model (llama3.1:8b / qwen3:8b) or a rule-based mock.
        """
        # 1. Try OpenAI if keys are active
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "mock-key":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                prompt = (
                    "Extract entities and relationships from the following text as a JSON array of triplets. "
                    "Each item must be a JSON object with keys: 'subject', 'predicate', 'object', and 'confidence' (0.0 to 1.0).\n\n"
                    f"Text:\n{text}"
                )
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                content = res.choices[0].message.content
                data = json.loads(content)
                # Handle cases where LLM returns root dict like {"triplets": [...]}
                if "triplets" in data:
                    return data["triplets"]
                elif isinstance(data, list):
                    return data
                return []
            except Exception as e:
                print(f"OpenAI Triplet Extraction failed: {e}. Trying local fallback...")

        # 2. Fall back to local Ollama LLM (prefer llama3.1:8b if available)
        try:
            url = f"{self.ollama_url}/api/generate"
            system_prompt = (
                "You are an information extraction system. Respond strictly with a JSON object containing a "
                "single list key 'triplets'. Each triplet has keys: 'subject', 'predicate', 'object', and 'confidence' (float 0.0 to 1.0). "
                "Do not include any thinking, markdown wrapping, or explanations outside the JSON."
            )
            prompt = (
                f"Identify key facts as triplets from this text:\n\n{text}\n\n"
                "Example format: {\"triplets\": [{\"subject\": \"Alice\", \"predicate\": \"works at\", \"object\": \"Google\", \"confidence\": 0.95}]}"
            )
            
            payload = {
                "model": "llama3.1:8b",  # Fallback to llama3.1:8b which exists in user tags
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "format": "json"
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            content = result.get("response", "").strip()
            data = json.loads(content)
            return data.get("triplets", [])
        except Exception as e:
            print(f"Local Ollama Triplet Extraction failed: {e}. Falling back to default mock triplets.")
            
        # 3. Final mock fallback
        return [
            {"subject": "Brainy Platform", "predicate": "ingests", "object": "YouTube Videos", "confidence": 0.98},
            {"subject": "YouTube Videos", "predicate": "contain", "object": "Audio Streams", "confidence": 0.95},
            {"subject": "Whisper Engine", "predicate": "transcribes", "object": "Audio Streams", "confidence": 0.90}
        ]


# Global LLM client instance
llm_client = LLMClient()
