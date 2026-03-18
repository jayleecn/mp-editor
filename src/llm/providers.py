"""LLM Provider implementations for mp-editor skill."""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class Message:
    """Simple message class compatible with LangChain messages."""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    @classmethod
    def from_langchain(cls, message):
        """Convert from LangChain message format."""
        if hasattr(message, 'type') and hasattr(message, 'content'):
            # LangChain v2 message
            role_map = {
                'system': 'system',
                'human': 'user',
                'ai': 'assistant',
                'assistant': 'assistant',
            }
            role = role_map.get(message.type, 'user')
            return cls(role=role, content=message.content)
        elif hasattr(message, 'role') and hasattr(message, 'content'):
            # Already in our format
            return cls(role=message.role, content=message.content)
        else:
            # Try to extract content
            content = str(message)
            return cls(role='user', content=content)


class LLMConfig:
    """Configuration for LLM calls."""
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.8,
        top_p: float = 1.0,
        max_completion_tokens: int = 4096,
        thinking: str = "disabled",
        **kwargs
    ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_completion_tokens = max_completion_tokens
        self.thinking = thinking
        self.extra = kwargs


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def chat(self, messages: List[Message], config: LLMConfig) -> str:
        """Send chat completion request and return the response text."""
        pass

    @abstractmethod
    def chat_sync(self, messages: List[Message], config: LLMConfig) -> str:
        """Synchronous version of chat."""
        pass


class AliyunProvider(LLMProvider):
    """Aliyun DashScope provider - OpenAI compatible mode."""

    def __init__(self):
        self.api_key = os.getenv("ALIYUN_API_KEY")
        self.base_url = os.getenv("ALIYUN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.default_model = os.getenv("ALIYUN_MODEL", "qwen-max")

        if not self.api_key:
            logger.warning("ALIYUN_API_KEY not set")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _prepare_payload(self, messages: List[Message], config: LLMConfig) -> Dict[str, Any]:
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        payload = {
            "model": config.model or self.default_model,
            "messages": msgs,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_tokens": config.max_completion_tokens,
        }
        return payload

    async def chat(self, messages: List[Message], config: LLMConfig) -> str:
        """Async chat completion via Aliyun DashScope."""
        if not self.api_key:
            raise ValueError("ALIYUN_API_KEY not configured")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = self._prepare_payload(messages, config)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            data = response.json()

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            raise ValueError(f"Empty response from Aliyun: {data}")

        return content

    def chat_sync(self, messages: List[Message], config: LLMConfig) -> str:
        """Synchronous chat completion via Aliyun DashScope."""
        if not self.api_key:
            raise ValueError("ALIYUN_API_KEY not configured")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = self._prepare_payload(messages, config)

        response = httpx.post(url, headers=self._get_headers(), json=payload, timeout=120.0)
        response.raise_for_status()
        data = response.json()

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            raise ValueError(f"Empty response from Aliyun: {data}")

        return content


class GoogleProvider(LLMProvider):
    """Google Gemini provider."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.base_url = os.getenv("GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self.default_model = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set")

    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert messages to Gemini format."""
        contents = []
        for msg in messages:
            role = "model" if msg.role in ("assistant", "ai") else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        return contents

    async def chat(self, messages: List[Message], config: LLMConfig) -> str:
        """Async chat completion via Google Gemini."""
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        model = config.model or self.default_model
        url = f"{self.base_url.rstrip('/')}/models/{model}:generateContent?key={self.api_key}"

        contents = self._convert_messages(messages)
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": config.temperature,
                "topP": config.top_p,
                "maxOutputTokens": config.max_completion_tokens,
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        content = "".join([p.get("text", "") for p in parts])

        if not content:
            raise ValueError(f"Empty response from Google: {data}")

        return content

    def chat_sync(self, messages: List[Message], config: LLMConfig) -> str:
        """Synchronous chat completion via Google Gemini."""
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        model = config.model or self.default_model
        url = f"{self.base_url.rstrip('/')}/models/{model}:generateContent?key={self.api_key}"

        contents = self._convert_messages(messages)
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": config.temperature,
                "topP": config.top_p,
                "maxOutputTokens": config.max_completion_tokens,
            }
        }

        response = httpx.post(url, json=payload, timeout=120.0)
        response.raise_for_status()
        data = response.json()

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        content = "".join([p.get("text", "") for p in parts])

        if not content:
            raise ValueError(f"Empty response from Google: {data}")

        return content
