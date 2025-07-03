def list_to_indexed_string(items):

    return '\n'.join(f"{i}. {item}" for i, item in enumerate(items))
