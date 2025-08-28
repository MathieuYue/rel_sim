def scenes_to_array(scenes_json):
    """
    Converts the content of scenes.json (as loaded from JSON) into an array of arrays,
    where each inner array represents the list of scenes for a progression step.
    The input should be a dict with keys "0", "1", ..., "N".
    """
    # Collect all keys that are digit strings, sort them numerically
    step_keys = sorted(
        (k for k in scenes_json.keys() if k.isdigit()),
        key=lambda x: int(x)
    )
    scenes_array = []
    for key in step_keys:
        scenes_array.append(scenes_json.get(key, []))
    return scenes_array

def list_to_string(lst):
    """
    Converts a list of items to a string, joining elements with a line break.
    Elements are converted to strings if they are not already.
    """
    return "\n".join(str(item) for item in lst)


from typing import Iterable, List, Dict, Union

Scenario = Dict[str, object]

import random

def find_scenarios_by_category(
    scenarios: Iterable[Scenario],
    categories: Union[str, Iterable[str]],
    *,
    match: str = "exact",          # "exact" | "contains" | "prefix"
    ignore_case: bool = True
) -> List[Scenario]:
    if isinstance(categories, str):
        targets = [categories]
    else:
        targets = list(categories)

    # normalize targets
    if ignore_case:
        targets_norm = [t.casefold() for t in targets]
    else:
        targets_norm = targets

    matched_scenarios = []
    for sc in scenarios:
        cat = sc.get("category")
        if not isinstance(cat, str):
            continue
        cat_norm = cat.casefold() if ignore_case else cat

        matched = False
        for t in targets_norm:
            if match == "exact" and cat_norm == t:
                matched = True
                break
            elif match == "contains" and t in cat_norm:
                matched = True
                break
            elif match == "prefix" and cat_norm.startswith(t):
                matched = True
                break

        if matched:
            matched_scenarios.append(sc)
    # Randomly sample up to 10 results
    if len(matched_scenarios) > 10:
        return random.sample(matched_scenarios, 10)
    else:
        return matched_scenarios


# rel_sim/util/json_utils.py
import json, re
from json import JSONDecodeError

def extract_braced_json(text: str) -> str:
    """Strip code fences and extract the first {...} block."""
    s = text.strip()
    # remove ```json ... ``` fences if present
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.DOTALL)
    # grab outermost { ... } (greedy to include nested braces)
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    return m.group(0) if m else s

def parse_llm_json(text: str):
    raw = extract_braced_json(text)
    try:
        return json.loads(raw)
    except JSONDecodeError as e:
        # Common fixups: convert single quotes to double, remove trailing commas
        fixed = raw
        # 1) If it looks like a Python dict (single quotes), try a careful transform
        if "'" in fixed and '"' not in fixed.split("\n", 1)[0]:
            # cautious replace: keys/values guarded; this is a heuristic
            fixed = re.sub(r"(?<!\\)'", '"', fixed)  # replace unescaped single quotes with double
        # 2) Remove trailing commas before } or ]
        fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
        try:
            return json.loads(fixed)
        except JSONDecodeError:
            # Last resort: if you fully control the source and trust it, you can try ast.literal_eval.
            # Safer to just raise with context if you don't trust input.
            snippet = raw[:400].replace("\n", "\\n")
            raise JSONDecodeError(f"Failed to parse LLM JSON. Start of payload: {snippet}", raw, e.pos)
