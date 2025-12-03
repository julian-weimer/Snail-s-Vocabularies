# Snail's Vocabularies 🐌

> [!NOTE]  
> The word lists are still incomplete or may contain errors.

Free [Anki](https://apps.ankiweb.net/) vocabulary decks or a variety of languages.

This repository includes a toolkit to create and manage vocabulary lists, as well as the lists themselves. The official decks are available [here](https://snailsvocabularies.cool).

## Motivation

I personally find that learning vocabulary is a good entry point to any new language. [Anki](https://apps.ankiweb.net/) is a tool that not only takes advantage of spaced repetition for improved memory retention, but also breaks down long lists of words into manageable chunks and tracks your sessions.

For some, manually creating personal decks can be part of their learning journey, but I always preferred having a ready-made deck so I could just start learning right away.

Wouldn't it be great to have high-quality vocabulary decks that are not behind any subscriptions and freely accessible to everyone?

## Features

- Each deck includes 1,500 words consisting of a universal foundational list and a selection of dictionary words derived from a [frequency list](https://github.com/rspeer/wordfreq/) unique to each language
- Support 11 languages (see [Project Status](#project-status) for details)
- A CLI-based toolkit to create and manage vocabulary decks
- AI-generated sounds for each word*
- Images sourced from [Unsplash](https://unsplash.com) for nouns*
- Fancy card design featuring a snail*

\*Not included in this repository

The foundational list is based on the following sources:
- [Basic English List](https://en.wikipedia.org/wiki/Basic_English)
- [Swadesh List](https://en.wikipedia.org/wiki/Swadesh_list)
- My own judgement inspired by a [comment](https://www.reddit.com/r/languagelearning/comments/rrhqr5/comment/hqhxszd/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) on Reddit

## Project Status

|       | Status   |
| ----- | -------- |
| nl    | -        |
| en    | -        |
| fr    | -        |
| de    | -        |
| it    | -        |
| pl    | -        |
| pt-br | -        |
| pt-pt | ✅       |
| ro    | -        |
| ru    | -        |
| es    | -        |
| uk    | -        |

## How to create a new deck using the toolkit

### 1. Create a list

Create a raw list with `get-list` (example: `python toolkit.py get-list fr`). Choose any language that is currently supported by the toolkit. To get an overview of the supported languages, use `languages` (example: `python toolkit.py languages`).

This will merge a foundational list (see `basics.json`) with a frequency list and save it in the `lists` folder by default. The entire list will be saved in chunks as JSON to be more easily processed by an LLM.

Next, you will use an LLM (Claude Sonnet 4.5 or similar quality) to refine the raw JSON files. Get a prompt for your target language using `get-refinement-prompt` (example: `python toolkit.py get-refinement-prompt fr`).

Finally, use `finalize-list` (example: `python toolkit.py finalize-list fr`) to finalize your list. It will check the list for structural errors and deduplicate it. You can trim a list with the `--trim` argument (example: `python toolkit.py finalize-list fr --trim 1500`).

### 2. Create media

Use `create-media` (example: `python toolkit.py create-media fr`) to fetch images from [Unsplash](https://unsplash.com) and generate audio files using [Google Cloud TTS](https://cloud.google.com/text-to-speech). The files will be stored in the `media` folder by default.

`UNSPLASH_ACCESS_KEY` must be set as an environment variable. You can also use a `.env` file in the project root directory.

To use [Google Cloud TTS](https://cloud.google.com/text-to-speech), you must be authenticated using `gcloud auth`.

### 3. Create the deck

To generate the deck, use `create-deck` (example: `python toolkit.py create-deck de fr`).

## Theming

In the `templates` folder you can find `card-answer.html.example` and `card-question.html.example`. Remove the `.example` suffix and use regular HTML and CSS to style your cards.

If you include a `common.css` file in the templates folder, it will be prepended to the `<style>` tags of each card template.

## How to improve the content quality

As you might have noticed, the project heavily relies on AI for translations and other data. To ensure the quality of the decks, it will be necessary to spot mistakes, improve translations manually, and find better-fitting images.

### Vocabulary lists

All lists are part of the repository and can be found as JSON files in the `lists` folder. Edit them directly.

It is fine to replace words, the goal is to create lists of words which are most useful in each language.

After any edit, run `finalize-list` (example: `python toolkit.py finalize-list fr`).

To manage translations more effectively, the toolkit provides the following commands:
- Use `dump-translations` (example: `python toolkit.py dump-translations fr all fr.csv`). Use the `new` column for your corrections.
- Use `replace-translations` (example: `python toolkit.py replace-translations fr fr.csv`) to apply your changes across all chunks.

### Media files

The media files for the [official decks](https://snailsvocabularies.cool) are managed by me. Feel free to open an issue for suggestions.

## License

This repository is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0).
