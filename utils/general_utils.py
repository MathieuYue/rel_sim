def history_to_str(history):
    hist_str = ""
    for row in history:
        hist_str += f"[{row[0]}]: {row[1]}\n"
    return hist_str

def list_to_indexed_string(items):

    return '\n'.join(f"{i}. {item}" for i, item in enumerate(items))

def list_to_indexed_string_1_based(items):

    return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))

def json_str_to_dict(json_str):
    """
    Converts a JSON string into a Python dictionary.
    Returns the dictionary if successful, otherwise raises ValueError.
    """
    import json
    try:
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Invalid JSON string: {e}")
