import json
import os

from constants import UNSPLASH_REFERENCE_URL, ImageSource


def get_image_source(en_slug: str, images_dir: str) -> str:
    json_filepath = os.path.join(images_dir, f"{en_slug}.json")

    if not os.path.exists(json_filepath):
        return ""

    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        source = data.get("source", "")
        author = data.get("author", "")

        if source == ImageSource.UNSPLASH.value and author:
            return f"{UNSPLASH_REFERENCE_URL}@{author}"

        return ""

    except (json.JSONDecodeError, IOError):
        return ""
