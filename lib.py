import json
import re
import requests

from space_containing import *
from name_gen import *

version = "2.1.1"
api_url = "http://localhost:10000/api"
url_pattern = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
si_pattern = r"s(äp|eyk|äpeyk)?(iv|ol|er|am|ìm|ìy|ay|ilv|irv|imv|iyev|ìyev|alm|ìlm|ìly|aly|arm|ìrm|ìry|ary|ìsy|asy)?(eiy|äng|eng|uy|ats)?i"
paren_pattern = r"(\(.+\))"
char_limit = 2000


def format_ipa(word: dict) -> str:
    return word['IPA']


def do_underline(stressed: str, syllables: str) -> str:
    syllables = syllables.replace(" ", "-")
    if "-" not in syllables:
        return syllables
    s0 = int(stressed) - 1
    s1 = syllables.split("-")
    if s0 >= 0 and s0 < len(s1):
        s1[s0] = f"__{s1[s0]}__"
        return '-'.join(s1)
    return syllables


def format_breakdown(word: dict) -> str:
    breakdown = do_underline(word['Stressed'], word['Syllables'])
    if word['InfixDots'] != "NULL":
        breakdown += f", {word['InfixDots']}"
    return breakdown


def format_prefixes(word: dict) -> str:
    results = ""
    len_pre_list = ["me", "pxe", "ay", "fay",
                    "tsay", "fray", "pe", "pem", "pep", "pay"]
    prefixes = word['Affixes']['Prefix']
    if prefixes is not None and len(prefixes) > 0:
        results += "      prefixes: "
        for k, prefix in enumerate(prefixes):
            if k != 0:
                results += ", "
            if prefix in len_pre_list:
                results += f"**{prefix}**+"
            else:
                results += f"**{prefix}**-"
        results += "\n"
    return results


def format_infixes(word: dict) -> str:
    results = ""
    infixes = word['Affixes']['Infix']
    if infixes is not None and len(infixes) > 0:
        results += "      infixes: "
        for k, infix in enumerate(infixes):
            if k != 0:
                results += ", "
            results += f"<**{infix}**>"
        results += "\n"
    return results


def format_suffixes(word: dict) -> str:
    results = ""
    suffixes = word['Affixes']['Suffix']
    if suffixes is not None and len(suffixes) > 0:
        results += "      suffixes: "
        for k, suffix in enumerate(suffixes):
            if k != 0:
                results += ", "
            results += f"-**{suffix}**"
        results += "\n"
    return results


def format_lenition(word: dict) -> str:
    results = ""
    lenition = word['Affixes']['Lenition']
    if lenition is not None and len(lenition) > 0:
        results += "      lenition: "
        for k, lenite in enumerate(lenition):
            if k != 0:
                results += ", "
            results += f"{lenite}"
        results += "\n"
    return results


def format_source(response_text: str) -> str:
    word = json.loads(response_text)
    if isinstance(word, dict) and "message" in word:
        return word["message"]
    results = ""
    for i in range(1, len(word) + 1):
        w = word[i - 1]
        if w['Source'] is None:
            results += f"[{i}] **{w['Navi']}**: no source results\n"
        else:
            w['Source'] = re.sub(url_pattern, r"<\1>", w['Source'])
            results += f"[{i}] **{w['Navi']}** @ {w['Source']}\n"
    return results


def format_audio(response_text: str) -> str:
    word = json.loads(response_text)
    if isinstance(word, dict) and "message" in word:
        return word["message"]
    results = ""
    for i in range(1, len(word) + 1):
        w = word[i - 1]
        syllables = do_underline(w['Stressed'], w['Syllables'])
        results += f"[{i}] **{w['Navi']}** ({syllables}) :speaker: [click here to listen](https://s.learnnavi.org/audio/vocab/{w['ID']}.mp3)\n"
    return results


def format(response_text: str, languageCode: str, showIPA: bool = False) -> str:
    words = json.loads(response_text)
    if isinstance(words, dict) and "message" in words:
        return words["message"]
    results = ""
    for i in range(1, len(words) + 1):
        word = words[i - 1]
        ipa = format_ipa(word)
        breakdown = format_breakdown(word)
        if showIPA:
            results += f"[{i}] **{word['Navi']}** [{ipa}] ({breakdown}) *{word['PartOfSpeech']}* {word[languageCode.upper()]}\n"
        else:
            results += f"[{i}] **{word['Navi']}** ({breakdown}) *{word['PartOfSpeech']}* {word[languageCode.upper()]}\n"
        results += format_prefixes(word)
        results += format_infixes(word)
        results += format_suffixes(word)
        results += format_lenition(word)
    if len(results) > char_limit:
        return f"{len(words)} results. please search a more specific list, or use /random with number and same args"
    return results


