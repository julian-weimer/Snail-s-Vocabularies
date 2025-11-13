# Word List Refinement

Let's refine a word list in a YAML file.

First of all, let's clean the YAML file:
- Remove all word objects that include words which appear wrong, such as numeric digits (Example: Remove 1,2,3.. and keep one, two, three...) or single-letter words that don't exist in $language_name. Make sure to reference the $language_code key for this action. If a word does not seem to be part of $language_name, remove the corresponding word object as well.
- Remove word objects which reference a human name, currencies, company or service names, and cities.

Let's add translations next:
- All word objects should include the following keys: $supported_languages, each with the corresponding translation.
- All translations should have the same meaning.
- For some languages the word might be ambiguous. In this case, add a simple clarification in parentheses. Example: press (media)
- All translations should be dictionary words. Lemmatize the word in `$language_code` if it is not a dictionary word.
- Capitalize nouns if $language_name requires it.
- Add a key called `word_type`, its value should be one of `noun`, `adjective`, `verb`, `adverb`, `pronoun`, `conjunction`, `preposition` or `other`.
- All English verbs should include 'to'. Example: to run
- All nouns should be in singular form
- All verbs should be in infinitive form
- All adjectives should be in positive form (not comparative and not superlative)

Your next task will be to expand each word object with new keys depending on `word_type`.

## word_type: noun

Add articles to the nouns in the $language_code key if $language_name is one of these languages (for example, "Katze" would become "die Katze" in German). Capitalize the noun if it is necessary for $language_name. Don't add "the" for English:
- catalan
- danish
- dutch
- english
- french
- german
- greek
- italian
- macedonian
- norwegian
- portuguese
- romanian
- spanish
- swedish

Add the `plural_form` key with the plural form of the noun if $language_name is one of these languages and if the noun is countable:
- catalan
- danish
- dutch
- english
- french
- german
- italian
- norwegian
- portuguese
- spanish
- swedish

Add a short explanation in English of plural usage to a `comment` key if $language_name is one of the following languages (example: '2-4: [plural form]; 5+: [another plural form]'). The languages below don't need a `plural_form` key:
- russian
- ukrainian
- polish
- czech
- croatian

Add a `gender` key with one of the following values: `masculine`, `feminine`, `neuter` if $language_name is one of these languages:
- catalan
- croatian
- czech
- dutch
- french
- german
- greek
- italian
- lithuanian
- macedonian
- polish
- portuguese
- romanian
- russian
- spanish
- ukrainian

## word_type: verb

Add the following keys including the corresponding conjugation of the verb if it is in present tense. Add the pronoun and capitalize it if it is common to do so in $language_name (example: "Ich gehe" in German):
- `first_person_singular`
- `first_person_plural`
- `second_person_singular`
- `second_person_plural`
- `third_person_singular`
- `third_person_plural`

Only add the keys if $language_name is one of these languages:
- catalan
- croatian
- czech
- danish
- dutch
- english
- finnish
- french
- german
- greek
- italian
- lithuanian
- macedonian
- norwegian
- polish
- portuguese
- romanian
- russian
- spanish
- swedish
- ukrainian

Add a `perfective` key and fill it with the perfective form of the verb if $language_name is one of these languages:
- polish
- russian
- ukrainian

Add a `perfective` key and fill it with the perfective form of the verb if $language_name is one of these languages:
- polish
- russian
- ukrainian

## word_type: adjective

Add these keys including the corresponding word or expression if the adjective has a comparative or superlative form:
- `positive`
- `comparative`
- `superlative`

## Other word types

Don't add any additional keys.

Thank you ❤️
