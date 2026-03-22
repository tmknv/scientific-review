def aggregate(state):
    scores = state.get("scores", {})
    base_scores = [
        scores.get("novelty", 0),
        scores.get("scientificity", 0),
        scores.get("complexity", 0),
        scores.get("readability", 0),
    ]
    final_score = round(sum(base_scores) / 4, 2)

    scores["final_score"] = final_score

    result = {
        "paper_id": state.get("paper_id", "unknown"),
        "mode": state.get("mode", "multiagent"),
        "scores": scores,
        "review": state.get("review", ""),
        "agents_outputs": state.get("agents_outputs", []),
    }

    return result