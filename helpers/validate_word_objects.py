from jsonschema import ValidationError, validate

from constants import WORD_OBJECT_SCHEMA
from log import logger


def validate_word_objects(word_objects: list[dict]) -> bool:
    for i, word_obj in enumerate(word_objects):
        try:
            validate(instance=word_obj, schema=WORD_OBJECT_SCHEMA)
        except ValidationError as e:
            logger.error(f"{word_obj} is not a valid word object: {e.message}")
            return False
        except Exception as e:
            logger.error(e)
            return False

    return True
