"""LLM Service for mp-editor skill - Aliyun only."""
import os
import asyncio
from typing import List, Optional
from llm.providers import (
    Message,
    LLMConfig,
    AliyunProvider,
)
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Aliyun-only LLM service."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM service.

        Args:
            provider: Provider name (only 'aliyun' supported)
        """
        self.provider_name = provider or os.getenv("LLM_PROVIDER", "aliyun")
        if self.provider_name != "aliyun":
            logger.warning(f"Only 'aliyun' provider is supported, ignoring: {self.provider_name}")
            self.provider_name = "aliyun"
        self.provider = AliyunProvider()

    async def chat(self, messages: List[Message], config: LLMConfig) -> str:
        """
        Send chat completion request.

        Args:
            messages: List of Message objects
            config: LLM configuration

        Returns:
            Response text from the LLM
        """
        # Convert LangChain messages if needed
        converted_messages = []
        for msg in messages:
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                converted_messages.append(Message.from_langchain(msg))
            else:
                converted_messages.append(msg)

        return await self.provider.chat(converted_messages, config)

    def chat_sync(self, messages: List[Message], config: LLMConfig) -> str:
        """
        Synchronous chat completion.

        Args:
            messages: List of Message objects
            config: LLM configuration

        Returns:
            Response text from the LLM
        """
        # Convert LangChain messages if needed
        converted_messages = []
        for msg in messages:
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                converted_messages.append(Message.from_langchain(msg))
            else:
                converted_messages.append(msg)

        return self.provider.chat_sync(converted_messages, config)

    def chat_sync_with_fallback_config(self, messages: List[Message], llm_config: dict) -> str:
        """
        Synchronous chat with config dict support.

        Args:
            messages: List of Message objects
            llm_config: Raw config dict with model, temperature, etc.

        Returns:
            Response text from the LLM
        """
        config = LLMConfig(
            model=llm_config.get("model"),
            temperature=llm_config.get("temperature", 0.8),
            top_p=llm_config.get("top_p", 1.0),
            max_completion_tokens=llm_config.get("max_completion_tokens", 4096),
        )
        return self.chat_sync(messages, config)
