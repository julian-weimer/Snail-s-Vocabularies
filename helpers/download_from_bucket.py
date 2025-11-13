import os

from dotenv import load_dotenv

from log import logger


def download_from_bucket(path: str) -> None:
    load_dotenv()

    bucket_name = os.getenv("GOOGLE_CLOUD_BUCKET")

    if not bucket_name:
        logger.error("GOOGLE_CLOUD_BUCKET environment variable is not set")
        return

    bucket_path = f"gs://{bucket_name}/{path}"

    logger.info(f"Downloading {bucket_path} to {path}...")

    result = os.system(f'gsutil -m rsync -r "{bucket_path}" "{path}"')

    if result == 0:
        logger.info("Download completed successfully")
    else:
        logger.error(f"Download failed with exit code {result}")
