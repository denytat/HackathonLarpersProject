def calculate_verdict(swarm, post_results, gemini_result=None):
    """
    Conservative assessment based on available evidence.
    Model output is supporting context, not proof of intent.
    """
    score = float(swarm.get("score", 0))

    signals = set()
    for edge in swarm.get("evidence", []):
        signals.update(edge.get("signals", {}).keys())

    has_multiple_signals = len(signals) >= 2

    if not has_multiple_signals:
        verdict = "uncertain"
        explanation = "Insufficient independent coordination signals."
    elif score >= 0.75:
        verdict = "coordinated_activity"
        explanation = (
            "Multiple algorithmic signals support possible "
            "coordination. Malicious intent is not established."
        )
    else:
        verdict = "suspicious"
        explanation = (
            "Multiple coordination indicators were detected, "
            "but the evidence is not conclusive."
        )

    if gemini_result:
        explanation += " Gemini analysis is available for review."

    return {
        "verdict": verdict,
        "explanation": explanation,
        "score": score,
    }