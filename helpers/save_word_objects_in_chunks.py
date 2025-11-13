import os

import yaml

from constants import DEFAULT_CHUNK_SIZE, Language


def save_word_objects_in_chunks(
    word_objects: list[dict],
    language: Language,
    lists_dir: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> list[str]:
    # Create directory if it doesn't exist
    os.makedirs(lists_dir, exist_ok=True)

    # Split into chunks and save
    created_files = []

    for i in range(0, len(word_objects), chunk_size):
        chunk = word_objects[i : i + chunk_size]
        chunk_number = (i // chunk_size) + 1
        filename = f"{chunk_number:03d}.yaml"
        filepath = os.path.join(lists_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(
                chunk, f, default_flow_style=False, allow_unicode=True, sort_keys=False
            )

        created_files.append(filepath)

    return created_files
