import re
from pathlib import Path

from google.cloud import texttospeech
from rich.progress import track

from constants import AI_VOICE_MAP, BCP_47_MAP, Language
from log import logger


def clean_word(text: str) -> str:
    # Remove content in parentheses
    text = re.sub(r"\s*\([^)]*\)", "", text)
    # Clean up any extra whitespace
    text = " ".join(text.split())
    return text.strip()


def get_audio_from_google_cloud_tts(
    word_objects: list[dict], language: Language, output_dir: str
) -> None:
    # Create audio directory if it doesn't exist
    audio_path = Path(output_dir)
    audio_path.mkdir(parents=True, exist_ok=True)

    # Check if language is supported with a voice
    voice_name = AI_VOICE_MAP.get(language)
    if not voice_name:
        logger.error(f"No voice mapping found for language: {language.value}")
        return

    # Get the BCP-47 language code
    language_code = BCP_47_MAP.get(language)
    if not language_code:
        logger.error(f"No BCP-47 code found for language: {language.value}")
        return

    # Instantiate a client
    client = texttospeech.TextToSpeechClient()

    # Configure audio output
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    for word_object in track(
        word_objects,
        description=f"Generating audio from Google Cloud TTS ({language.value})...",
    ):
        key = word_object.get("key")
        if not key:
            logger.warning(f"Word object missing 'key' field: {word_object}")
            continue

        # Check if audio already exists
        audio_file_path = audio_path / f"{key}.mp3"

        if audio_file_path.exists():
            logger.info(f"Audio for '{key}' already exists, skipping")
            continue

        # Get the word text in the target language
        text = word_object.get(language.value)
        if not text:
            logger.warning(
                f"No text found for key '{key}' in language '{language.value}'"
            )
            continue

        # Remove parenthetical clarifications before TTS
        clean_text = clean_word(text)
        if not clean_text:
            logger.warning(
                f"Text for key '{key}' became empty after removing clarifications"
            )
            continue

        try:
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=clean_text)

            # Build the voice request with the configured voice name
            voice = texttospeech.VoiceSelectionParams(
                name=voice_name,
                language_code=language_code,
            )

            # Perform the text-to-speech request
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            # Save the audio content to file
            with open(audio_file_path, "wb") as out:
                out.write(response.audio_content)

            logger.info(f"Audio for '{key}' generated successfully")

        except Exception as e:
            logger.error(f"Failed to generate audio for '{key}': {e}")
