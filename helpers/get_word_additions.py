import os

import i18n

# Configure i18n
i18n.load_path.append(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
)
i18n.set("filename_format", "{locale}.{format}")
i18n.set("file_format", "yaml")
i18n.set("fallback", "en")


def get_adjective_additions(word_object: dict, locale: str = "en") -> str:
    positive = word_object.get("positive", "")
    comparative = word_object.get("comparative", "")
    superlative = word_object.get("superlative", "")

    # Return empty string if comparative or superlative forms are not present
    if not comparative or not superlative:
        return ""

    html_parts = ['<dl class="additions">']

    label = i18n.t("adjective_additions.positive", locale=locale)
    html_parts.append(f"  <dt>{label}</dt>\n  <dd>{positive}</dd>")

    label = i18n.t("adjective_additions.comparative", locale=locale)
    html_parts.append(f"  <dt>{label}</dt>\n  <dd>{comparative}</dd>")

    label = i18n.t("adjective_additions.superlative", locale=locale)
    html_parts.append(f"  <dt>{label}</dt>\n  <dd>{superlative}</dd>")

    html_parts.append("</dl>")

    return "\n".join(html_parts)


def get_verb_additions(word_object: dict, locale: str = "en") -> str:
    first_person_singular = word_object.get("first_person_singular", "")
    first_person_plural = word_object.get("first_person_plural", "")
    second_person_singular = word_object.get("second_person_singular", "")
    second_person_plural = word_object.get("second_person_plural", "")
    third_person_singular = word_object.get("third_person_singular", "")
    third_person_plural = word_object.get("third_person_plural", "")

    # Return empty string if none of the conjugations are present
    if not any(
        [
            first_person_singular,
            first_person_plural,
            second_person_singular,
            second_person_plural,
            third_person_singular,
            third_person_plural,
        ]
    ):
        return ""

    html_parts = ['<dl class="additions">']

    if first_person_singular:
        label = i18n.t("verb_additions.first_person_singular", locale=locale)
        html_parts.append(f"  <dt>{label}</dt>\n  <dd>{first_person_singular}</dd>")

    if first_person_plural:
        label = i18n.t("verb_additions.first_person_plural", locale=locale)
        html_parts.append(f"  <dt>{label}</dt>\n  <dd>{first_person_plural}</dd>")

    html_parts.append("</dl>")
    html_parts.append('<dl class="additions">')

    if second_person_singular:
        label = i18n.t("verb_additions.second_person_singular", locale=locale)
        html_parts.append(f"  <dt>{label}</dt>\n  <dd>{second_person_singular}</dd>")

    if second_person_plural:
        label = i18n.t("verb_additions.second_person_plural", locale=locale)
        html_parts.append(f"  <dt>{label}</dt>\n  <dd>{second_person_plural}</dd>")

    html_parts.append("</dl>")
    html_parts.append('<dl class="additions">')

    if third_person_singular:
        label = i18n.t("verb_additions.third_person_singular", locale=locale)
        html_parts.append(f"  <dt>{label}</dt>\n  <dd>{third_person_singular}</dd>")

    if third_person_plural:
        label = i18n.t("verb_additions.third_person_plural", locale=locale)
        html_parts.append(f"  <dt>{label}</dt>\n  <dd>{third_person_plural}</dd>")

    html_parts.append("</dl>")

    return "\n".join(html_parts)


def get_plural_form_addition(plural_form: str, locale: str = "en") -> str:
    if not plural_form:
        return ""

    # Get the localized abbreviation for "plural"
    plural_abbr = i18n.t("noun_additions.plural_form", locale=locale)

    return f'<div class="plural-form">{plural_form}  <span class="info">{plural_abbr}</span></div>'


def get_gender_addition(gender: str, locale: str = "en") -> str:
    if not gender:
        return ""

    # Get the localized abbreviation for the gender
    gender_abbr = i18n.t(f"noun_additions.gender.{gender}", locale=locale)

    return f'<span class="info">{gender_abbr}</span>'


def get_comment(comment: str) -> str:
    if not comment:
        return ""

    return f"""<div class="comment">
  <div class="info-icon">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="24 24 208 208" fill="currentColor"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm-4,48a12,12,0,1,1-12,12A12,12,0,0,1,124,72Zm12,112a16,16,0,0,1-16-16V128a8,8,0,0,1,0-16,16,16,0,0,1,16,16v40a8,8,0,0,1,0,16Z"/></svg>
  </div>
  <div class="comment-content">{comment}</div>
</div>"""
