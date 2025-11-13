from enum import Enum

DEFAULT_LENGTH = 2500
DEFAULT_LISTS_DIR = "./lists"
DEFAULT_DECKS_DIR = "./build"
DEFAULT_BASICS_LIST_PATH = "./basics.yaml"
DEFAULT_MEDIA_DIR = "./media"
DEFAULT_IMAGES_DIR = "images"
DEFAULT_AUDIO_DIR = "audio"
DEFAULT_TEMPLATE_PATH = "./templates/refinement_prompt.md"
DEFAULT_CHUNK_SIZE = 50
DEFAULT_TRIM_LENGTH = 0

IMAGES_DIR_NAME = "images"
AUDIO_DIR_NAME = "audio"

UNSPLASH_REFERENCE_URL = "unsplash.com/"

ONE_HOUR = 60 * 60
UNSPLASH_LIMIT_PER_HOUR = 50

TIMEOUT = 10

DEEPL_ENGLISH_SOURCE_LANG = "EN"
DEEPL_ENGLISH_TARGET_LANG = "EN-US"

GENANKI_ID = 1343927636
GENANKI_FLASHCARD_MODEL_ID = 1612251940


class ImageSource(Enum):
    UNSPLASH = "unsplash"


class WordType(Enum):
    NOUN = "noun"
    ADJECTIVE = "adjective"
    VERB = "verb"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    CONJUNCTION = "conjunction"
    PREPOSITION = "preposition"
    OTHER = "other"
    ALL = "all"


class Language(Enum):
    ARABIC = "ar"
    BANGLA = "bn"
    BOSNIAN = "bs"
    BULGARIAN = "bg"
    CATALAN = "ca"
    CHINESE = "zh"
    CROATIAN = "hr"
    CZECH = "cs"
    DANISH = "da"
    DUTCH = "nl"
    ENGLISH = "en"
    FINNISH = "fi"
    FRENCH = "fr"
    GERMAN = "de"
    GREEK = "el"
    HEBREW = "he"
    HINDI = "hi"
    HUNGARIAN = "hu"
    ICELANDIC = "is"
    INDONESIAN = "id"
    ITALIAN = "it"
    JAPANESE = "ja"
    KOREAN = "ko"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    MACEDONIAN = "mk"
    MALAY = "ms"
    NORWEGIAN = "nb"
    PERSIAN = "fa"
    POLISH = "pl"
    PORTUGUESE_EU = "pt-pt"
    PORTUGUESE_BR = "pt-br"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SERBIAN = "sr"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    SPANISH = "es"
    SWEDISH = "sv"
    TAGALOG = "fil"
    TAMIL = "ta"
    TURKISH = "tr"
    UKRAINIAN = "uk"
    URDU = "ur"
    VIETNAMESE = "vi"


BCP_47_MAP = {
    Language.ARABIC: "ar-SA",
    Language.BANGLA: "bn-BD",
    Language.BOSNIAN: "bs-BA",
    Language.BULGARIAN: "bg-BG",
    Language.CATALAN: "ca-ES",
    Language.CHINESE: "zh-CN",
    Language.CROATIAN: "hr-HR",
    Language.CZECH: "cs-CZ",
    Language.DANISH: "da-DK",
    Language.DUTCH: "nl-NL",
    Language.ENGLISH: "en-US",
    Language.FINNISH: "fi-FI",
    Language.FRENCH: "fr-FR",
    Language.GERMAN: "de-DE",
    Language.GREEK: "el-GR",
    Language.HEBREW: "he-IL",
    Language.HINDI: "hi-IN",
    Language.HUNGARIAN: "hu-HU",
    Language.ICELANDIC: "is-IS",
    Language.INDONESIAN: "id-ID",
    Language.ITALIAN: "it-IT",
    Language.JAPANESE: "ja-JP",
    Language.KOREAN: "ko-KR",
    Language.LATVIAN: "lv-LV",
    Language.LITHUANIAN: "lt-LT",
    Language.MACEDONIAN: "mk-MK",
    Language.MALAY: "ms-MY",
    Language.NORWEGIAN: "nb-NO",
    Language.PERSIAN: "fa-IR",
    Language.POLISH: "pl-PL",
    Language.PORTUGUESE_EU: "pt-PT",
    Language.PORTUGUESE_BR: "pt-BR",
    Language.ROMANIAN: "ro-RO",
    Language.RUSSIAN: "ru-RU",
    Language.SERBIAN: "sr-RS",
    Language.SLOVAK: "sk-SK",
    Language.SLOVENIAN: "sl-SI",
    Language.SPANISH: "es-ES",
    Language.SWEDISH: "sv-SE",
    Language.TAGALOG: "fil-PH",
    Language.TAMIL: "ta-IN",
    Language.TURKISH: "tr-TR",
    Language.UKRAINIAN: "uk-UA",
    Language.URDU: "ur-PK",
    Language.VIETNAMESE: "vi-VN",
}

