"""LLM Service for mp-editor skill - Provider-agnostic LLM interface."""
import os
import asyncio
from typing import List, Optional
from llm.providers import (
    LLMProvider,
    Message,
    LLMConfig,
    AliyunProvider,
    GoogleProvider,
)
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Provider-agnostic LLM service with fallback support."""

    PROVIDERS = {
        "aliyun": AliyunProvider,
        "google": GoogleProvider,
    }

    def __init__(self, provider: Optional[str] = None, fallback_chain: Optional[List[str]] = None):
        """
        Initialize LLM service.

        Args:
            provider: Primary provider name (aliyun|google)
            fallback_chain: List of provider names to try on failure
        """
        self.provider_name = provider or os.getenv("LLM_PROVIDER", "aliyun")
        self.fallback_chain = fallback_chain or self._build_fallback_chain()
        self.provider = self._create_provider(self.provider_name)

    def _build_fallback_chain(self) -> List[str]:
        """Build default fallback chain from environment or default."""
        fallback = os.getenv("LLM_FALLBACK_CHAIN", "")
        if fallback:
            return [p.strip() for p in fallback.split(",") if p.strip()]
        # Default fallback: aliyun -> google
        return ["aliyun", "google"]

    def _create_provider(self, name: str) -> LLMProvider:
        """Create provider instance by name."""
        provider_class = self.PROVIDERS.get(name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {name}. Available: {list(self.PROVIDERS.keys())}")
        return provider_class()

    async def chat(self, messages: List[Message], config: LLMConfig) -> str:
        """
        Send chat completion request with fallback support.

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

        # Try primary provider and fallbacks
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

                logger.info(f"Trying LLM provider: {provider_name}")
                result = await provider.chat(converted_messages, config)
                logger.info(f"Successfully used provider: {provider_name}")
                return result

            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                if provider_name == tried[-1]:  # Last provider
                    raise
                continue

        raise RuntimeError("All LLM providers failed")

    def chat_sync(self, messages: List[Message], config: LLMConfig) -> str:
        """
        Synchronous chat completion with fallback support.

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

        # Try primary provider and fallbacks
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

                logger.info(f"Trying LLM provider: {provider_name}")
                result = provider.chat_sync(converted_messages, config)
                logger.info(f"Successfully used provider: {provider_name}")
                return result

            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                if provider_name == tried[-1]:  # Last provider
                    raise
                continue

        raise RuntimeError("All LLM providers failed")

    async def chat_with_fallback_config(self, messages: List[Message], llm_config: dict) -> str:
        """
        Convenience method that accepts raw config dict from JSON.

        Args:
            messages: List of Message or LangChain message objects
            llm_config: Configuration dict with keys like model, temperature, etc.

        Returns:
            Response text from the LLM
        """
        config = LLMConfig(
            model=llm_config.get("model"),
            temperature=llm_config.get("temperature", 0.8),
            top_p=llm_config.get("top_p", 1.0),
            max_completion_tokens=llm_config.get("max_completion_tokens", 4096),
            thinking=llm_config.get("thinking", "disabled"),
        )
        return await self.chat(messages, config)

    def chat_sync_with_fallback_config(self, messages: List[Message], llm_config: dict) -> str:
        """
        Synchronous version with raw config dict.

        Args:
            messages: List of Message or LangChain message objects
            llm_config: Configuration dict with keys like model, temperature, etc.

        Returns:
            Response text from the LLM
        """
        config = LLMConfig(
            model=llm_config.get("model"),
            temperature=llm_config.get("temperature", 0.8),
            top_p=llm_config.get("top_p", 1.0),
            max_completion_tokens=llm_config.get("max_completion_tokens", 4096),
            thinking=llm_config.get("thinking", "disabled"),
        )
        return self.chat_sync(messages, config)
