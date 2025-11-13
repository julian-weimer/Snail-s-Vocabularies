import os
from pathlib import Path

import requests
from ratelimit import limits, sleep_and_retry

from constants import ONE_HOUR, UNSPLASH_LIMIT_PER_HOUR
from helpers.save_unsplash_image import save_unsplash_image
from log import logger


@sleep_and_retry
@limits(calls=UNSPLASH_LIMIT_PER_HOUR, period=ONE_HOUR)
def get_image_data_by_id(unsplash_id: str) -> dict | None:
    # Get the access key from environment
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        logger.error("UNSPLASH_ACCESS_KEY environment variable not set")
        return None

    headers = {"Authorization": f"Client-ID {access_key}"}

    response = requests.get(
        f"https://api.unsplash.com/photos/{unsplash_id}",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def get_image_from_unsplash(
    key: str,
    unsplash_id: str,
    output_dir: str,
) -> None:
    # Create images directory if it doesn't exist
    images_path = Path(output_dir)
    images_path.mkdir(parents=True, exist_ok=True)

    # Set up file paths
    image_file_path = images_path / f"{key}.jpg"
    metadata_file_path = images_path / f"{key}.json"

    try:
        # Fetch image data from Unsplash
        image_data = get_image_data_by_id(unsplash_id)
        if not image_data:
            logger.error(f"Failed to fetch image with ID '{unsplash_id}'")
            return

        # Save the image
        save_unsplash_image(
            image_data=image_data,
            image_file_path=str(image_file_path),
            metadata_file_path=str(metadata_file_path),
            key=key,
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch image for '{key}': {e}")
    except Exception as e:
        logger.error(f"Failed to save image for '{key}': {e}")
