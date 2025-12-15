import csv
import json
import os
import shutil
import uuid
from string import Template

import typer
import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.traceback import install
from wordfreq import top_n_list

from constants import (
    AI_VOICE_MAP,
    DEFAULT_AUDIO_DIR,
    DEFAULT_BASICS_LIST_PATH,
    DEFAULT_CHECK_RESULT_PATH,
    DEFAULT_DECKS_DIR,
    DEFAULT_IMAGES_DIR,
    DEFAULT_LENGTH,
    DEFAULT_LISTS_DIR,
    DEFAULT_MEDIA_DIR,
    DEFAULT_TEMPLATE_PATH,
    DEFAULT_TRIM_LENGTH,
    SUPPORTED_LANGUAGES,
    WORDFREQ_LANG_MAP,
    Language,
    WordType,
)
from helpers.check_list_against_dict_cc import check_list_against_dict_cc
from helpers.create_deck import create_deck
from helpers.deduplicate_list import deduplicate_list
from helpers.download_from_bucket import download_from_bucket
from helpers.get_audio_from_google_cloud_tts import get_audio_from_google_cloud_tts
from helpers.get_image_from_unsplash import get_image_from_unsplash
from helpers.get_images_from_unsplash import get_images_from_unsplash
from helpers.load_word_list import load_word_list
from helpers.save_word_objects_in_chunks import save_word_objects_in_chunks
from helpers.upload_to_bucket import upload_to_bucket
from log import logger

install(show_locals=True)

app = typer.Typer()


@app.command()
def get_list(
    language: Language,
    basics_list_path: str = DEFAULT_BASICS_LIST_PATH,
    frequency_list_length: int = DEFAULT_LENGTH,
    lists_dir: str = DEFAULT_LISTS_DIR,
) -> None:
    # Load environment variables from .env file
    load_dotenv()

    # load basics.yaml and save it in basics_list variable
    with open(basics_list_path, "r", encoding="utf-8") as f:
        basics_list = yaml.safe_load(f)

    # get initial frequency list
    # wordfreq does not make a difference between european and brazilian portuguese
    wordfreq_lang = WORDFREQ_LANG_MAP.get(language, language.value)
    frequency_list = top_n_list(wordfreq_lang, frequency_list_length)

    # convert frequency list to word objects
    basics_word_objects = []
    for word in basics_list:
        word_object = {
            Language.ENGLISH.value: word.get(Language.ENGLISH.value, None),
            language.value: word.get(language.value, None),
        }
        basics_word_objects.append(word_object)

    # convert frequency list to word objects
    frequency_word_objects = []
    for word in frequency_list:
        word_object = {
            language.value: word,
        }
        frequency_word_objects.append(word_object)

    # combine basics and frequency lists
    word_objects = basics_word_objects + frequency_word_objects

    # deduplicate word_objects based on key
    word_objects = deduplicate_list(word_objects, key=language.value)

    # save the word objects in chunks of 50
    os.makedirs(lists_dir, exist_ok=True)
    created_files = save_word_objects_in_chunks(
        word_objects=word_objects,
        language=language,
        lists_dir=lists_dir,
    )

    logger.info(f"Saved {len(word_objects)} words across {len(created_files)} files")


@app.command()
def languages() -> None:
    console = Console()
    table = Table(title="Supported Languages")

    table.add_column("Language", style="cyan")
    table.add_column("Code", style="magenta")
    table.add_column("TTS Support", style="green")

    for lang in Language:
        tts_support = "✓" if AI_VOICE_MAP.get(lang) else "✗"
        table.add_row(lang.name.title(), lang.value, tts_support)

    console.print(table)


@app.command()
def get_refinement_prompt(
    language: Language,
    lists_dir: str = DEFAULT_LISTS_DIR,
    template_path: str = DEFAULT_TEMPLATE_PATH,
) -> None:
    word_list_location = os.path.join(lists_dir, f"{language.value}")

    supported_languages = ", ".join([f"`{lang.value}`" for lang in SUPPORTED_LANGUAGES])

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    template = Template(template_content)
    prompt = template.substitute(
        language_code=language.value,
        language_name=language.name.title(),
        word_list_location=word_list_location,
        supported_languages=supported_languages,
    )

    console = Console()
    console.print(prompt)


@app.command()
def create_media(
    language: Language, media_dir: str = DEFAULT_MEDIA_DIR, images: bool = False
) -> None:
    word_objects = load_word_list(language=language)

    if not word_objects:
        return

    if images:
        get_images_from_unsplash(
            word_objects=word_objects,
            output_dir=os.path.join(media_dir, DEFAULT_IMAGES_DIR),
        )

    get_audio_from_google_cloud_tts(
        word_objects=word_objects,
        language=language,
        output_dir=os.path.join(media_dir, DEFAULT_AUDIO_DIR, language.value),
    )


