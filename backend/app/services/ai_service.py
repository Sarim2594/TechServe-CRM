import logging
import os
from collections.abc import Iterable
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

AI_CATEGORIES = ("Billing", "Technical", "Account", "Shipping", "Refund", "General")
AI_SENTIMENTS = ("Positive", "Neutral", "Negative", "Frustrated")

CATEGORY_KEYWORDS = {
    "Refund": ("refund", "reimburse", "money back", "duplicate payment", "chargeback"),
    "Billing": ("bill", "invoice", "payment", "charge", "price", "subscription"),
    "Technical": ("error", "bug", "broken", "crash", "slow", "install", "server", "dashboard"),
    "Account": ("account", "login", "log in", "password", "sign in", "access", "profile"),
    "Shipping": ("delivery", "deliver", "shipment", "shipping", "tracking", "package"),
}
FRUSTRATED_WORDS = (
    "angry",
    "frustrated",
    "terrible",
    "unacceptable",
    "urgent",
    "immediately",
    "many times",
    "nothing works",
)
NEGATIVE_WORDS = ("problem", "issue", "error", "failed", "broken", "cannot", "can't", "refund")
POSITIVE_WORDS = ("thanks", "thank you", "great", "helpful", "appreciate", "resolved")


def classify_ticket(title: str, description: str) -> str:
    prompt = (
        "Classify this customer support ticket. Reply with exactly one category from: "
        f"{', '.join(AI_CATEGORIES)}.\nTitle: {title}\nDescription: {description}"
    )
    provider_result = _generate_text("ticket classification", prompt, max_output_tokens=20)
    return _validated_label(provider_result, AI_CATEGORIES) or _rule_based_category(title, description)


def analyze_sentiment(title: str, description: str) -> str:
    prompt = (
        "Classify the customer's tone. Reply with exactly one sentiment from: "
        f"{', '.join(AI_SENTIMENTS)}.\nTitle: {title}\nDescription: {description}"
    )
    provider_result = _generate_text("sentiment analysis", prompt, max_output_tokens=20)
    return _validated_label(provider_result, AI_SENTIMENTS) or _rule_based_sentiment(title, description)


def suggest_response(ticket: object, customer: object, comments: Iterable[object]) -> str:
    title = getattr(ticket, "title", "Support request")
    description = getattr(ticket, "description", "")
    category = getattr(ticket, "ai_category", None) or getattr(ticket, "category", None) or "General"
    priority = getattr(ticket, "priority", "Medium")
    customer_name = getattr(customer, "full_name", "there")
    company = getattr(customer, "company", None) or "Not provided"
    comment_context = _comment_context(comments)
    prompt = (
        "Draft a concise, professional customer-service reply. Acknowledge the issue, explain that the "
        "support team is reviewing it, and state a helpful next step. Do not expose internal notes or invent "
        "a completed fix. Keep it under 140 words.\n"
        f"Customer: {customer_name}\nCompany: {company}\nTicket title: {title}\n"
        f"Description: {description}\nCategory: {category}\nPriority: {priority}\n"
        f"Internal context: {comment_context}"
    )
    provider_result = _generate_text("reply suggestion", prompt, max_output_tokens=220)
    if provider_result:
        return provider_result
    article = "an" if category[:1].lower() in "aeiou" else "a"
    return (
        f"Hello {customer_name}, thank you for contacting TechServe Solutions. "
        f"I am sorry you are experiencing an issue with {title.lower()}. "
        f"We have recorded this as {article} {category.lower()} request with {priority.lower()} priority, "
        "and our support team is reviewing the details. We will update you with the next step as soon as possible. "
        "Kind regards, TechServe Solutions Support"
    )


def summarize_ticket(ticket: object, comments: Iterable[object]) -> str:
    comments = list(comments)
    title = getattr(ticket, "title", "Support request")
    description = getattr(ticket, "description", "")
    status = getattr(ticket, "status", "Unknown")
    category = getattr(ticket, "ai_category", None) or getattr(ticket, "category", None) or "General"
    prompt = (
        "Summarize this support ticket for an internal CRM record. Keep it factual, concise, and under 90 words. "
        "Mention the issue, current status, category, and notable updates without inventing a resolution.\n"
        f"Title: {title}\nDescription: {description}\nStatus: {status}\nCategory: {category}\n"
        f"Updates: {_comment_context(comments)}"
    )
    provider_result = _generate_text("conversation summary", prompt, max_output_tokens=150)
    if provider_result:
        return provider_result
    summary = f"{title}. Category: {category}. Current status: {status}. Logged updates: {len(comments)}."
    if comments:
        summary += f" Latest update: {getattr(comments[-1], 'message', '')[:180]}"
    return summary


def _rule_based_category(title: str, description: str) -> str:
    lowered = f"{title} {description}".lower()
    scores = {
        category: sum(keyword in lowered for keyword in keywords)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] else "General"


def _rule_based_sentiment(title: str, description: str) -> str:
    lowered = f"{title} {description}".lower()
    if any(word in lowered for word in FRUSTRATED_WORDS):
        return "Frustrated"
    negative_score = sum(word in lowered for word in NEGATIVE_WORDS)
    positive_score = sum(word in lowered for word in POSITIVE_WORDS)
    if negative_score > positive_score:
        return "Negative"
    if positive_score > negative_score:
        return "Positive"
    return "Neutral"


def _comment_context(comments: Iterable[object]) -> str:
    messages = [getattr(comment, "message", "").strip()[:300] for comment in comments]
    messages = [message for message in messages if message]
    return " | ".join(messages[-5:]) or "No updates logged."


def _validated_label(value: str | None, allowed_values: tuple[str, ...]) -> str | None:
    if not value:
        return None
    lowered = value.strip().lower()
    for allowed_value in allowed_values:
        if lowered == allowed_value.lower():
            return allowed_value
    logger.warning("AI provider returned an invalid structured label: %s", value)
    return None


def _generate_text(task: str, prompt: str, max_output_tokens: int) -> str | None:
    provider = os.getenv("AI_PROVIDER", "rule_based").strip().lower()
    if provider == "fallback":
        provider = "rule_based"
    if provider == "rule_based":
        return None

    api_key = os.getenv("AI_API_KEY", "").strip()
    if not api_key:
        logger.info("AI provider '%s' has no API key. Using rule-based fallback for %s.", provider, task)
        return None

    try:
        if provider == "openai":
            return _openai_text(api_key, prompt, max_output_tokens)
        if provider == "gemini":
            return _gemini_text(api_key, prompt)
        logger.warning("Unknown AI provider '%s'. Using rule-based fallback for %s.", provider, task)
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
        logger.warning("AI provider '%s' failed for %s. Using rule-based fallback: %s", provider, task, exc)
    return None


def _openai_text(api_key: str, prompt: str, max_output_tokens: int) -> str:
    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "input": prompt,
            "max_output_tokens": max_output_tokens,
        },
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"].strip()
    output_parts = [
        content.get("text", "")
        for item in payload.get("output", [])
        for content in item.get("content", [])
        if content.get("type") == "output_text"
    ]
    result = "".join(output_parts).strip()
    if not result:
        raise ValueError("OpenAI response did not include text output")
    return result


def _gemini_text(api_key: str, prompt: str) -> str:
    model = quote(os.getenv("GEMINI_MODEL", "gemini-1.5-flash").removeprefix("models/"), safe="")
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    result = "".join(
        part.get("text", "")
        for candidate in payload.get("candidates", [])
        for part in candidate.get("content", {}).get("parts", [])
    ).strip()
    if not result:
        raise ValueError("Gemini response did not include text output")
    return result
