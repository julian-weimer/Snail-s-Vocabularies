# Snail's Vocabularies 🐌

> [!NOTE]  
> The word lists may contain errors.

Free [Anki](https://apps.ankiweb.net/) vocabulary decks for various languages.

This repository includes a toolkit to create and manage vocabulary lists, as well as the lists themselves. The official decks are available [here](https://snailsvocabularies.cool).

## Motivation

I personally find that learning vocabulary is a good entry point to any new language. [Anki](https://apps.ankiweb.net/) is a tool that not only takes advantage of spaced repetition for improved memory retention, but also breaks down long lists of words into manageable chunks and tracks your sessions.

For some, manually creating personal decks can be part of their learning journey, but I always preferred having a ready-made deck so I could just start learning right away.

## Features

- A deck includes 1,500 words consisting of a universal foundational list and a selection of dictionary words derived from a [frequency list](https://github.com/rspeer/wordfreq/) unique to each language
- A CLI-based toolkit to create and manage vocabulary decks
- AI-generated sounds for each word*
- Images sourced from [Unsplash](https://unsplash.com) for nouns*
- Fancy card design featuring a snail*

\*The media files and the card templates are not part of the repository

The foundational list is based on the following sources:
- [Basic English List](https://en.wikipedia.org/wiki/Basic_English)
- [Swadesh List](https://en.wikipedia.org/wiki/Swadesh_list)
- My own judgement inspired by a [comment](https://www.reddit.com/r/languagelearning/comments/rrhqr5/comment/hqhxszd/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) on Reddit

## How to create a new deck using the toolkit

### 1. Create a list

Create a raw list with `create-list` (example: `python toolkit.py create-list fr`). Choose any language that is supported by the toolkit. To get an overview of the supported languages, use `languages` (example: `python toolkit.py languages`).

This will merge a foundational list (see `basics.yaml`) with a frequency list and save it in the `lists` folder by default. The entire list will be saved in chunks as YAML to be more easily processed by an LLM.

Next, you will use an LLM to refine the raw YAML files. Get a prompt for your target language using `get-refinement-prompt` (example: `python toolkit.py get-refinement-prompt fr`).

Finally, use `finalize-list` (example: `python toolkit.py finalize-list fr`) to finalize your list. It will check the list for structural errors and deduplicate it. You can trim a list with the `--trim` argument (example: `python toolkit.py finalize-list fr --trim 1500`).

### 2. Create media

Use `get-images` (example: `python toolkit.py get-images fr`) to fetch images from [Unsplash](https://unsplash.com) and `create-audio` (example: `python toolkit.py create-audio fr`) to generate audio files using [Google Cloud TTS](https://cloud.google.com/text-to-speech). The files will be stored in the `media` folder by default.

`UNSPLASH_ACCESS_KEY` must be set as an environment variable. You can also use a `.env` file in the project root directory.

To use [Google Cloud TTS](https://cloud.google.com/text-to-speech), you must be authenticated using `gcloud auth`.

### 3. Create the deck

To generate the deck, use `create-deck` (example: `python toolkit.py create-deck fr`).

## Theming

In the `templates` folder you can find `card-answer.html.example` and `card-question.html.example`. Remove the `.example` suffix and use regular HTML and CSS to style your cards.

If you include a `common.css` file in the templates folder, it will be prepended to the `<style>` tags of each card template.

## License

This repository is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0).
