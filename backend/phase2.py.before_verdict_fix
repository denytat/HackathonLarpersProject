import logging
import os

from backend.detector import analyze_posts
from backend.services.nemotron import classify_post
from backend.services.gemini import analyze_swarm
from backend.verdict import calculate_verdict

logger = logging.getLogger(__name__)


def run_phase2(posts):
    posts = [
        p.model_dump() if hasattr(p, "model_dump") else p
        for p in posts
    ]

    result = analyze_posts(posts)

    # Phase 1 still works when AI is disabled.
    if os.getenv("ENABLE_AI", "false").lower() != "true":
        return result

    swarms = result["swarms"]
    post_results = result["posts"]

    # Only analyse posts in detected swarms.
    swarm_accounts = {
        account
        for swarm in swarms
        for account in swarm["accounts"]
    }

    post_lookup = {p["id"]: p for p in posts}
    classifications = {}
    text_cache = {}

    # Nemotron: classify each unique message only once.
    for post in posts:
        if post["account"] not in swarm_accounts:
            continue

        post_id = post["id"]
        text = post["text"]

        # Normalize whitespace and capitalization.
        cache_key = " ".join(text.split()).casefold()

        # Reuse the classification for identical messages.
        if cache_key in text_cache:
            classifications[post_id] = text_cache[cache_key]
            continue

        try:
            classification = classify_post(text)

            text_cache[cache_key] = classification
            classifications[post_id] = classification

        except Exception:
            logger.exception(
                "Nemotron classification failed for post %s",
                post_id,
            )
    # Add Nemotron results without removing existing fields.
    for post_result in post_results:
        post_id = post_result["id"]
        classification = classifications.get(post_id)

        if classification is None:
            continue

        source_text = post_lookup[post_id]["text"]
        techniques = []

        for name in classification["techniques"]:
            # Only use evidence that is actually present
            # in the original post.
            matching_evidence = next(
                (
                    item
                    for item in classification["evidence"]
                    if item and item in source_text
                ),
                "",
            )

            techniques.append({
                "name": name,
                "span": matching_evidence,
                "explanation": classification["explanation"],
            })

        post_result["techniques"] = techniques
        post_result["ai_analysis"] = {
            "status": "completed",
            "confidence": classification["confidence"],
            "explanation": classification["explanation"],
        }

        if techniques:
            post_result["flagged_by"] = sorted(
                set(post_result["flagged_by"]) | {"nemotron"}
            )

    # Gemini: one request per detected swarm.
    for swarm in swarms:
        swarm_posts = [
            post
            for post in posts
            if post["account"] in swarm["accounts"]
        ]

        gemini_result = None

        try:
            gemini_result = analyze_swarm(
                swarm,
                swarm_posts,
            )
        except Exception:
            logger.exception(
                "Gemini analysis failed for swarm %s",
                swarm["id"],
            )

        related_results = [
            item
            for item in post_results
            if post_lookup[item["id"]]["account"]
            in swarm["accounts"]
        ]

        verdict = calculate_verdict(
            swarm,
            related_results,
            gemini_result,
        )

        swarm["ai_analysis"] = {
            "status": (
                "completed"
                if gemini_result is not None
                else "unavailable"
            ),
            "gemini": gemini_result,
            "verdict": verdict["verdict"],
            "explanation": verdict["explanation"],
        }

    return result