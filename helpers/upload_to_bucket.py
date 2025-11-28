import os

from dotenv import load_dotenv

from log import logger


def upload_to_bucket(path: str) -> None:
    load_dotenv()

    bucket_name = os.getenv("GOOGLE_CLOUD_BUCKET")

    if not bucket_name:
        logger.error("GOOGLE_CLOUD_BUCKET environment variable is not set")
        return

    bucket_path = f"gs://{bucket_name}/{path}"

    logger.info(f"Uploading {path} to {bucket_path}...")

    result = os.system(f'gsutil -m rsync -r "{path}" "{bucket_path}"')

    if result == 0:
        logger.info("Upload completed successfully")
    else:
        logger.error(f"Upload failed with exit code {result}")
