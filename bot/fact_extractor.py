import json
import re
import logging
import inspect
import time
import socket
import os
from typing import Any, Dict, List, Optional

try:
    import ollama
except Exception:  # pragma: no cover - allow import failure when testing without ollama
    ollama = None

# Try to import Ollama-specific ConnectionError if available, otherwise fall back to Exception
OllamaConnectionError = Exception
try:
    if ollama is not None:
        from ollama._client import ConnectionError as OllamaConnectionError  # type: ignore
except Exception:
    OllamaConnectionError = Exception


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are SYSTEMIC NEWS FACT ENGINE.

You are not a news writer.
You are an investigative journalist and fact checker.

Your only goal is to discover the truth.

Rules:

• Never invent facts.
• Never guess.
• Ignore opinions.
• Ignore speculation.
• Ignore clickbait.
• If multiple trusted sources agree, treat it as verified.
• If sources disagree, record the disagreement.
• If something is unknown, say it is unknown.
• Preserve dates, names, numbers and locations exactly.

Return ONLY valid JSON.
"""


USER_PROMPT = """
Study every article carefully.

Do NOT summarize.

Investigate.

Return ONLY valid JSON with the following fields:

headline

verified_facts

unknown_facts

conflicting_reports

timeline

people

organizations

locations

countries

numbers

quotes

causes

effects

next_events

confidence

Rules:

- Every verified fact must be supported by multiple trusted sources.
- Never invent information.
- Never guess.
- If information is missing, put it in unknown_facts.
- Return ONLY JSON.
"""

OUTPUT_SCHEMA: Dict[str, Any] = {
    "headline": "",
    "verified_facts": [],
    "unknown_facts": [],
    "conflicting_reports": [],
    "timeline": [],
    "people": [],
    "organizations": [],
    "locations": [],
    "countries": [],
    "numbers": [],
    "quotes": [],
    "causes": [],
    "effects": [],
    "next_events": [],
    "confidence": 0,
}


def validate_articles(articles: Any) -> List[Dict[str, Any]]:
    """Ensure articles is a list of dicts and normalize missing keys.

    Each article will be normalized to include at least: source, title, text, score.
    """
    if not isinstance(articles, list):
        raise TypeError("articles must be a list of dicts")

    normalized: List[Dict[str, Any]] = []
    for art in articles:
        if not isinstance(art, dict):
            continue
        normalized.append({
            "source": str(art.get("source", "unknown")),
            "title": str(art.get("title", "")),
            "text": str(art.get("text", "")),
            "score": float(art.get("score", 0)) if art.get("score") is not None else 0.0,
        })

    return normalized


def build_context(articles: List[Dict[str, Any]]) -> str:
    """Build a plain-text context containing all articles for the LLM prompt."""
    parts: List[str] = []

    for i, article in enumerate(articles, start=1):
        parts.append("""
ARTICLE {idx}

SOURCE:
{source}

TITLE:
{title}

TEXT:
{text}

------------------------------------
""".strip().format(
            idx=i,
            source=article.get("source", "unknown"),
            title=article.get("title", ""),
            text=article.get("text", ""),
        ))

    return "\n\n".join(parts)


def source_agreement(articles: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count how many articles come from each source."""
    counts: Dict[str, int] = {}
    for article in articles:
        source = article.get("source", "unknown")
        counts[source] = counts.get(source, 0) + 1
    return counts


def trusted_sources(articles: List[Dict[str, Any]], threshold: float = 95.0) -> List[Dict[str, Any]]:
    """Return articles whose score is >= threshold."""
    return [a for a in articles if a.get("score", 0) >= threshold]


def estimate_confidence(articles: List[Dict[str, Any]]) -> int:
    """Estimate a confidence score (0-100) based on number of trusted sources and average score.

    This is a heuristic. The minimum is 0 when there are no articles.
    """
    if not articles:
        return 0

    trusted_count = len(trusted_sources(articles))
    avg_score = sum(a.get("score", 0) for a in articles) / len(articles)

    # Start from a baseline of 40, add 6 points per trusted source, and weight by avg_score
    conf = int(min(100, 40 + trusted_count * 6 + (avg_score - 50) * 0.2))
    return max(0, conf)


# --- New helper utilities for robust Ollama usage ---

