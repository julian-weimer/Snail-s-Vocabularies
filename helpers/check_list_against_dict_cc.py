import csv
import time
from urllib.parse import quote_plus

import requests
from diskcache import Cache
from rich.progress import track

from constants import DEFAULT_CHECK_RESULT_PATH, TIMEOUT, Language
from log import logger

# Initialize persistent cache for dict.cc lookups
_dictcc_cache = Cache(".cache/dictcc")


def check_list_against_dict_cc(
    word_objects: list[dict], check_result_path: str = DEFAULT_CHECK_RESULT_PATH
) -> None:
    not_found = []
    total_checks = 0

    for word_object in track(word_objects, description="Verifying..."):
        key = word_object.get("key", None)
        english_word = word_object.get(Language.ENGLISH.value, None)

        for lang in Language:
            lang_code = lang.value

            # Skip if this translation doesn't exist in the word object
            if lang_code not in word_object or lang_code is Language.ENGLISH.value:
                continue

            translated_word = word_object[lang_code]
            total_checks += 1

            # Strip articles before checking (German, Italian, Spanish, French, Portuguese)
            translated_word_stripped = translated_word
            articles = [
                # German
                "der ", "die ", "das ",
                # Italian
                "il ", "lo ", "la ", "l'", "i ", "gli ", "le ",
                # Spanish
                "el ", "la ", "los ", "las ",
                # French
                "le ", "la ", "l'", "les ",
                # Portuguese
                "o ", "a ", "os ", "as "
            ]
            for article in articles:
                if translated_word.lower().startswith(article):
                    translated_word_stripped = translated_word[len(article) :]
                    break

            try:
                url = f"https://en{lang_code}.dict.cc/?s={quote_plus(english_word)}"

                # Create cache key (use stripped version for checking)
                cache_key = f"{english_word}|{lang_code}|{translated_word_stripped}"

                # Check cache first
                cached_result = _dictcc_cache.get(cache_key)

                if cached_result is not None:
                    # Use cached result
                    word_found = cached_result
                else:
                    # Fetch the page with browser-like headers
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                    }
                    response = requests.get(url, headers=headers, timeout=TIMEOUT)
                    response.raise_for_status()

                    # Check if the translated word appears in the HTML (using stripped version)
                    word_found = (
                        translated_word_stripped.lower() in response.text.lower()
                    )

                    # Store in cache
                    _dictcc_cache.set(cache_key, word_found)

                    # Wait to avoid overwhelming the server (only for non-cached requests)
                    time.sleep(0.5)

                # Check if the translated word was found
                if not word_found:
                    not_found.append(
                        {
                            "key": key,
                            "english": english_word,
                            "translation": translated_word,
                            "language": lang.name,
                            "code": lang_code,
                            "url": url,
                        }
                    )
                    logger.warn(f"{translated_word} not found in {url}")
                else:
                    logger.info(f"{translated_word} found in {url}")

            except requests.RequestException as e:
                logger.error(f"Failed to verify {translated_word}: {e}")

    if not_found:
        with open(check_result_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["key", "english", "translation", "language", "code", "url"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(not_found)

        logger.info(f"CSV file created: {check_result_path}")
    else:
        logger.info("All translations verified successfully!")