@app.command()
def replace_image(
    key: str, unsplash_url: str, media_dir: str = DEFAULT_MEDIA_DIR
) -> None:
    # Extract the Unsplash ID from the URL
    # URL format: https://unsplash.com/photos/{id} or https://unsplash.com/photos/{slug}-{id}
    # Unsplash IDs are always 11 characters long
    url_parts = unsplash_url.rstrip("/").split("/")
    photo_slug = url_parts[-1]
    unsplash_id = photo_slug[-11:]

    get_image_from_unsplash(
        key=key,
        unsplash_id=unsplash_id,
        output_dir=os.path.join(media_dir, DEFAULT_IMAGES_DIR),
    )

    logger.info(
        f"Image replaced for key '{key}' with Unsplash URL '{unsplash_url}' (ID: {unsplash_id})"
    )


@app.command()
def finalize_list(
    language: Language,
    lists_dir: str = DEFAULT_LISTS_DIR,
    trim: int = DEFAULT_TRIM_LENGTH,
) -> None:
    word_objects = load_word_list(language=language, key_is_required=False)

    if not word_objects:
        return

    # regenerate key
    for word_obj in word_objects:
        if "en" in word_obj:
            word_obj["key"] = str(uuid.uuid4())

    # deduplicate list
    deduplicated_word_objects = deduplicate_list(word_objects)

    if trim > 0:
        deduplicated_word_objects = deduplicated_word_objects[:trim]

    # recreate the language directory to clear old files
    lang_dir = os.path.join(lists_dir, language.value)
    if os.path.exists(lang_dir):
        shutil.rmtree(lang_dir)

    updated_files = save_word_objects_in_chunks(
        word_objects=deduplicated_word_objects,
        language=language,
        lists_dir=lists_dir,
    )

    logger.info(
        f"Finalized list: {len(word_objects)} → {len(deduplicated_word_objects)} words across {len(updated_files)} file(s)"
    )


@app.command()
def check_translations_against_dict_cc(
    language: Language, check_result_path: str = DEFAULT_CHECK_RESULT_PATH
) -> None:
    word_objects = load_word_list(language=language)

    if not word_objects:
        return

    check_list_against_dict_cc(
        word_objects=word_objects, check_result_path=check_result_path
    )


@app.command()
def dump_list(language: Language, output_file: str) -> None:
    word_objects = load_word_list(language=language)

    if not word_objects:
        return

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(word_objects, f, ensure_ascii=False, indent=2)

    logger.info(f"Dumped {len(word_objects)} word objects to {output_file}")


@app.command()
def dump_translations(
    language: Language, word_type: WordType, output_file: str
) -> None:
    word_objects = load_word_list(language=language)

    if not word_objects:
        return

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["en", "current", "new"])

        count = 0
        for word_obj in word_objects:
            english_word = word_obj.get("en")
            translation_value = word_obj.get(language.value)
            word_type_in_list = word_obj.get("word_type")

            # For word_type "all" dump all words, otherwhise filter list by word_type.
            if (translation_value and word_type.value == WordType.ALL.value) or (
                translation_value and word_type_in_list == word_type.value
            ):
                writer.writerow([english_word, translation_value, translation_value])
                count += 1

    logger.info(f"Dumped {count} translations to {output_file}")


@app.command()
def replace_translations(
    language: Language,
    input_file: str,
    lists_dir: str = DEFAULT_LISTS_DIR,
) -> None:
    word_objects = load_word_list(language=language)

    if not word_objects:
        return

    replacements = {}
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            current_translation = row["current"]
            new_translation = row["new"]
            replacements[current_translation] = new_translation

    for word_obj in word_objects:
        current_translation = word_obj.get(language.value)

        if current_translation in replacements:
            word_obj[language.value] = replacements[current_translation]

    updated_files = save_word_objects_in_chunks(
        word_objects=word_objects,
        language=language,
        lists_dir=lists_dir,
    )

    logger.info(
        f"Updated {len(replacements)} words across {len(updated_files)} file(s)"
    )


@app.command(name="create-deck")
def create_deck_command(
    target_language: Language,
    decks_dir: str = DEFAULT_DECKS_DIR,
    media_dir: str = DEFAULT_MEDIA_DIR,
) -> None:
    word_objects = load_word_list(language=target_language)

    if not word_objects:
        return

    create_deck(
        word_objects=word_objects,
        native_language=Language.ENGLISH,
        target_language=target_language,
        media_dir=media_dir,
        output_dir=os.path.join(decks_dir, target_language.value),
    )


@app.command()
def upload_media(media_dir: str = DEFAULT_MEDIA_DIR):
    upload_to_bucket(path=media_dir.lstrip("./"))


@app.command()
def download_media(media_dir: str = DEFAULT_MEDIA_DIR):
    download_from_bucket(path=media_dir.lstrip("./"))


@app.command()
def upload_decks(
    decks_dir: str = DEFAULT_DECKS_DIR,
):
    upload_to_bucket(path=decks_dir.lstrip("./"))


if __name__ == "__main__":
    app()
