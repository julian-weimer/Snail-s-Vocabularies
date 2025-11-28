from jsonschema import ValidationError, validate
from rich.progress import track

from constants import get_word_object_schema
from log import logger


def validate_word_objects(
    word_objects: list[dict], key_is_required: bool = True
) -> bool:
    schema = get_word_object_schema(key_is_required=key_is_required)

    for word_obj in track(
        word_objects, description="Validating word objects", transient=True
    ):
        try:
            validate(instance=word_obj, schema=schema)
        except ValidationError as e:
            logger.error(f"{word_obj} is not a valid word object: {e.message}")
            return False
        except Exception as e:
            logger.error(e)
            return False

    return True
