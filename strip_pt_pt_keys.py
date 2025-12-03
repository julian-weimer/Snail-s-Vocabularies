#!/usr/bin/env python3
"""
Script to remove specific language keys from pt-pt JSON files
Removes: nl, fr, de, it, pl, ro, ru, es, uk, pt-br
"""

import sys

sys.path.insert(0, '.')

from constants import DEFAULT_CHUNK_SIZE, DEFAULT_LISTS_DIR, Language
from helpers.load_word_list import load_word_list
from helpers.save_word_objects_in_chunks import save_word_objects_in_chunks
from log import logger


def remove_language_keys(word_objects: list[dict]) -> list[dict]:
    """
    Remove specific language keys from each word object
    """
    keys_to_remove = {'nl', 'fr', 'de', 'it', 'pl', 'ro', 'ru', 'es', 'uk', 'pt-br'}

    cleaned_objects = []
    for word_obj in word_objects:
        cleaned_obj = {
            key: value
            for key, value in word_obj.items()
            if key not in keys_to_remove
        }
        cleaned_objects.append(cleaned_obj)

    return cleaned_objects


def main():
    # Load all pt-pt word objects
    logger.info("Loading pt-pt word list...")
    word_objects = load_word_list(
        language=Language.PORTUGUESE_EU,
        lists_dir=DEFAULT_LISTS_DIR,
        key_is_required=False  # Don't validate schema during load
    )

    if word_objects is False:
        logger.error("Failed to load word list")
        return 1

    logger.info(f"Loaded {len(word_objects)} word objects")

    # Remove unnecessary language keys
    logger.info("Removing language keys: nl, fr, de, it, pl, ro, ru, es, uk, pt-br...")
    cleaned_objects = remove_language_keys(word_objects)

    logger.info(f"Processed {len(cleaned_objects)} word objects")

    # Save back to files
    logger.info("Saving cleaned word objects back to pt-pt directory...")
    created_files = save_word_objects_in_chunks(
        word_objects=cleaned_objects,
        language=Language.PORTUGUESE_EU,
        lists_dir=DEFAULT_LISTS_DIR,
        chunk_size=DEFAULT_CHUNK_SIZE
    )

    logger.info(f"Successfully saved {len(created_files)} files:")
    for filepath in created_files:
        logger.info(f"  - {filepath}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
