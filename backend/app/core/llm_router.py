"""
Multi-LLM Router with Automatic Fallback

Cycles through free-tier LLM providers when rate limits are hit.
Supports structured output for resume parsing and tailoring.

Usage:
    from app.core.llm_router import get_llm, get_structured_llm

    llm = get_llm()  # Returns best available LLM
    structured_llm = get_structured_llm(MyPydanticModel)  # With structured output
"""

import os
from typing import Type, TypeVar, Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

T = TypeVar("T", bound=BaseModel)


# ─────────────────────────────────────────────────────────────
# Provider Configurations
# ─────────────────────────────────────────────────────────────

class LLMProvider:
    """Base class for LLM providers."""

    name: str = "base"
    priority: int = 0  # Lower = higher priority

    def __init__(self):
        self.is_available = self._check_availability()
        self.failure_count = 0
        self.max_failures = 3  # After 3 failures, skip this provider temporarily

    def _check_availability(self) -> bool:
        """Check if API key is configured."""
        raise NotImplementedError

    def get_llm(self, temperature: float = 0.1):
        """Return the LangChain LLM instance."""
        raise NotImplementedError

    def get_structured_llm(self, schema: Type[T], temperature: float = 0.1):
        """Return LLM with structured output."""
        llm = self.get_llm(temperature)
        return llm.with_structured_output(schema, method="json_schema")

    def mark_failure(self):
        """Mark a failure for this provider."""
        self.failure_count += 1
        if self.failure_count >= self.max_failures:
            logger.warning(f"⚠️ {self.name} hit max failures, temporarily disabled")

    def reset_failures(self):
        """Reset failure count on success."""
        self.failure_count = 0

    @property
    def is_healthy(self) -> bool:
        return self.is_available and self.failure_count < self.max_failures


class GeminiProvider(LLMProvider):
    """Google Gemini - Primary (60 req/min free)"""

    name = "Gemini"
    priority = 1

    def _check_availability(self) -> bool:
        return bool(os.getenv("GOOGLE_API_KEY"))

    def get_llm(self, temperature: float = 0.1):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=temperature,
            max_output_tokens=4096,
        )


class OpenRouterProvider(LLMProvider):
    """OpenRouter - Access to many free models via single API"""

    name = "OpenRouter"
    priority = 2

    def _check_availability(self) -> bool:
        return bool(os.getenv("OPENROUTER_API_KEY"))

    def get_llm(self, temperature: float = 0.1):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="tngtech/deepseek-r1t2-chimera:free",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=4096,
            default_headers={
                "HTTP-Referer": "https://eiregate.app",
                "X-Title": "EireGate"
            }
        )


class MistralProvider(LLMProvider):
    """Mistral AI - mistral-small (free tier)"""

    name = "Mistral"
    priority = 3

    def _check_availability(self) -> bool:
        return bool(os.getenv("MISTRAL_API_KEY"))

    def get_llm(self, temperature: float = 0.1):
        from langchain_mistralai import ChatMistralAI
        return ChatMistralAI(
            model="mistral-small-latest",
            api_key=os.getenv("MISTRAL_API_KEY"),
            temperature=temperature,
            max_tokens=4096,
        )


class HuggingFaceProvider(LLMProvider):
    """Hugging Face Inference API - Free serverless models"""

    name = "HuggingFace"
    priority = 4

    def _check_availability(self) -> bool:
        return bool(os.getenv("HUGGINGFACE_API_KEY"))

    def get_llm(self, temperature: float = 0.1):
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

        llm = HuggingFaceEndpoint(
            repo_id="HuggingFaceH4/zephyr-7b-beta",
            huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY"),
            temperature=temperature,
            max_new_tokens=2048,
        )
        return ChatHuggingFace(llm=llm)


# ─────────────────────────────────────────────────────────────
# LLM Router
# ─────────────────────────────────────────────────────────────

class LLMRouter:
    """
    Multi-LLM router with automatic fallback.

    Tries providers in priority order, falling back on rate limits or errors.
    """

    def __init__(self):
        # Initialize all providers
        self.providers: List[LLMProvider] = [
            GeminiProvider(),
            OpenRouterProvider(),
            MistralProvider(),
            HuggingFaceProvider(),
        ]

        # Filter to only available providers
        self.available_providers = [p for p in self.providers if p.is_available]

        # Sort by priority
        self.available_providers.sort(key=lambda p: p.priority)

        if not self.available_providers:
            raise ValueError(
                "No LLM providers configured! Add at least one API key to .env:\n"
                "  GOOGLE_API_KEY=...\n"
                "  OPENROUTER_API_KEY=...\n"
                "  MISTRAL_API_KEY=...\n"
                "  HUGGINGFACE_API_KEY=..."
            )

        logger.info(f"✓ LLM Router initialized with {len(self.available_providers)} providers: "
                    f"{[p.name for p in self.available_providers]}")

    def get_healthy_providers(self) -> List[LLMProvider]:
        """Get providers that haven't hit their failure limit."""
        healthy = [p for p in self.available_providers if p.is_healthy]
        if not healthy:
            # Reset all providers if none are healthy
            logger.warning("All providers exhausted, resetting failure counts...")
            for p in self.available_providers:
                p.reset_failures()
            return self.available_providers
        return healthy

    def get_llm(self, temperature: float = 0.1):
        """Get the best available LLM."""
        providers = self.get_healthy_providers()
        return providers[0].get_llm(temperature)

    def get_provider_name(self) -> str:
        """Get the name of the current primary provider."""
        providers = self.get_healthy_providers()
        return providers[0].name if providers else "None"


