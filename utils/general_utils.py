def history_to_str(history):
    hist_str = ""
    for row in history:
        hist_str += f"[{row[0]}]: {row[1]}\n"
    return hist_str

def list_to_indexed_string(items):

    return '\n'.join(f"{i}. {item}" for i, item in enumerate(items))

def list_to_indexed_string_1_based(items):

    return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))

def read_all_j2_prompts(folder_path):
    """
    Reads all .j2 prompt files in the given folder and returns a dictionary
    mapping filenames to their contents.
    """
    import os
    prompts = {}
    if not os.path.isdir(folder_path):
        return prompts
    for filename in os.listdir(folder_path):
        if filename.endswith(".j2"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                prompts[filename] = f.read()
    return prompts
