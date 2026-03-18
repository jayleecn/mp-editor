"""Image Generation Service for mp-editor skill."""
import os
import base64
import tempfile
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import httpx
import logging

logger = logging.getLogger(__name__)


class ImageGenProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    async def generate(self, prompt: str, size: str = "3024x1296") -> str:
        """
        Generate image from prompt.

        Args:
            prompt: Image generation prompt
            size: Image size (width x height)

        Returns:
            URL or base64 data URI of the generated image
        """
        pass

    @abstractmethod
    def generate_sync(self, prompt: str, size: str = "3024x1296") -> str:
        """Synchronous version of generate."""
        pass


class AliyunImageProvider(ImageGenProvider):
    """Aliyun DashScope image generation provider."""

    def __init__(self):
        self.api_key = os.getenv("ALIYUN_API_KEY")
        self.base_url = os.getenv("ALIYUN_BASE_URL", "https://dashscope.aliyuncs.com")
        self.model = os.getenv("ALIYUN_IMAGE_MODEL", "wanx2.1-t2i-turbo")

        if not self.api_key:
            logger.warning("ALIYUN_API_KEY not set for image generation")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _parse_size(self, size: str) -> str:
        """Parse size string to DashScope format."""
        # Default size for WeChat cover (3024x1296 ~= 900:383)
        size_map = {
            "3024x1296": "1440*640",  # Wide banner
            "1024x1024": "1024*1024",  # Square
            "768x1344": "768*1344",    # Portrait
        }
        return size_map.get(size, "1440*640")

    async def generate(self, prompt: str, size: str = "3024x1296") -> str:
        """Generate image via Aliyun DashScope."""
        if not self.api_key:
            raise ValueError("ALIYUN_API_KEY not configured")

        # Normalize base URL to origin
        try:
            origin = str(self.base_url).split("/compatible-mode")[0]
        except:
            origin = self.base_url

        # Use correct endpoint per reference implementation
        url = f"{origin.rstrip('/')}/api/v1/services/aigc/multimodal-generation/generation"

        # Match reference implementation payload format
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ]
            },
            "parameters": {
                "prompt_extend": False,
                "size": "1536*864",
            }
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            # Submit task
            response = await client.post(url, headers=self._get_headers(), json=payload)
            if not response.is_success:
                error_text = await response.text()
                raise ValueError(f"Aliyun image generation failed: {response.status_code} - {error_text[:500]}")

            data = response.json()

            # Check for immediate result or task-based result
            image_data = data.get("output", {}).get("result_image")
            if image_data:
                if str(image_data).startswith("http"):
                    return str(image_data)
                return f"data:image/png;base64,{image_data}"

            # Check for content array format
            content = data.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", [])
            for item in content:
                if item.get("image"):
                    img = item["image"]
                    if str(img).startswith("http"):
                        return str(img)
                    return f"data:image/png;base64,{img}"

            raise ValueError(f"No image in response: {data}")

    def generate_sync(self, prompt: str, size: str = "3024x1296") -> str:
        """Synchronous image generation via Aliyun DashScope."""
        import asyncio
        return asyncio.run(self.generate(prompt, size))


class GoogleImageProvider(ImageGenProvider):
    """Google Gemini image generation provider."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.base_url = os.getenv("GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self.model = os.getenv("GOOGLE_IMAGE_MODEL", "gemini-2.0-flash-exp-image-generation")

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set for image generation")

    async def generate(self, prompt: str, size: str = "3024x1296") -> str:
        """Generate image via Google Gemini."""
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        url = f"{self.base_url.rstrip('/')}/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "responseModalities": ["TEXT", "IMAGE"],
            }
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        # Extract image from response
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])

        for part in parts:
            if "inlineData" in part:
                mime_type = part["inlineData"].get("mimeType", "image/png")
                image_data = part["inlineData"].get("data", "")
                return f"data:{mime_type};base64,{image_data}"

        raise ValueError(f"No image generated in response: {data}")

    def generate_sync(self, prompt: str, size: str = "3024x1296") -> str:
        """Synchronous image generation via Google Gemini."""
        import asyncio
        return asyncio.run(self.generate(prompt, size))


class ImageGenService:
    """Provider-agnostic image generation service."""

    PROVIDERS = {
        "aliyun": AliyunImageProvider,
        "google": GoogleImageProvider,
    }

    def __init__(self, provider: Optional[str] = None, fallback_chain: Optional[list] = None):
        """
        Initialize image generation service.

        Args:
            provider: Primary provider name (aliyun|google)
            fallback_chain: List of provider names to try on failure
        """
        self.provider_name = provider or os.getenv("IMAGE_PROVIDER", "aliyun")
        self.fallback_chain = fallback_chain or ["aliyun", "google"]
        self.provider = self._create_provider(self.provider_name)

    def _create_provider(self, name: str) -> ImageGenProvider:
        """Create provider instance by name."""
        provider_class = self.PROVIDERS.get(name.lower())
        if not provider_class:
            raise ValueError(f"Unknown image provider: {name}. Available: {list(self.PROVIDERS.keys())}")
        return provider_class()

    async def generate(self, prompt: str, size: str = "3024x1296") -> str:
        """
        Generate image with fallback support.

        Args:
            prompt: Image generation prompt
            size: Image size (width x height)

        Returns:
            URL or base64 data URI of the generated image
        """
        tried = []
        for provider_name in [self.provider_name] + [p for p in self.fallback_chain if p != self.provider_name]:
            if provider_name in tried:
                continue
            tried.append(provider_name)

            try:
                if provider_name == self.provider_name:
                    provider = self.provider
                else:
                    provider = self._create_provider(provider_name)

                logger.info(f"Trying image provider: {provider_name}")
                result = await provider.generate(prompt, size)
                logger.info(f"Successfully used image provider: {provider_name}")
                return result

            except Exception as e:
                logger.warning(f"Image provider {provider_name} failed: {e}")
                if provider_name == tried[-1]:
                    raise
                continue

        raise RuntimeError("All image providers failed")

    def generate_sync(self, prompt: str, size: str = "3024x1296") -> str:
        """Synchronous image generation with fallback support."""
        import asyncio
        tried = []

        for provider_name in [self.provider_name] + [p for p in self.fallback_chain if p != self.provider_name]:
            if provider_name in tried:
                continue
            tried.append(provider_name)

            try:
                if provider_name == self.provider_name:
                    provider = self.provider
                else:
                    provider = self._create_provider(provider_name)

                logger.info(f"Trying image provider: {provider_name}")
                result = provider.generate_sync(prompt, size)
                logger.info(f"Successfully used image provider: {provider_name}")
                return result

            except Exception as e:
                logger.warning(f"Image provider {provider_name} failed: {e}")
                if provider_name == tried[-1]:
                    raise
                continue

        raise RuntimeError("All image providers failed")