# ─────────────────────────────────────────────────────────────
# Smart Invoke with Fallback
# ─────────────────────────────────────────────────────────────

# Global router instance
_router: Optional[LLMRouter] = None


def get_router() -> LLMRouter:
    """Get or create the global router instance."""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router


def invoke_with_fallback(
    prompt_template,
    input_data: dict,
    output_schema: Optional[Type[T]] = None,
    temperature: float = 0.1,
) -> T | str:
    """
    Invoke LLM with automatic fallback on failure.

    Args:
        prompt_template: LangChain ChatPromptTemplate
        input_data: Dict of variables for the prompt
        output_schema: Optional Pydantic model for structured output
        temperature: LLM temperature

    Returns:
        Parsed Pydantic model if schema provided, else raw string
    """
    router = get_router()
    providers = router.get_healthy_providers()

    last_error = None

    for provider in providers:
        try:
            logger.debug(f"Trying {provider.name}...")

            llm = provider.get_llm(temperature)

            if output_schema:
                structured_llm = llm.with_structured_output(output_schema, method="json_schema")
                chain = prompt_template | structured_llm
            else:
                chain = prompt_template | llm

            result = chain.invoke(input_data)

            # Success! Reset failure count
            provider.reset_failures()
            logger.info(f"✓ {provider.name} succeeded")

            return result

        except Exception as e:
            error_msg = str(e).lower()

            # Check if it's a rate limit or quota error
            is_rate_limit = any(x in error_msg for x in [
                "rate limit", "quota", "429", "too many requests",
                "resource exhausted", "capacity", "overloaded"
            ])

            if is_rate_limit:
                logger.warning(f"⚠️ {provider.name} rate limited: {e}")
                provider.mark_failure()
            else:
                logger.error(f"❌ {provider.name} error: {e}")
                provider.mark_failure()

            last_error = e
            continue

    # All providers failed
    raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")


def get_llm(temperature: float = 0.1):
    """Get the best available LLM (convenience function)."""
    return get_router().get_llm(temperature)


def get_current_provider() -> str:
    """Get the name of the current primary provider."""
    return get_router().get_provider_name()


# ─────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────

def get_llm_status() -> dict:
    """Get status of all LLM providers for health endpoint."""
    router = get_router()
    return {
        "current_provider": router.get_provider_name(),
        "providers": [
            {
                "name": p.name,
                "available": p.is_available,
                "healthy": p.is_healthy,
                "failures": p.failure_count,
                "priority": p.priority,
            }
            for p in router.providers
        ]
    }


def test_provider(provider_name: str) -> dict:
    """
    Test a specific LLM provider with a simple prompt.
    Returns success/failure and response time.
    """
    import time

    router = get_router()

    # Find the provider
    provider = None
    for p in router.providers:
        if p.name.lower() == provider_name.lower():
            provider = p
            break

    if not provider:
        return {
            "provider": provider_name,
            "success": False,
            "error": f"Provider '{provider_name}' not found. Available: {[p.name for p in router.providers]}"
        }

    if not provider.is_available:
        return {
            "provider": provider.name,
            "success": False,
            "error": "API key not configured"
        }

    try:
        start_time = time.time()

        llm = provider.get_llm(temperature=0.1)
        response = llm.invoke("Say 'Hello from {provider}!' in exactly 5 words.".format(provider=provider.name))

        elapsed = round(time.time() - start_time, 2)

        # Extract content from response
        content = response.content if hasattr(response, 'content') else str(response)

        provider.reset_failures()

        return {
            "provider": provider.name,
            "success": True,
            "response": content,
            "response_time_seconds": elapsed
        }

    except Exception as e:
        provider.mark_failure()
        return {
            "provider": provider.name,
            "success": False,
            "error": str(e)
        }


def test_all_providers() -> dict:
    """Test all configured LLM providers and return results."""
    router = get_router()
    results = []

    for provider in router.providers:
        if provider.is_available:
            result = test_provider(provider.name)
            results.append(result)
        else:
            results.append({
                "provider": provider.name,
                "success": False,
                "error": "API key not configured",
                "skipped": True
            })

    working = sum(1 for r in results if r.get("success", False))

    return {
        "summary": f"{working}/{len(results)} providers working",
        "results": results
    }
