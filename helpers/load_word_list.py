import os

import yaml

from constants import Language
from helpers.validate_word_objects import validate_word_objects
from log import logger


# Custom YAML loader that treats "on", "off", "yes", "no", "true", "false" as strings
class SafeLoader(yaml.SafeLoader):
    pass


# Remove boolean resolvers for on/off/yes/no/true/false
for ch in "OoYyNnTtFf":
    if ch in SafeLoader.yaml_implicit_resolvers:
        SafeLoader.yaml_implicit_resolvers[ch] = [
            (tag, regexp)
            for tag, regexp in SafeLoader.yaml_implicit_resolvers[ch]
            if tag != "tag:yaml.org,2002:bool"
        ]


def load_word_list(
    language: Language,
    lists_dir: str,
    key_is_required: bool = True,
) -> list[dict] | bool:
    if not os.path.exists(lists_dir):
        logger.error(
            f"Word list directory not found for language '{language.value}': {lists_dir}"
        )
        return False

    word_objects = []

    # Get all YAML files in the directory and sort them
    yaml_files = sorted([f for f in os.listdir(lists_dir) if f.endswith(".yaml")])

    if not yaml_files:
        logger.error(f"No YAML files found in {lists_dir}")
        return False

    # Load each YAML file and combine the word objects
    for yaml_file in yaml_files:
        filepath = os.path.join(lists_dir, yaml_file)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                chunk = yaml.load(f, Loader=SafeLoader)
                if isinstance(chunk, list):
                    word_objects.extend(chunk)
                else:
                    logger.warning(
                        f"Expected list in {filepath}, got {type(chunk).__name__}"
                    )
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}", exc_info=True)

    logger.info(
        f"Loaded {len(word_objects)} words from {len(yaml_files)} file(s) ('{lists_dir}')"
    )

    word_objects_is_valid = validate_word_objects(
        word_objects=word_objects, key_is_required=key_is_required
    )

    if word_objects_is_valid:
        return word_objects
    else:
        return False
