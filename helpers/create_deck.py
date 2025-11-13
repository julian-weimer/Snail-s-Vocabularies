import os

import genanki
import i18n
from slugify import slugify

from constants import (
    DEFAULT_AUDIO_DIR,
    GENANKI_FLASHCARD_MODEL_ID,
    GENANKI_ID,
    Language,
)
from helpers.get_image_source import get_image_source
from helpers.get_word_additions import (
    get_adjective_additions,
    get_comment,
    get_gender_addition,
    get_plural_form_addition,
    get_verb_additions,
)
from helpers.update_deck_index import update_deck_index
from log import logger

# Configure i18n
i18n.load_path.append(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
)
i18n.set("filename_format", "{locale}.{format}")
i18n.set("file_format", "yaml")
i18n.set("fallback", "en")


def load_template(template_name: str) -> str:
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates", f"{template_name}.html"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Inject common css if the template contains styles
    if "<style>" in content:
        design_tokens = get_common_css()
        content = content.replace("<style>", f"<style>\n{design_tokens}")

    return content


def get_common_css() -> str:
    tokens_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates", "common.css"
    )
    if not os.path.exists(tokens_path):
        return ""
    with open(tokens_path, "r", encoding="utf-8") as f:
        return f.read()


FLASHCARD_MODEL = genanki.Model(
    model_id=GENANKI_FLASHCARD_MODEL_ID,
    name="Flashcard Model",
    fields=[
        {"name": "native_word"},
        {"name": "target_word"},
        {"name": "word_type"},
        {"name": "sound"},
        {"name": "image"},
        {"name": "dl"},
        {"name": "gender"},
        {"name": "plural_form"},
        {"name": "image_source"},
        {"name": "comment"},
    ],
    templates=[
        {
            "name": "Vocabulary",
            "qfmt": load_template("card-question"),
            "afmt": load_template("card-answer"),
        },
    ],
)


def create_deck(
    word_objects: list[dict],
    native_language: Language,
    target_language: Language,
    media_dir: str,
    output_dir: str,
) -> None:
    deck_title_key = f"deck_titles.deck_title_{target_language.value}"
    translated_title = i18n.t(deck_title_key, locale=native_language.value)

    # Fallback title
    if translated_title == deck_title_key:
        translated_title = f"{native_language.value}_{target_language.value}"

    deck = genanki.Deck(GENANKI_ID, translated_title + " 🐌")

    audio_dir = os.path.join(media_dir, DEFAULT_AUDIO_DIR, target_language.value)
    images_dir = os.path.join(media_dir, "images")

    package = genanki.Package(deck)
    package.media_files = []

    for word_object in word_objects:
        key = word_object.get("key")
        native_word = word_object.get(native_language.value)
        target_word = word_object.get(target_language.value)
        word_type = word_object.get("word_type")
        plural_form = word_object.get("plural_form")
        gender = word_object.get("gender")
        comment_text = word_object.get("comment", "")
        en = word_object.get("en", "")

        if not native_word or not target_word:
            logger.error(
                f"{word_object} does not include {native_language.value} and {target_language.value}."
            )
            return

        translated_word_type = i18n.t(
            f"word_types.{word_type}", locale=native_language.value
        )

        audio_filepath = os.path.join(audio_dir, f"{key}.mp3")
        audio_filename = f"{key}.mp3"

        # Check if audio file exists
        sound_field = ""
        if os.path.exists(audio_filepath):
            sound_field = f"[sound:{audio_filename}]"
            package.media_files.append(audio_filepath)
        else:
            logger.warning(f"Audio file not found: {audio_filepath}")

        # Slugify the English word for the image filename
        en_slug = slugify(en) if en else "unknown"

        # Check if image file exists with format: {en_slug}.jpg
        image_filepath = os.path.join(images_dir, f"{en_slug}.jpg")
        image_filename = f"{en_slug}.jpg"
        image_field = ""
        if os.path.exists(image_filepath):
            image_field = f'<img src="{image_filename}">'
            package.media_files.append(image_filepath)
        else:
            logger.warning(f"Image file not found: {image_filepath}")

        # Get image source attribution
        image_source_snippet = get_image_source(en_slug, images_dir)

        # Get additions based on word type
        dl_snippet = ""
        gender_snippet = ""
        plural_form_snippet = ""
        if word_type == "noun":
            gender_snippet = get_gender_addition(gender, native_language.value)
            plural_form_snippet = get_plural_form_addition(
                plural_form, native_language.value
            )
        elif word_type == "adjective":
            dl_snippet = get_adjective_additions(word_object, native_language.value)
        elif word_type == "verb":
            dl_snippet = get_verb_additions(word_object, native_language.value)

        # Get comment snippet
        comment_snippet = get_comment(comment_text)

        note = genanki.Note(
            model=FLASHCARD_MODEL,
            fields=[
                native_word,
                target_word,
                translated_word_type,
                sound_field,
                image_field,
                dl_snippet,
                gender_snippet,
                plural_form_snippet,
                image_source_snippet,
                comment_snippet,
            ],
        )
        deck.add_note(note)

    os.makedirs(output_dir, exist_ok=True)

    filename = slugify(translated_title)
    output_path = os.path.join(output_dir, f"{filename}.apkg")
    package.write_to_file(output_path)

    logger.info(f"Deck created: {output_path}")

    # Update the deck index
    decks_base_dir = os.path.dirname(output_dir)
    index_path = os.path.join(decks_base_dir, "index.json")

    relative_deck_path = os.path.relpath(output_path, decks_base_dir)

    update_deck_index(
        index_path=index_path,
        native_language_code=native_language.value,
        target_language_code=target_language.value,
        deck_path=relative_deck_path,
    )
