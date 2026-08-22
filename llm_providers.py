"""
LLM Provider Abstraction Layer
Supports multiple backends: Anthropic Claude, Hermes, etc.
"""

from abc import ABC, abstractmethod
from typing import Tuple
import logging
import os

logger = logging.getLogger(__name__)


class AgentConfig:
    """Agent configuration (shared across providers)"""
    def __init__(self, reasoning_effort: str = "medium", model: str = "claude-opus-5", max_tokens: int = 4096, system_prompt: str = None):
        self.reasoning_effort = reasoning_effort
        self.model = model
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or "You are a helpful AI assistant."


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def invoke(self, prompt: str, config: AgentConfig) -> Tuple[str, bool]:
        """
        Invoke the LLM with a prompt and system prompt.
        Returns: (response_text, reasoning_used)
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if provider is available"""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set. Claude provider will use mock responses.")

    def health_check(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)

    def invoke(self, prompt: str, config: AgentConfig) -> Tuple[str, bool]:
        """Call Claude API via Anthropic"""
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set. Using mock response.")
            return f"Mock: {prompt[:100]}...", False

        import httpx

        try:
            # Map model names to actual Anthropic models
            model_map = {
                "claude-opus-5": "claude-opus-5",
                "claude-opus-4": "claude-opus-5",
                "claude-sonnet-5": "claude-sonnet-5",
                "claude-sonnet": "claude-sonnet-5",
                "claude-opus": "claude-opus-5",
                "claude-haiku": "claude-haiku-4-5-20251001",
            }
            actual_model = model_map.get(config.model, "claude-opus-5")

            # Build request payload
            payload = {
                "model": actual_model,
                "max_tokens": config.max_tokens,
                "system": config.system_prompt,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            # Add thinking if using high reasoning
            if config.reasoning_effort in ["high", "xhigh", "max", "ultra"]:
                # Newer models (Opus 5, Sonnet 5) use "adaptive" thinking
                payload["thinking"] = {
                    "type": "adaptive"
                }
                # Map reasoning effort to output effort
                effort_map = {
                    "high": "medium",
                    "xhigh": "high",
                    "max": "high",
                    "ultra": "high"
                }
                payload["output_config"] = {
                    "effort": effort_map.get(config.reasoning_effort, "medium")
                }

            logger.info(f"[Anthropic] Calling {actual_model} (reasoning: {config.reasoning_effort})")

            # Call Anthropic API
            with httpx.Client() as client:
                response = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json=payload,
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    text_content = ""
                    thinking_content = ""

                    for block in result.get("content", []):
                        if block.get("type") == "text":
                            text_content = block.get("text", "")
                        elif block.get("type") == "thinking":
                            thinking_content = block.get("thinking", "")

                    response_text = text_content or f"(Processed: {prompt[:50]}...)"
                    reasoning_used = bool(thinking_content)

                    logger.info(f"[Anthropic] ✓ Response ({len(response_text)} chars, reasoning: {reasoning_used})")
                    return response_text, reasoning_used
                else:
                    error_msg = response.text[:200]
                    logger.error(f"[Anthropic] API error {response.status_code}: {error_msg}")
                    return f"❌ API error: {error_msg}", False

        except Exception as e:
            logger.error(f"[Anthropic] Error: {e}")
            return f"❌ Error: {str(e)[:200]}", False


class HermesProvider(LLMProvider):
    """Hermes local agent provider"""

    def __init__(self):
        self.hermes_available = self._check_hermes()

    def _check_hermes(self) -> bool:
        """Check if Hermes is installed and accessible"""
        try:
            from pathlib import Path
            hermes_home = Path.home() / ".hermes"
            return hermes_home.exists()
        except Exception as e:
            logger.error(f"[Hermes] Error checking availability: {e}")
            return False

    def health_check(self) -> bool:
        """Check if Hermes is available"""
        return self.hermes_available

    def invoke(self, prompt: str, config: AgentConfig) -> Tuple[str, bool]:
        """Call Hermes agent"""
        if not self.hermes_available:
            logger.warning("[Hermes] Hermes not available. Using mock response.")
            return f"Mock (Hermes unavailable): {prompt[:100]}...", False

        try:
            # TODO: Implement actual Hermes invocation
            # This is a placeholder for the real Hermes integration
            # In production, this would:
            # 1. Import hermes-agent from ~/.hermes
            # 2. Create an agent instance
            # 3. Invoke with the prompt
            # 4. Return response + reasoning_used flag

            logger.info(f"[Hermes] Would invoke agent (reasoning: {config.reasoning_effort})")

            # For now, return a placeholder
            response_text = f"[Hermes] {prompt[:100]}..."
            reasoning_used = config.reasoning_effort in ["high", "xhigh", "max", "ultra"]

            return response_text, reasoning_used

        except Exception as e:
            logger.error(f"[Hermes] Error: {e}")
            return f"❌ Hermes error: {str(e)[:200]}", False


def get_provider(provider_name: str = None) -> LLMProvider:
    """Factory function to get the configured provider"""
    if provider_name is None:
        provider_name = os.getenv("LLM_PROVIDER", "anthropic").lower()

    providers = {
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,  # Alias
        "hermes": HermesProvider,
    }

    provider_class = providers.get(provider_name)
    if not provider_class:
        logger.warning(f"Unknown provider '{provider_name}', defaulting to Anthropic")
        provider_class = AnthropicProvider

    logger.info(f"Loaded LLM provider: {provider_class.__name__}")
    return provider_class()
