import os

import i18n
import markdown as md

# Configure i18n
i18n.load_path.append(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
)
i18n.set("filename_format", "{locale}.{format}")
i18n.set("file_format", "yaml")
i18n.set("fallback", "en")


def get_gender_addition(gender: str, locale: str = "en") -> str:
    if not gender:
        return ""

    return i18n.t(f"noun_additions.gender.{gender}", locale=locale)


def get_comment(comment: str) -> str:
    if not comment:
        return ""

    return md.markdown(comment)
