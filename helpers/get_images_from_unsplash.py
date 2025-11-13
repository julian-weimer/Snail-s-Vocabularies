import json
import os
import random
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image
from ratelimit import limits, sleep_and_retry
from rich.progress import track

from constants import (
    DEFAULT_IMAGES_DIR,
    ONE_HOUR,
    UNSPLASH_LIMIT_PER_HOUR,
    Language,
    WordType,
)
from helpers.save_unsplash_image import save_unsplash_image
from log import logger


@sleep_and_retry
@limits(calls=UNSPLASH_LIMIT_PER_HOUR, period=ONE_HOUR)
def get_images_data(query: str) -> dict | None:
    # Get the access key from environment
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        logger.error("UNSPLASH_ACCESS_KEY environment variable not set")
        return None

    headers = {"Authorization": f"Client-ID {access_key}"}
    params = {"query": query, "orientation": "squarish"}

    response = requests.get(
        "https://api.unsplash.com/search/photos",
        headers=headers,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def get_images_from_unsplash(
    word_objects: list[dict],
    output_dir: str,
) -> None:
    # Create images directory if it doesn't exist
    images_path = Path(output_dir)
    images_path.mkdir(parents=True, exist_ok=True)

    # Filter word_objects to only word_type of NOUN, VERB and ADJECTIVE
    allowed_types = {WordType.NOUN.value, WordType.VERB.value, WordType.ADJECTIVE.value}
    word_objects = [
        word_obj
        for word_obj in word_objects
        if word_obj.get("word_type") in allowed_types
    ]

    for word_object in track(
        word_objects, description="Fetching images from Unsplash..."
    ):
        key = word_object.get("key")
        if not key:
            logger.warning(f"Word object missing 'key' field: {word_object}")
            continue

        # Check if image already exists
        image_file_path = images_path / f"{key}.jpg"
        metadata_file_path = images_path / f"{key}.json"

        if image_file_path.exists() and metadata_file_path.exists():
            logger.info(f"Image for '{key}' already exists, skipping")
            continue

        try:
            query = word_object.get(Language.ENGLISH.value, key)
            data = get_images_data(query)

            # Get a random result from the first 10 search results
            results = data.get("results", [])
            if not results:
                logger.warning(f"No images found for '{key}' with query '{query}'")
                continue

            save_unsplash_image(
                image_data=results[0],
                image_file_path=image_file_path,
                metadata_file_path=metadata_file_path,
                key=key,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch image for '{key}': {e}")
        except Exception as e:
            logger.error(f"Failed to save image for '{key}': {e}")
