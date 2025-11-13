import os
import shutil
import uuid
from string import Template

import pyperclip
import typer
import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.traceback import install
from wordfreq import top_n_list


# Custom YAML loader that treats "on", "off", "yes", "no", "true", "false" as strings
class SafeLoader(yaml.SafeLoader):
    pass


# Remove boolean resolvers for on/off/yes/no/true/false
for ch in "OoYyNnTtFf":
    if ch in SafeLoader.yaml_implicit_resolvers:
        SafeLoader.yaml_implicit_resolvers[ch] = [
            (tag, regexp)
            for tag, regexp in SafeLoader.yaml_implicit_resolvers[ch]
            if tag != "tag:yaml.org,2002:bool"
        ]

from constants import (
    AI_VOICE_MAP,
    DEFAULT_AUDIO_DIR,
    DEFAULT_BASICS_LIST_PATH,
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
from helpers.create_deck import create_deck
from helpers.deduplicate_list import deduplicate_list
from helpers.download_from_bucket import download_from_bucket
from helpers.get_audio_from_google_cloud_tts import get_audio_from_google_cloud_tts
from helpers.get_image_from_unsplash import get_image_from_unsplash
from helpers.load_word_list import load_word_list
from helpers.save_word_objects_in_chunks import save_word_objects_in_chunks
from helpers.upload_to_bucket import upload_to_bucket
from log import logger

install(show_locals=True)

app = typer.Typer()


@app.command()
def create_list(
    language: Language,
    basics_list_path: str = DEFAULT_BASICS_LIST_PATH,
    frequency_list_length: int = DEFAULT_LENGTH,
    lists_dir: str = DEFAULT_LISTS_DIR,
) -> None:
    # Load environment variables from .env file
    load_dotenv()

    # load basics.yaml and save it in basics_list variable
    with open(basics_list_path, "r", encoding="utf-8") as f:
        basics_list = yaml.load(f, Loader=SafeLoader)

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
    lang_dir = os.path.join(lists_dir, language.value)
    created_files = save_word_objects_in_chunks(
        word_objects=word_objects,
        language=language,
        lists_dir=lang_dir,
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
def create_audio(
    language: Language,
    media_dir: str = DEFAULT_MEDIA_DIR,
    lists_dir: str = DEFAULT_LISTS_DIR,
) -> None:
    lang_dir = os.path.join(lists_dir, language.value)
    word_objects = load_word_list(language=language, lists_dir=lang_dir)

    if not word_objects:
        return

    get_audio_from_google_cloud_tts(
        word_objects=word_objects,
        language=language,
        output_dir=os.path.join(media_dir, DEFAULT_AUDIO_DIR, language.value),
    )


@app.command()
def get_images(
    language: Language,
    media_dir: str = DEFAULT_MEDIA_DIR,
    lists_dir: str = DEFAULT_LISTS_DIR,
) -> None:
    # Load word list for the language
    lang_dir = os.path.join(lists_dir, language.value)
    word_objects = load_word_list(language=language, lists_dir=lang_dir)

    if not word_objects:
        return

    # Filter for nouns only
    noun_objects = [obj for obj in word_objects if obj.get("word_type") == "noun"]

    if not noun_objects:
        logger.info("No nouns found in the word list")
        return

    images_dir = os.path.join(media_dir, DEFAULT_IMAGES_DIR)
    console = Console()

    # Import slugify for checking existing files
    from slugify import slugify

    # Track statistics
    skipped = 0
    added = 0
    skipped_by_user = 0
    total = len(noun_objects)
    processed = 0

    console.print(f"[bold]Processing {total} nouns...[/bold]\n")

    for word_object in noun_objects:
        en = word_object.get("en", "")
        if not en:
            logger.warning(f"Word object missing 'en' field: {word_object}")
            continue

        # Slugify the English word for the filename
        en_slug = slugify(en)

        # Check if image already exists
        image_filepath = os.path.join(images_dir, f"{en_slug}.jpg")
        if os.path.exists(image_filepath):
            skipped += 1
            processed += 1
            continue

        # Copy word to clipboard
        pyperclip.copy(en)

        # Calculate remaining
        processed += 1
        remaining = total - processed

        # Prompt user for Unsplash URL
        console.print(
            f"\n[bold cyan]Word ({processed}/{total}, {remaining} left):[/bold cyan] {en} [dim](copied to clipboard)[/dim]"
        )
        unsplash_url = typer.prompt(
            "Unsplash URL (or press Enter to skip)", default="", show_default=False
        )

        # Skip if user pressed Enter without input
        if not unsplash_url.strip():
            skipped_by_user += 1
            continue

        # Extract the Unsplash ID from the URL
        # URL format: https://unsplash.com/photos/{id} or https://unsplash.com/photos/{slug}-{id}
        # Unsplash IDs are always 11 characters long
        url_parts = unsplash_url.rstrip("/").split("/")
        photo_slug = url_parts[-1]
        unsplash_id = photo_slug[-11:]

        get_image_from_unsplash(
            word_object=word_object,
            unsplash_id=unsplash_id,
            output_dir=images_dir,
        )

        added += 1
        logger.info(f"Image saved for '{en}' (ID: {unsplash_id})")

    # Print summary
    console.print(
        f"\n[bold green]Summary:[/bold green] {added} added, {skipped} already exist, {skipped_by_user} skipped by user"
    )


@app.command()
def finalize_list(
    language: Language,
    lists_dir: str = DEFAULT_LISTS_DIR,
    trim: int = DEFAULT_TRIM_LENGTH,
) -> None:
    lang_dir = os.path.join(lists_dir, language.value)
    word_objects = load_word_list(
        language=language, lists_dir=lang_dir, key_is_required=False
    )

    if not word_objects:
        return

    # regenerate key
    for word_obj in word_objects:
        if "en" in word_obj:
            word_obj["key"] = str(uuid.uuid4())

    # deduplicate list
    deduplicated_word_objects = deduplicate_list(word_objects, key=language.value)

    if trim > 0:
        deduplicated_word_objects = deduplicated_word_objects[:trim]

    # recreate the language directory to clear old files
    lang_dir = os.path.join(lists_dir, language.value)
    if os.path.exists(lang_dir):
        shutil.rmtree(lang_dir)

    updated_files = save_word_objects_in_chunks(
        word_objects=deduplicated_word_objects,
        language=language,
        lists_dir=lang_dir,
    )

    logger.info(
        f"Finalized list: {len(word_objects)} → {len(deduplicated_word_objects)} words across {len(updated_files)} file(s)"
    )


@app.command()
def dump_list(
    language: Language,
    lists_dir: str = DEFAULT_LISTS_DIR,
    word_type: WordType = WordType.ALL,
) -> None:
    lang_dir = os.path.join(lists_dir, language.value)
    word_objects = load_word_list(language=language, lists_dir=lang_dir)

    if not word_objects:
        return

    # Filter by word_type if not "all"
    if word_type.value != WordType.ALL.value:
        filtered_word_objects = [
            word_obj
            for word_obj in word_objects
            if word_obj.get("word_type") == word_type.value
        ]
    else:
        filtered_word_objects = word_objects

    # Save as chunks to ./dump directory
    created_files = save_word_objects_in_chunks(
        word_objects=filtered_word_objects,
        language=language,
        lists_dir="./dump",
    )
    logger.info(
        f"Dumped {len(filtered_word_objects)} word objects across {len(created_files)} file(s) to 'dump'"
    )


@app.command(name="export-list")
def export_list(
    language: Language,
    output_file: str,
    lists_dir: str = DEFAULT_LISTS_DIR,
    word_type: WordType = WordType.ALL,
) -> None:
    lang_dir = os.path.join(lists_dir, language.value)
    word_objects = load_word_list(language=language, lists_dir=lang_dir)

    if not word_objects:
        return

    # Filter by word_type if not "all"
    if word_type.value != WordType.ALL.value:
        filtered_word_objects = [
            word_obj
            for word_obj in word_objects
            if word_obj.get("word_type") == word_type.value
        ]
    else:
        filtered_word_objects = word_objects

    # Save as single file
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(
            filtered_word_objects,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    logger.info(f"Exported {len(filtered_word_objects)} word objects to {output_file}")


@app.command(name="replace-from-dump")
def replace_from_dump(
    language: Language,
    lists_dir: str = DEFAULT_LISTS_DIR,
) -> None:
    # Load word objects from ./dump
    dump_word_objects = load_word_list(language=language, lists_dir="./dump")

    if not dump_word_objects:
        return

    # Load word objects from ./lists/[language]
    lang_dir = os.path.join(lists_dir, language.value)
    list_word_objects = load_word_list(language=language, lists_dir=lang_dir)

    if not list_word_objects:
        return

    # Create a mapping of key -> word_object from dump
    dump_map = {
        word_obj.get("key"): word_obj
        for word_obj in dump_word_objects
        if word_obj.get("key")
    }

    # Replace matching word objects
    replaced_count = 0
    for i, word_obj in enumerate(list_word_objects):
        key = word_obj.get("key")
        if key and key in dump_map:
            list_word_objects[i] = dump_map[key]
            replaced_count += 1

    # Save updated word objects back to ./lists/[language]
    lang_dir = os.path.join(lists_dir, language.value)
    if os.path.exists(lang_dir):
        shutil.rmtree(lang_dir)

    updated_files = save_word_objects_in_chunks(
        word_objects=list_word_objects,
        language=language,
        lists_dir=lang_dir,
    )

    logger.info(
        f"Replaced {replaced_count} word objects across {len(updated_files)} file(s)"
    )


@app.command(name="create-deck")
def create_deck_command(
    target_language: Language,
    decks_dir: str = DEFAULT_DECKS_DIR,
    media_dir: str = DEFAULT_MEDIA_DIR,
    lists_dir: str = DEFAULT_LISTS_DIR,
) -> None:
    lang_dir = os.path.join(lists_dir, target_language.value)
    word_objects = load_word_list(language=target_language, lists_dir=lang_dir)

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
