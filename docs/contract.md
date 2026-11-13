# API contract v1

## POST /analyze

Request:
{
"posts": [
{"id": "p1", "account": "user_a", "text": "...",
"timestamp": "2026-11-13T21:00:00Z",
"reply_to": null, "image_url": null}
]
}

Response:
{
"swarms": [
{"id": "s1", "accounts": ["user_a","user_b"], "score": 0.87,
"evidence": ["14 accounts posted near-identical text within 90 seconds"]}
],
"posts": [
{"id": "p1",
"techniques": [{"name": "fear_appeal", "span": "...", "explanation": "..."}],
"verdict": "flagged | uncertain | organic",
"confidence": 0.0,
"flagged_by": ["timing", "nemotron", "gemini"]}
]
}

## GET /health -> {"status": "ok"}
