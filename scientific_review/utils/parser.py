import json
import re

def extract_json(text: str):
    text = re.sub(r"```json\s?|```", "", text).strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        candidate = match.group(0)
    else:
        candidate = text

    candidate_cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
    try:
        return json.loads(candidate_cleaned)
    except json.JSONDecodeError:
        pass

    fixed = re.sub(r"([{,])\s*'([^']+)':", r'\1 "\2":', candidate_cleaned)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        final_attempt = candidate_cleaned.replace("'", '"')
        try:
            return json.loads(final_attempt)
        except:
            raise ValueError(f"Failed to parse JSON. Raw: {text[:100]}...")