def get_naive_plural_en(word_en: str) -> str:
    if word_en == 'stomach':
        return 'stomachs'
    endings_es = ['s', 'x', 'z', 'sh', 'ch']
    for ending in endings_es:
        if word_en.endswith(ending):
            return f"{word_en}es"
    return f"{word_en}s"


def format_translation(response_text: str, languageCode: str) -> str:
    words = json.loads(response_text)
    if isinstance(words, dict) and "message" in words:
        return "(?)"
    results = ""
    root_index = -1
    for i, word in enumerate(words):
        prefixes = word['Affixes']['Prefix']
        infixes = word['Affixes']['Infix']
        suffixes = word['Affixes']['Suffix']
        lenition = word['Affixes']['Lenition']
        if prefixes is None and infixes is None and suffixes is None and lenition is None:
            root_index = i
            break
    if root_index != -1:
        word = words[root_index]
        definition = f"{word[languageCode.upper()]}"
        definition_clean = re.sub(paren_pattern, "", definition)
        results += f"{definition_clean}"
    else:
        for i in range(len(words)):
            word = words[i]
            if i != 0:
                results += " / "
            definition = f"{word[languageCode.upper()]}"
            definition_clean = re.sub(paren_pattern, "", definition)
            prefixes = word['Affixes']['Prefix']
            if prefixes is not None:
                if "fì" in prefixes:
                    definition_clean = f"this {definition_clean}"
                elif "tsa" in prefixes:
                    definition_clean = f"that {definition_clean}"
                elif "fay" in prefixes:
                    definition_clean = f"these {get_naive_plural_en(definition_clean)}"
                elif "tsay" in prefixes:
                    definition_clean = f"those {get_naive_plural_en(definition_clean)}"
                elif "fra" in prefixes:
                    definition_clean = f"every {definition_clean}"
                elif "fray" in prefixes:
                    definition_clean = f"all {get_naive_plural_en(definition_clean)}"
            results += f"{definition_clean}"
    return results


def format_version(response_text: str) -> str:
    version_info = json.loads(response_text)
    version_text = "```\n"
    version_text += f"slash-fwew: {version}\n"
    version_text += f"fwew-api:   {version_info['APIVersion']}\n"
    version_text += f"fwew-lib:   {version_info['FwewVersion']}\n"
    version_text += f"dictionary: {version_info['DictVersion']}\n"
    version_text += "```"
    return version_text


def format_number(response_text: str) -> str:
    number = json.loads(response_text)
    if isinstance(number, dict) and "message" in number:
        return number["message"]
    name = number["name"]
    octal = number["octal"]
    decimal = number["decimal"]
    return f"**na'vi**: {name} | **octal**: {octal} | **decimal**: {decimal}"


def get_word_bundles(words: str) -> list[str]:
    result = []
    for pattern in patterns:
        words = re.sub(pattern, r'"\1"', words)
    yy = [c for c in re.split(r'("\w+ \w+\s?\w*")', words) if len(c) > 0]
    for w in yy:
        if w.startswith('"') and w.endswith('"'):
            result.append(w[1:-1])
        else:
            result.extend(w.split())
    result = [r for r in result if r != '"']
    return result


def get_fwew(languageCode: str, words: str, showIPA: bool = False) -> str:
    results = ""
    word_list = get_word_bundles(words)
    for i, word in enumerate(word_list):
        if i != 0:
            results += "\n"
        word = word_list[i]
        res = requests.get(f"{api_url}/fwew/{word}")
        text = res.text
        results += format(text, languageCode, showIPA)
    return results


def get_fwew_reverse(languageCode: str, words: str, showIPA: bool = False) -> str:
    results = ""
    word_list = words.split()
    for i, word in enumerate(word_list):
        if i != 0:
            results += "\n"
        word = word_list[i]
        res = requests.get(f"{api_url}/fwew/r/{languageCode.lower()}/{word}")
        text = res.text
        results += format(text, languageCode, showIPA)
    return results


