import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    if not text or not text.strip():
        raise ValueError("Empty text: cannot extract JSON")

    cleaned = text.strip()

    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    candidates: list[str] = [cleaned]

    obj_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if obj_match:
        candidates.insert(0, obj_match.group(0))

    arr_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if arr_match:
        candidates.insert(0, arr_match.group(0))

    for candidate in candidates:
        candidate_cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
        variants = [
            candidate_cleaned,
            candidate_cleaned.replace("'", '"'),
        ]
        for variant in variants:
            try:
                return json.loads(variant)
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Failed to parse JSON. Raw text starts with: {text[:200]!r}")
