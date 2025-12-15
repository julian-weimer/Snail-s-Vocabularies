import os

import yaml

from constants import DEFAULT_LISTS_DIR, Language
from helpers.validate_word_objects import validate_word_objects
from log import logger


def load_word_list(
    language: Language,
    lists_dir: str = DEFAULT_LISTS_DIR,
    key_is_required: bool = True,
) -> list[dict] | bool:
    lang_dir = os.path.join(lists_dir, language.value)

    if not os.path.exists(lang_dir):
        logger.error(
            f"Word list directory not found for language '{language.value}': {lang_dir}"
        )
        return False

    word_objects = []

    # Get all YAML files in the language directory and sort them
    yaml_files = sorted([f for f in os.listdir(lang_dir) if f.endswith(".yaml")])

    if not yaml_files:
        logger.error(f"No YAML files found in {lang_dir}")
        return False

    # Load each YAML file and combine the word objects
    for yaml_file in yaml_files:
        filepath = os.path.join(lang_dir, yaml_file)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                chunk = yaml.safe_load(f)
                if isinstance(chunk, list):
                    word_objects.extend(chunk)
                else:
                    logger.warning(
                        f"Expected list in {filepath}, got {type(chunk).__name__}"
                    )
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML in {filepath}: {e}")
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}", exc_info=True)

    logger.info(
        f"Loaded {len(word_objects)} words for language '{language.value}' from {len(yaml_files)} file(s)"
    )

    word_objects_is_valid = validate_word_objects(
        word_objects=word_objects, key_is_required=key_is_required
    )

    if word_objects_is_valid:
        return word_objects
    else:
        return False