AI_VOICE_MAP = {
    Language.ARABIC: False,
    Language.BANGLA: False,
    Language.BOSNIAN: False,
    Language.BULGARIAN: False,
    Language.CATALAN: "ca-ES-Standard-B",
    Language.CHINESE: "yue-HK-Standard-D",
    Language.CROATIAN: False,
    Language.CZECH: False,
    Language.DANISH: False,
    Language.DUTCH: False,
    Language.ENGLISH: "en-GB-Studio-C",
    Language.FINNISH: False,
    Language.FRENCH: False,
    Language.GERMAN: "de-DE-Studio-B",
    Language.GREEK: False,
    Language.HEBREW: False,
    Language.HINDI: False,
    Language.HUNGARIAN: False,
    Language.ICELANDIC: False,
    Language.INDONESIAN: False,
    Language.ITALIAN: False,
    Language.JAPANESE: False,
    Language.KOREAN: False,
    Language.LATVIAN: False,
    Language.LITHUANIAN: False,
    Language.MACEDONIAN: False,
    Language.MALAY: False,
    Language.NORWEGIAN: False,
    Language.PERSIAN: False,
    Language.POLISH: "pl-PL-Standard-G",
    Language.PORTUGUESE_EU: "pt-PT-Wavenet-F",
    Language.PORTUGUESE_BR: False,
    Language.ROMANIAN: False,
    Language.RUSSIAN: False,
    Language.SERBIAN: False,
    Language.SLOVAK: False,
    Language.SLOVENIAN: False,
    Language.SPANISH: False,
    Language.SWEDISH: False,
    Language.TAGALOG: False,
    Language.TAMIL: False,
    Language.TURKISH: False,
    Language.UKRAINIAN: False,
    Language.URDU: False,
    Language.VIETNAMESE: False,
}

SUPPORTED_LANGUAGES = [
    Language.ENGLISH,
]

WORDFREQ_LANG_MAP = {
    Language.PORTUGUESE_EU: "pt",
    Language.PORTUGUESE_BR: "pt",
}


def get_word_object_schema(key_is_required: bool = True) -> dict:
    base_required = [lang.value for lang in SUPPORTED_LANGUAGES]
    if key_is_required:
        base_required.append("key")

    return {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "word_type": {
                "enum": [
                    "noun",
                    "adjective",
                    "verb",
                    "adverb",
                    "pronoun",
                    "conjunction",
                    "preposition",
                    "other",
                ]
            },
            "plural_form": {"type": "string"},
            "gender": {"enum": ["masculine", "feminine", "neuter"]},
            "first_person_singular": {"type": "string"},
            "first_person_plural": {"type": "string"},
            "second_person_singular": {"type": "string"},
            "second_person_plural": {"type": "string"},
            "third_person_singular": {"type": "string"},
            "third_person_plural": {"type": "string"},
            "comment": {"type": "string"},
            **{lang.value: {"type": "string"} for lang in Language},
        },
        "required": base_required,
        "allOf": [
            {
                "if": {"properties": {"word_type": {"const": "verb"}}},
                "then": {
                    "required": [
                        "first_person_singular",
                        "first_person_plural",
                        "second_person_singular",
                        "second_person_plural",
                        "third_person_singular",
                        "third_person_plural",
                    ]
                },
            }
        ],
    }


def get_word_objects_array_schema(key_is_required: bool = True) -> dict:
    """Returns a JSON schema for validating an array of word objects."""
    return {
        "type": "array",
        "items": get_word_object_schema(key_is_required=key_is_required),
    }


WORD_OBJECT_SCHEMA = get_word_object_schema(key_is_required=True)
