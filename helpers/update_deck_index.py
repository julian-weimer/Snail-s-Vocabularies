import json
import os

from log import logger


def update_deck_index(
    index_path: str,
    native_language_code: str,
    target_language_code: str,
    deck_path: str,
) -> None:
    index = {}
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Could not parse {index_path}, creating new index")
            index = {}

    index_key = f"{native_language_code}_{target_language_code}"

    index[index_key] = deck_path

    native_languages = index.get("native_languages", None)
    target_languages = index.get("target_languages", None)

    if native_languages == None:
        native_languages = []

    if native_language_code not in native_languages:
        native_languages.append(native_language_code)

    if target_languages == None:
        target_languages = []

    if target_language_code not in target_languages:
        target_languages.append(target_language_code)

    index["native_languages"] = native_languages
    index["target_languages"] = target_languages

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    logger.info(f"Updated deck index: {index_key} -> {deck_path}")
