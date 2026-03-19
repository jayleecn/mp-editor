"""Image Generation Service for mp-editor skill - Aliyun only."""
import os
import base64
from typing import Dict
import httpx
import logging

logger = logging.getLogger(__name__)


class AliyunImageProvider:
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


class ImageGenService:
    """Aliyun-only image generation service."""

    def __init__(self, provider: str = "aliyun"):
        """
        Initialize image generation service.

        Args:
            provider: Provider name (only 'aliyun' supported)
        """
        if provider != "aliyun":
            logger.warning(f"Only 'aliyun' provider is supported, ignoring: {provider}")
        self.provider = AliyunImageProvider()

    async def generate(self, prompt: str, size: str = "3024x1296") -> str:
        """
        Generate image.

        Args:
            prompt: Image generation prompt
            size: Image size (width x height)

        Returns:
            URL or base64 data URI of the generated image
        """
        logger.info("Generating image via Aliyun DashScope")
        return await self.provider.generate(prompt, size)

    def generate_sync(self, prompt: str, size: str = "3024x1296") -> str:
        """Synchronous image generation."""
        logger.info("Generating image via Aliyun DashScope")
        return self.provider.generate_sync(prompt, size)