def _ollama_is_running(host: str = "localhost", port: int = 11434, timeout: float = 1.0) -> bool:
    """Quick TCP check to see if Ollama daemon is reachable."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _call_ollama_chat(client, *args, timeout: Optional[int] = None, max_retries: int = 3, **kwargs):
    """
    Call client.chat defensively:
      - only pass `timeout` kwarg if client's chat() accepts it (works across client versions)
      - retry on connection/transient errors
    """
    params = dict(kwargs)

    # add timeout only if available in signature
    try:
        sig = inspect.signature(client.chat)
        if timeout is not None and 'timeout' in sig.parameters:
            params['timeout'] = timeout
    except Exception:
        # skip if introspection fails
        pass

    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            return client.chat(*args, **params)
        except TypeError as e:
            # If TypeError caused by unsupported kwarg (timeout), remove it and retry once
            if 'timeout' in params:
                logger.warning("Ollama client.chat doesn't accept 'timeout'; removing and retrying.")
                params.pop('timeout', None)
                continue
            raise
        except OllamaConnectionError as e:
            last_exc = e
            logger.warning("Ollama connection error (attempt %d/%d): %s", attempt, max_retries, e)
            time.sleep(2 ** (attempt - 1))
        except Exception as e:
            last_exc = e
            logger.warning("Ollama unexpected error (attempt %d/%d): %s", attempt, max_retries, e)
            time.sleep(2 ** (attempt - 1))

    # Raise the last connection-related exception for the caller to handle
    raise OllamaConnectionError("Failed to call Ollama after retries.") from last_exc


# --- End helpers ---


def extract_facts(
    articles: List[Dict[str, Any]], model: str = "llama3.1", timeout: Optional[int] = None
) -> str:
    """Call the LLM to extract facts and return the raw assistant text.

    Requires the `ollama` package and a running Ollama service. If ollama is not available,
    this function raises a RuntimeError to make failures explicit. In CI, if SKIP_OLLAMA is set
    or the Ollama daemon is not reachable, this function will return an empty string so callers
    can continue without failing the whole job.
    """
    articles = validate_articles(articles)
    context = build_context(articles)

    if ollama is None:
        raise RuntimeError(
            "ollama package is not available. Install and configure Ollama or mock extract_facts in tests."
        )

    # CI / test guard: allow skipping Ollama in environments where it's not running
    if os.getenv('SKIP_OLLAMA', '').lower() == 'true' or (os.getenv('CI') and not _ollama_is_running()):
        logger.info("SKIP_OLLAMA enabled or Ollama not reachable; returning empty extraction.")
        return ""

    try:
        response = _call_ollama_chat(
            ollama,
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT + "\n\n" + context},
            ],
            timeout=timeout,
        )

        # Ollama's client may return different shapes; accept dict-like responses.
        if isinstance(response, dict):
            # Try common keys
            if "message" in response and isinstance(response["message"], dict):
                return response["message"].get("content", "")
            return response.get("content", "") or ""

        # If it's a simple object with str(), return that
        return str(response)

    except Exception as exc:
        logger.exception("Failed to call LLM: %s", exc)
        # Instead of raising, return an empty string so callers can continue and enrich with metadata
        return ""


JSON_BLOCK_RE = re.compile(r"```json\s*(\{[\s\S]*?\})\s*```|(```\s*(\{[\s\S]*?\})\s*```)|(^\s*(\{[\s\S]*?\})\s*$)", re.MULTILINE)


def parse_facts(text: str) -> Dict[str, Any]:
    """Extract the first JSON object from text and return it as a dict.

    If parsing fails, returns a copy of OUTPUT_SCHEMA.
    """
    if not text:
        return OUTPUT_SCHEMA.copy()

    text = text.strip()

    # Try to find a JSON block inside markdown fences or raw text
    match = JSON_BLOCK_RE.search(text)
    candidate = None
    if match:
        # match groups may vary depending on which alternative matched
        for g in match.groups():
            if g and g.strip().startswith("{"):
                candidate = g.strip()
                break

    if candidate is None:
        # As a fallback try to find the first { ... } balanced JSON by searching braces
        # This is a simple heuristic and not a full parser.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]

    if candidate is None:
        return OUTPUT_SCHEMA.copy()

    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
        # If it's not a dict (e.g., a list), wrap into schema where appropriate
        return {**OUTPUT_SCHEMA.copy(), "verified_facts": parsed}

    except json.JSONDecodeError:
        logger.exception("Failed to decode JSON from LLM output. Returning empty schema.")
        return OUTPUT_SCHEMA.copy()


def print_fact_statistics(facts: Dict[str, Any]) -> None:
    print()
    print("========== FACT SHEET ==========")
    print("Verified :", len(facts.get("verified_facts", [])))
    print("Unknown  :", len(facts.get("unknown_facts", [])))
    print("Conflicts:", len(facts.get("conflicting_reports", [])))
    print("Timeline :", len(facts.get("timeline", [])))
    print("Confidence:", facts.get("confidence", 0))
    print("Sources  :", facts.get("sources", {}))
    print("===============================")
    print()


def build_fact_sheet(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """High-level helper: extract facts from articles and return a normalized facts dict.

    This calls the LLM (extract_facts), parses the returned text, and enriches the
    result with confidence and source agreement information.
    """
    articles = validate_articles(articles)

    raw = ""
    try:
        raw = extract_facts(articles)
    except Exception as exc:
        # Do not crash the whole process if the LLM call fails; return an empty schema with metadata
        logger.exception("LLM extraction failed: %s", exc)

    facts = parse_facts(raw)

    # Enrich with computed metadata
    facts["confidence"] = estimate_confidence(articles)
    facts["sources"] = source_agreement(articles)

    print_fact_statistics(facts)

    return facts


if __name__ == "__main__":
    # Example usage that does not call the LLM by default. Replace or configure as needed.
    sample_articles = [
        {
            "source": "Example News",
            "title": "Sample headline",
            "text": "A sample event happened on 2026-08-05 in City X.",
            "score": 98,
        },
        {
            "source": "Other News",
            "title": "Another report",
            "text": "Report confirming details about the sample event.",
            "score": 96,
        },
    ]

    # Demonstrate parse_facts with a canned JSON string so this file is runnable without Ollama.
    demo_json = json.dumps({
        "headline": "Sample headline",
        "verified_facts": ["Sample event on 2026-08-05"],
        "unknown_facts": [],
        "conflicting_reports": [],
        "timeline": [],
        "people": [],
        "organizations": [],
        "locations": [],
        "countries": [],
        "numbers": [],
        "quotes": [],
        "causes": [],
        "effects": [],
        "next_events": [],
        "confidence": 100,
    }, indent=2)

    parsed = parse_facts(f"```json\n{demo_json}\n```")
    parsed["confidence"] = estimate_confidence(sample_articles)
    parsed["sources"] = source_agreement(sample_articles)

    print_fact_statistics(parsed)
    print("Fact sheet (short):", {k: parsed[k] for k in ("headline", "confidence")})
