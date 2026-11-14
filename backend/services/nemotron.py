import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ["NEMOTRON_BASE_URL"],
    api_key=os.environ["VERDA_INFERENCE_KEY"],
    timeout=30.0,
)

ALLOWED_TECHNIQUES = {
    "repetitive_messaging",
    "hashtag_spamming",
    "narrative_amplification",
    "emotional_manipulation",
    "impersonation",
    "misleading_claims",
}


def classify_post(text: str) -> dict:
    if not text.strip():
        return {
            "techniques": [],
            "confidence": 0.0,
            "explanation": "Empty post.",
            "evidence": [],
        }

    response = client.chat.completions.create(
        model=os.environ["NEMOTRON_MODEL"],
        messages=[
            {
                "role": "system",
                "content": """
You are a social media content analyst.

Classify the supplied post using ONLY these techniques:
- repetitive_messaging
- hashtag_spamming
- narrative_amplification
- emotional_manipulation
- impersonation
- misleading_claims

Important:
- A single post cannot establish coordination.
- Ordinary political opinions are not automatically manipulation.
- Do not invent facts or external context.
- If evidence is insufficient, return an empty techniques list.
- Only classify techniques supported by the supplied text.

Return ONLY a valid JSON object with:
{
  "techniques": [],
  "confidence": 0.0,
  "explanation": "Short explanation",
  "evidence": []
}

Confidence must be between 0 and 1.
Do not include Markdown or extra text.
""",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.1,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Nemotron returned an empty response.")

    # Remove Markdown fences if the model includes them.
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        content = content.rsplit("```", 1)[0].strip()

    result = json.loads(content)

    if not isinstance(result, dict):
        raise ValueError("Nemotron must return a JSON object.")

    techniques = result.get("techniques")
    confidence = result.get("confidence")
    explanation = result.get("explanation")
    evidence = result.get("evidence")

    if not isinstance(techniques, list):
        raise ValueError("Invalid techniques list.")

    if not all(
        isinstance(t, str) and t in ALLOWED_TECHNIQUES
        for t in techniques
    ):
        raise ValueError("Nemotron returned unknown techniques.")

    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        raise ValueError("Invalid confidence value.")

    if not isinstance(explanation, str):
        raise ValueError("Invalid explanation.")

    if not isinstance(evidence, list) or not all(
        isinstance(item, str) for item in evidence
    ):
        raise ValueError("Invalid evidence list.")

    return {
        "techniques": techniques,
        "confidence": float(confidence),
        "explanation": explanation,
        "evidence": evidence,
    }