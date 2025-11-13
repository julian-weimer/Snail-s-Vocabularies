def deduplicate_list(word_objects: list[dict], key: str = "key") -> list[dict]:
    seen = set()
    deduplicated = []

    for word_obj in word_objects:
        value = word_obj.get(key, "")
        if value and value not in seen:
            seen.add(value)
            deduplicated.append(word_obj)

    return deduplicated
