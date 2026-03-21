def aggregate(state):
    scores = state.scores

    if not scores:
        raise ValueError("No scores to aggregate")

    final_score = sum(scores.values()) / len(scores)

    if final_score >= 7:
        verdict = "accept"
    elif final_score >= 4:
        verdict = "revise"
    else:
        verdict = "reject"

    result = {
        "scores": {
            **scores,
            "final_score": round(final_score, 2),
        },
        "explanations": state.explanations,
        "review": state.review_final or "",
        "verdict": verdict,
        "agents_outputs": state.agent_outputs,
    }

    return result
