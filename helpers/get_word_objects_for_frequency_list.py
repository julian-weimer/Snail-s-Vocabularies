from constants import Language


def get_word_objects_for_frequency_list(
    words: list[str],
    language: Language,
) -> list[dict]:
    word_objects = []

    for word in words:
        word_object = {
            language.value: word,
        }
        word_objects.append(word_object)

    return word_objects
