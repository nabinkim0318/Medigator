# api/services/llm/client.py
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from collections.abc import Callable
from typing import Any

from openai import (
    APIConnectionError,
    AsyncOpenAI,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from core.config import settings

logger = logging.getLogger("llm")

# ---- Config normalization ----
LLM_MODEL = getattr(settings, "LLM_MODEL", getattr(settings, "openai_model", "gpt-4o-mini"))
LLM_TEMPERATURE = float(
    getattr(settings, "LLM_TEMPERATURE", getattr(settings, "openai_temperature", 0.1)),
)
LLM_TOP_P = float(
    getattr(settings, "LLM_TOP_P", getattr(settings, "openai_top_p", 0.9)),
)
LLM_TIMEOUT_S = (
    float(getattr(settings, "LLM_TIMEOUT_MS", getattr(settings, "openai_timeout_ms", 3500)))
    / 1000.0
)
LLM_SEED = int(
    getattr(settings, "LLM_SEED", getattr(settings, "openai_seed", 42)),
)
OPENAI_API_KEY = getattr(settings, "OPENAI_API_KEY", getattr(settings, "openai_api_key", None))

# Optional: Azure/OpenRouter etc custom endpoint
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # if none, basic

# ---- Clients (sync/async) ----
sync_client: OpenAI | None = None
async_client: AsyncOpenAI | None = None
if OPENAI_API_KEY:
    base_kwargs = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        base_kwargs["base_url"] = OPENAI_BASE_URL
    sync_client = OpenAI(**base_kwargs)
    async_client = AsyncOpenAI(**base_kwargs)


# ---- Enhanced TTL cache with metrics ----
class _TTLCache:
    def __init__(self, ttl_s: int = 1800, maxsize: int = 256):
        self.ttl = ttl_s
        self.store: dict[str, tuple[float, Any]] = {}
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _now(self):
        return time.time()

    def get(self, k: str):
        v = self.store.get(k)
        if not v:
            self.misses += 1
            return None

        ts, val = v
        if self._now() - ts > self.ttl:
            self.store.pop(k, None)
            self.misses += 1
            return None

        self.hits += 1
        return val

    def set(self, k: str, v: Any):
        if len(self.store) >= self.maxsize:
            # drop oldest
            oldest = min(self.store.items(), key=lambda x: x[1][0])[0]
            self.store.pop(oldest, None)
            self.evictions += 1

        self.store[k] = (self._now(), v)

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        return {
            "size": len(self.store),
            "max_size": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": round(hit_rate, 3),
        }


_cache = _TTLCache()


def _ckey(
    messages: list[dict],
    model: str,
    temperature: float,
    response_format: dict | None,
    *,
    top_p: float | None = None,
    seed: int | None = None,
) -> str:
    blob = json.dumps(
        {
            "m": messages,
            "model": model,
            "t": temperature,
            "tp": top_p,
            "seed": seed,
            "rf": response_format,
        },
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode()).hexdigest()


# ---- Enhanced Retry helpers ----
def _is_retryable(e: Exception) -> bool:
    """Check if exception is retryable with more specific error handling"""
    return isinstance(
        e,
        (
            APIConnectionError,
            RateLimitError,
            InternalServerError,
            TimeoutError,
            asyncio.TimeoutError,
        ),
    ) or any(
        k in str(e).lower()
        for k in [
            "rate limit",
            "timeout",
            "connection",
            "server error",
            "unavailable",
            "temporary",
            "retry",
        ]
    )


async def _retry_async(fn, *, attempts=3, base_delay=0.25, max_delay=2.0):
    """Enhanced retry with better error handling and logging"""
    last = None
    for i in range(attempts):
        try:
            return await fn()
        except Exception as e:
            last = e
            logger.warning(f"Attempt {i + 1}/{attempts} failed: {type(e).__name__}: {e}")

            if not _is_retryable(e) or i == attempts - 1:
                logger.error(f"Final attempt failed: {type(e).__name__}: {e}")
                raise

            delay = min(max_delay, base_delay * (2**i))
            logger.info(f"Retrying in {delay:.2f}s...")
            await asyncio.sleep(delay)

    raise last  # pragma: no cover


# ---- Public functions ----
async def chat_json(
    *,
    messages: list[dict],
    model: str = LLM_MODEL,
    temperature: float = LLM_TEMPERATURE,
    top_p: float = LLM_TOP_P,
    response_schema: dict | None = None,
    timeout_s: float = LLM_TIMEOUT_S,
    seed: int | None = LLM_SEED,
    use_cache: bool = True,
    fallback_func: Callable[[], dict[str, Any]] | None = None,
) -> dict:
    """
    Force JSON response with strict schema validation.
    Returns dict on success, raises exception on failure.
    Falls back to fallback_func if provided.
    """
    if not async_client:
        raise RuntimeError("LLM client unavailable (no OPENAI_API_KEY)")

    # Force JSON schema setting
    if response_schema is None:
        rf = {"type": "json_object"}
    else:
        rf = {"type": "json_schema", "json_schema": response_schema}  # type: ignore

    key = _ckey(messages, model, temperature, rf, top_p=top_p, seed=seed)
    if use_cache:
        hit = _cache.get(key)
        if hit is not None:
            return hit

    async def _call():
        try:
            resp = await async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                response_format=rf,
                timeout=timeout_s,
                seed=seed,
            )
            txt = resp.choices[0].message.content or "{}"

            # JSON parsing attempt
            try:
                return json.loads(txt)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                logger.error(f"Raw response: {txt[:200]}...")

                # Embedded JSON extraction attempt
                import re

                json_match = re.search(r"\{.*\}", txt, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass

                # Return error on parsing failure
                raise ValueError(f"JSON parsing failed: {e!s}")

        except Exception as e:
            logger.error(f"LLM API call failed: {type(e).__name__}: {e}")
            raise

    try:
        data = await _retry_async(_call, attempts=3)
        if use_cache:
            _cache.set(key, data)
        return data

    except Exception as e:
        logger.error(f"LLM chat_json failed after retries: {type(e).__name__}: {e}")

        # Use fallback function if available
        if fallback_func:
            logger.info("Using fallback function due to LLM failure")
            try:
                fallback_result = fallback_func()
                return fallback_result
            except Exception as fallback_error:
                logger.error(f"Fallback function also failed: {fallback_error}")

        raise


# ---- Enhanced utility functions ----
def validate_config() -> dict:
    """Validate LLM configuration and return status"""
    issues = []

    if not OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY not set")

    if LLM_TEMPERATURE < 0 or LLM_TEMPERATURE > 2:
        issues.append(f"LLM_TEMPERATURE {LLM_TEMPERATURE} out of range [0, 2]")

    if LLM_TIMEOUT_S <= 0:
        issues.append(f"LLM_TIMEOUT_S {LLM_TIMEOUT_S} must be positive")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "config": {
            "model": LLM_MODEL,
            "temperature": LLM_TEMPERATURE,
            "timeout_s": LLM_TIMEOUT_S,
            "has_api_key": bool(OPENAI_API_KEY),
            "base_url": OPENAI_BASE_URL,
        },
    }


def get_client_status() -> dict:
    """Get comprehensive LLM client status"""
    config_status = validate_config()
    cache_stats = _cache.get_stats()

    return {
        "available": async_client is not None and config_status["valid"],
        "config_status": config_status,
        "cache": cache_stats,
        "clients": {"sync": sync_client is not None, "async": async_client is not None},
    }


def clear_cache():
    """Clear the cache and reset statistics"""
    _cache.store.clear()
    _cache.hits = 0
    _cache.misses = 0
    _cache.evictions = 0
    logger.info("Cache cleared and statistics reset")
