from jsonschema import ValidationError, validate

from constants import get_word_objects_array_schema
from log import logger


def validate_word_objects(
    word_objects: list[dict], key_is_required: bool = True
) -> bool:
    schema = get_word_objects_array_schema(key_is_required=key_is_required)

    try:
        validate(instance=word_objects, schema=schema)
        return True
    except ValidationError as e:
        # Extract the path to the problematic item to provide better error messages
        if e.path:
            item_index = list(e.path)[0] if e.path else "unknown"
            word_obj = (
                word_objects[item_index]
                if isinstance(item_index, int) and item_index < len(word_objects)
                else {}
            )
            logger.error(
                f"Validation error at index {item_index}: {e.message}\nObject: {word_obj}"
            )
        else:
            logger.error(f"Validation error: {e.message}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        return False