def get_profanity(lang: str, showIPA: bool) -> str:
    words = "skxawng kalweyaveng kurkung pela'ang pxasìk teylupil tsahey txanfwìngtu vonvä' wiya"
    return get_fwew(lang, words, showIPA)


def get_source(words: str) -> str:
    results = ""
    word_list = get_word_bundles(words)
    for i, word in enumerate(word_list):
        if i != 0:
            results += "\n"
        word = word_list[i]
        res = requests.get(f"{api_url}/fwew/{word}")
        text = res.text
        results += format_source(text)
    return results


def get_audio(words: str) -> str:
    results = ""
    word_list = get_word_bundles(words)
    for i, word in enumerate(word_list):
        if i != 0:
            results += "\n"
        word = word_list[i]
        res = requests.get(f"{api_url}/fwew/{word}")
        text = res.text
        results += format_audio(text)
    return results


def get_list(languageCode: str, args: str) -> str:
    res = requests.get(f"{api_url}/list/{args}")
    text = res.text
    return format(text, languageCode)


def get_random(languageCode: str, n: int) -> str:
    res = requests.get(f"{api_url}/random/{n}")
    text = res.text
    return format(text, languageCode)


def get_random_filter(languageCode: str, n: int, args: str) -> str:
    res = requests.get(f"{api_url}/random/{n}/{args}")
    text = res.text
    return format(text, languageCode)


def get_number(word: str) -> str:
    res = requests.get(f"{api_url}/number/{word}")
    text = res.text
    return format_number(text)


def get_number_reverse(num: int) -> str:
    res = requests.get(f"{api_url}/number/r/{num}")
    text = res.text
    return format_number(text)


def get_line_ending(word: str) -> str:
    results = ""
    match = re.search(r"([.?!]+)$", word)
    if match and match.group() is not None:
        results += match.group()
        results += "\n\n"
    return results


def get_translation(text: str, languageCode: str) -> str:
    results = ""
    word_list = get_word_bundles(text)
    for i, word in enumerate(word_list):
        if i != 0 and not results.endswith("\n"):
            results += " **|** "
        word = word_list[i]
        if re.match(r"hrh", word):
            results += f"lol{get_line_ending(word)}"
            continue
        elif word == "a":
            results += "that"
            continue
        elif re.match(si_pattern, word):
            results += f"do / make{get_line_ending(word)}"
            continue
        elif word == "srake":
            results += "(yes/no question)"
            continue
        elif re.match(r"srak", word):
            results += f"(yes/no question){get_line_ending(word)}"
            continue
        res = requests.get(f"{api_url}/fwew/{word}")
        text = res.text
        results += format_translation(text, languageCode)
        results += get_line_ending(word)
    if len(results) > char_limit:
        return f"translation exceeds character limit of {char_limit}"
    return results


def get_name(a: int, b: int, c: int, ending: str, k: int = 1) -> str:
    results = ""
    if not valid(a, b, c, k):
        results = "Nice try. ;D"
    else:
        a, b, c, k = int(a), int(b), int(c), int(k)
        mk = 0
        # Do entire generator process n times
        while (mk < k):
            i = 0

            # BUILD FIRST NAME
            # first syllable: CV
            results += f"{get_onset()}{get_nucleus()}".capitalize()
            while i < a - 1:
                # some more CV until `a` syllables
                results += f"{get_onset()}{get_nucleus()}"
                i += 1
            results += get_coda()  # Maybe end the syllable with something, maybe not
            i = 0  # reset counter back to 0 for the next part of the name

            results += " te "

            # BUILD FAMILY NAME
            results += f"{get_onset()}{get_nucleus()}".capitalize()  # CV
            while i < b - 1:
                results += f"{get_onset()}{get_nucleus()}"  # CV
                i += 1
            results += get_coda()  # C or None
            i = 0  # reset again for the last part of name
            results += " "

            # BUILD PARENT'S NAME
            results += f"{get_onset()}{get_nucleus()}".capitalize()
            while i < c - 1:
                results += f"{get_onset()}{get_nucleus()}"  # CV
                i += 1
            results += get_coda()
            i = 0

            # ADD ENDING
            results += ending + "\n"

            mk += 1

    return results


def get_lenition() -> str:
    return """```
kx → k
px → p
tx → t
k  → h
p  → f
ts → s
t  → s
'  → (disappears, except before ll or rr)
```"""


def get_version() -> str:
    res = requests.get(f"{api_url}/version")
    return format_version(res.text)
