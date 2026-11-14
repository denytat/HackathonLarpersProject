def calculate_verdict(swarm, post_results=None, gemini_result=None):
    """
    Assess swarm-level coordination conservatively.

    Coordinated activity is not proof of malicious intent.
    This function must never flag individual posts as malicious.
    """
    score = float(swarm.get("score", 0))

    signals = set()

    for edge in swarm.get("evidence", []):
        signals.update(edge.get("signals", {}).keys())

    has_multiple_signals = len(signals) >= 2

    if has_multiple_signals and score >= 0.75:
        verdict = "coordinated_activity"
        explanation = (
            "Multiple independent algorithmic signals support "
            "coordinated activity. This does not establish "
            "malicious intent or prove that the content is false."
        )
    else:
        verdict = "uncertain"
        explanation = (
            "Some coordination indicators were found, but the "
            "available evidence is insufficient for a stronger "
            "swarm-level conclusion."
        )

    if gemini_result is not None:
        explanation += " Gemini analysis is available for review."

    return {
        "verdict": verdict,
        "explanation": explanation,
        "score": score,
    }
