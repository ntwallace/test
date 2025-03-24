
def generate_cache_key(*key_parts: str) -> str:
    return "::".join(key_parts)
