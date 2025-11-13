import json
import os

from constants import DEFAULT_CHUNK_SIZE, Language


def save_word_objects_in_chunks(
    word_objects: list[dict],
    language: Language,
    lists_dir: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> list[str]:
    # Create language subdirectory
    lang_dir = os.path.join(lists_dir, language.value)
    os.makedirs(lang_dir, exist_ok=True)

    # Split into chunks and save
    created_files = []
    total_chunks = len(word_objects) + chunk_size - 1

    for i in range(0, len(word_objects), chunk_size):
        chunk = word_objects[i : i + chunk_size]
        chunk_number = (i // chunk_size) + 1
        filename = f"{chunk_number:03d}.json"
        filepath = os.path.join(lang_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)

        created_files.append(filepath)

    return created_files
