import json
from io import BytesIO

import requests
from PIL import Image

from log import logger


def save_unsplash_image(image_data: dict, image_file_path: str, metadata_file_path: str, key: str) -> None:
    # Get image URL and author info
    image_url = image_data["urls"]["full"]
    author = image_data["user"]["username"]

    # Download the image
    image_response = requests.get(image_url, timeout=30)
    image_response.raise_for_status()

    # Open image with PIL
    img = Image.open(BytesIO(image_response.content))

    # Crop image to 1024x1024 (centered without distortion)
    width, height = img.size

    # Determine the shorter side to create a square crop
    min_dimension = min(width, height)

    # Calculate crop box (centered)
    left = (width - min_dimension) // 2
    top = (height - min_dimension) // 2
    right = left + min_dimension
    bottom = top + min_dimension

    # Crop to square
    img_cropped = img.crop((left, top, right, bottom))

    # Resize to 1024x1024
    img_resized = img_cropped.resize((1024, 1024), Image.Resampling.LANCZOS)

    # Save the image
    img_resized.save(image_file_path, "JPEG", quality=90)

    # Save metadata
    metadata = {"author": author, "source": "unsplash"}

    with open(metadata_file_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Created image for '{key}' (author: {author})")
