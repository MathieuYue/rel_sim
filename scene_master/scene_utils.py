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

def history_to_str(history):
    hist_str = ""
    for row in history:
        hist_str += f"[{row[0]}]: {row[1]}\n"
    return hist_str