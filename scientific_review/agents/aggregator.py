def aggregate(state):
    scores = state.get("scores", {})
    avg_score = sum(scores.values()) / len(scores)

    if avg_score >= 7:
        verdict = "accept"
    elif avg_score >= 4:
        verdict = "revise"
    else:
        verdict = "reject"

    return {
        "paper_id": state.get("paper_id", "unknown"),
        "mode": state.get("mode", "multiagent"),
        "scores": {
            **scores,
            "final_score": round(avg_score, 2),
        },
        "verdict": verdict,
        "strengths": state.get("strengths", []),
        "weaknesses": state.get("weaknesses", []),
        "suggestions": state.get("suggestions", []),
        "bias_risks": state.get("bias_risks", []),
        "explanations": state.get("explanations", {}),
        "criterion_comments": state.get("comments", {}),
        "review": state.get("review_final", "") or state.get("review_refined", "") or state.get("review_draft", ""),
        "review_consistency": state.get("review_consistency"),
        "agents_outputs": state.get("agents_outputs", []),
        "raw_output": state.get("raw_output"),
    }