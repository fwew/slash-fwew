import json
import os
import re
from pathlib import Path
import disnake
from disnake import Colour

import requests
from dotenv import load_dotenv

from name_gen import *
from space_containing import *

version = "3.7.1"

load_dotenv(os.path.join(Path.cwd(), ".env"))
api_url = os.environ.get("API_URL")
# api_url = "http://localhost:10000/api"

url_pattern = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
si_pattern = r"s(äp|eyk|äpeyk)?(iv|ol|er|am|ìm|ìy|ay|ilv|irv|imv|iyev|ìyev|alm|ìlm|ìly|aly|arm|ìrm|ìry|ary|ìsy|asy)?(eiy|äng|eng|uy|ats)?i"
paren_pattern = r"(\(.+\))"
char_limit = 2000

global_onset = ["", ""]

prefix_map_singular = {
    "fì": "this",
    "tsa": "that",
    "fra": "every",
    "fne": "kind of",
}

prefix_map_plural = {
    "fay": "these",
    "tsay": "those",
    "fray": "all",
    "me": "two",
    "pxe": "three",
    "ay": "plural"
}

suffix_map = {
    "fkeyk": "state of",
    "yu": "person who",
    "ur": "to",
    "ru": "to",
    "r": "to",
    "ri": "regarding",
    "ìri": "regarding",
    "yä": "of",
    "ä": "of",
}

infix_map = {
    "ol": "finished",
    "er": "in the middle of",
    "ay": "will",
    "asy": "will intentionally",
    "ìy": "will soon",
    "ìsy": "will soon intentionally",
    "am": "in the past",
    "ìm": "just now",
    "iv": "may/to",
    "eyk": "cause to",
    "äp": "to self",
    "ei": "I like it",
    "eiy": "I like it",
    "äng": "I don't like",
    "eng": "I don't like",
    "ats": "supposedly",
    "us": "that does the action of",
    "awn": "that received the action of",
}


def get_language(inter):
    channel_languages = {
        1104882512607576114: "fr",  # LN/fr/#commandes-bot
        298701183898484737: "de",  # LN/other/#deutsch
        365987412163297284: "fr",  # LN/other/#français
        466721683496239105: "nl",  # LN/other/#nederlands
        649363324143665192: "pl",  # LN/other/#polski
        998643323260653728: "pt",  # LN/other/#português
        1074870940271378472: "pt",  # LN/Português/geral-pt
        1074872259283529778: "pt",  # LN/Português/estudos
        507306946190114846: "ru",  # LN/other/#русский
        1197573962406830121: "ru",  # LN/Русское сообщество На'ви/общение
        1199402001428140224: "ru",  # LN/Русское сообщество На'ви/учебный-класс
        998643038878453870: "tr"   # LN/other/#türkçe
    }
    if inter.channel is None:
        return "en"
    if inter.channel.id in channel_languages:
        return channel_languages[inter.channel.id]
    server_languages = {
        935489523155075092: "en",
        395558141162422275: "en",
        154318499722952704: "en",
        860933619296108564: "en",
        1060288947596570624: "es",
        1058520916612624536: "fr",
        1061696962304426025: "fr",
        1103339942538645605: "fr",
        1065673594354548757: "ru",
        1063774395748847648: "ru",
        1215999922470653982: "ru",
    }
    if inter.guild is None:
        return "en"
    if inter.guild_id not in server_languages:
        server_languages[inter.guild_id] = "en"
    return server_languages[inter.guild_id]


def do_underline(ipa: str, syllables: str) -> str:
    # Make sure there's no multiple IPAs with only stress difference
    multipleIPA = ipa.split("] or [")
    if len(multipleIPA) > 1:
        twoIPAs = [multipleIPA[0].replace("ˈ", ""), multipleIPA[1].replace("ˈ", "")]
        if twoIPAs[0] == twoIPAs[1]: # If it's really a stress difference
            ipa = twoIPAs[0] # Just use one with no stress markers
        else: # If it's a pronunciation difference, too
            ipa = multipleIPA[0] # Use the first one
    
    # Find stressed syllables
    ipa_syllables = []
    ipa_words = ipa.split(" ")
    for word2 in ipa_words:
        if word2 == "or":
            break
        b = word2.split(".")
        for syllable in b:
            if "ˈ" in syllable:
                ipa_syllables.append(True)
            else:
                ipa_syllables.append(False)
    
    # If it's not equal, there's an "or", indicating any syllable stress is correct
    s1 = syllables.split(" ")
    syllables = ""
    i = 0
    for a in s1:
        if a == "or":
            i = 0
            syllables += "or "
            continue
        s2 = a.split("-")
        j = 0
        while i < len(ipa_syllables) and j < len(s2):
            stressed = ipa_syllables[i]
            if j != 0:
                syllables += "-"
            if stressed:
                syllables += "__" + s2[j] + "__"
            else:
                syllables += s2[j]
            i += 1
            j += 1
        syllables += " " 
    syllables = syllables.removesuffix(" or ")

    if "-" not in syllables:
        return syllables
    ipa_words = ipa.split(" ")

    # We don't want words with multiple IPAs
    if len(ipa_words) > 1 and ipa_words[1] == "or":
        return syllables
    ipa_syllables = []

    return syllables


def format_breakdown(word: dict) -> str:
    breakdown = do_underline(word['IPA'], word['Syllables'])
    if word['InfixDots'] != "NULL":
        breakdown += f", {word['InfixDots']}"
    return breakdown.strip()


def format_prefixes(word: dict) -> str:
    results = ""
    len_pre_list = ["me", "pxe", "ay", "fay", "pepe"
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


def format_comment(word: dict) -> str:
    results = ""
    comment = word['Affixes']['Comment']
    if comment is not None and len(comment) > 0:
        results += "      comment: "
        for k, comment in enumerate(comment):
            if k != 0:
                results += ", "
            results += f"**{comment}**"
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


def format_source(words: str) -> str:
    results = ""
    for word in words:
        if isinstance(word, dict) and "message" in word:
            return word["message"]
        for i in range(1, len(word)):
            w = word[i]
            if w['Source'] is None:
                results += f"[{i}] **{w['Navi']}**: no source results\n"
            else:
                w['Source'] = re.sub(url_pattern, r"<\1>", w['Source'])
                results += f"[{i}] **{w['Navi']}** @ {w['Source']}\n"
        results += "\n"
    return results


def format_audio(words: str) -> str:
    results = ""
    for word in words:
        if isinstance(word, dict) and "message" in word:
            return word["message"]
        for i in range(1, len(word)):
            w = word[i]
            syllables = do_underline(w['IPA'], w['Syllables'])
            results += f"[{i}] **{w['Navi']}** ({syllables}) :speaker: [click here to listen](https://s.learnnavi.org/audio/vocab/{w['ID']}.mp3)\n"
        results += "\n"
    return results


def format_alphabet(letter: str, letters_dict: dict, names_dict: dict, i: int) -> str:
    letter = letter.lower()
    letter_id = -1
    current_letter = ""
    current_letter_name = ""
    if letter in letters_dict:
        letter_id = letters_dict[letter]
        current_letter = letter
        current_letter_name = list(names_dict.keys())[letter_id - 1]
    elif letter in names_dict:
        letter_id = names_dict[letter]
        current_letter = list(letters_dict.keys())[letter_id - 1]
        current_letter_name = letter
    if letter_id == -1:
        return f"[{i + 1}] **{letter}**: no results\n"
    return f"[{i + 1}] **{current_letter}** ({current_letter_name}) :speaker: [click here to listen](https://s.learnnavi.org/audio/alphabet/{letter_id}.mp3)\n"


def format_pages_dictionary(words: str, languageCode: str, showIPA: bool = False, reef: bool = False):
    if isinstance(words, dict) and "message" in words:
        return words["message"], 1
    results = ""
    total = 0
    if len(words) == 1:
        results += format_pages_dictionary_helper(
            words[0], languageCode, showIPA, 1, reef)
    else:
        for i in range(1, len(words) + 1):
            someWord = words[i - 1]
            results += format_pages_dictionary_helper(
                someWord, languageCode, showIPA, i, reef)

    # Make 2000 character pages
    split_results = results.split("\n")
    complete_pages = [""]

    for a in split_results:
        if len(a) + len(complete_pages[-1]) > 2000:
            complete_pages.append(a + "\n")
        else:
            complete_pages[-1] += a + "\n"
        # How we know it's a result and not an affix check
        if len(a) > 0 and a[0] == "[":
            total += 1

    return complete_pages, total


def format_pages_1d(words: str, languageCode: str, showIPA: bool = False):
    if isinstance(words, dict) and "message" in words:
        return words["message"], 1
    results = format_pages_helper(words, languageCode, showIPA)
    total = 0

    # Make 2000 character pages
    split_results = results.split("\n")
    complete_pages = [""]

    for a in split_results:
        if len(a) + len(complete_pages[-1]) > 2000:
            complete_pages.append(a + "\n")
        else:
            complete_pages[-1] += a + "\n"
        # How we know if it's a result and not an affix check
        if len(a) > 0 and a[0] == "[":
            total += 1

    return complete_pages, total


def format_pages_dictionary_helper(words: str, languageCode: str, showIPA: bool = False, row: int = 0, reef: bool = False) -> str:
    results = ""
    if len(words) == 1:
        if row == 0:
            row = 1
        results += "**" + words[0]['Navi'] + ":** word not found\n"
    else:
        j = 1
        results += "**" + words[0]['Navi'] + ":**\n"
        while j < len(words):
            word = words[j]
            results += "["
            results += f"{row}"
            if len(words) > 2:
                results += f"-{j}"

            results += "] "

            results += f"**{word['Navi']}** "

            ipa = word['IPA']
            breakdown = format_breakdown(word)
            if showIPA:
                ipa2 = ipa.replace("ʊ", "u")
                results += f"[{ipa2}] "
                if "ʊ" in ipa:
                    results += f"or [{ipa}] "
            results += f"({breakdown}) *{word['PartOfSpeech']}* {word[languageCode.upper()]}\n"

            if reef:
                res = requests.get(f"{api_url}/reef/{ipa}")
                text = res.text
                words2 = json.loads(text)

                or_string = " or "

                split0 = words2[0].split(or_string)
                split1 = words2[1].split("]" + or_string + "[")

                breakdown = ""

                i = 0
                for a in split1:
                    if i >= len(split0):
                        res = requests.get(f"{api_url}/reef/{a}")
                        text = res.text
                        words3 = json.loads(text)
                        breakdown += do_underline(words3[1], words3[0])
                    else:
                        breakdown += do_underline(a, split0[i])
                    i += 1
                    if i < len(split1):
                        breakdown += or_string[1:]

                results += " (Reef Na'vi: " + breakdown
                if showIPA:
                    results += " [" + words2[1] + "]"
                results += ")\n"

            results += format_prefixes(word)
            results += format_infixes(word)
            results += format_suffixes(word)
            results += format_lenition(word)
            results += format_comment(word)
            j += 1
    results += "\n"

    return results


def format_pages_helper(words: str, languageCode: str, showIPA: bool = False, row: int = 0) -> str:
    results = ""
    if len(words) == 0:
        if row == 0:
            row = 1
        results += "[" + str(row) + "] word not found\n"
    else:
        j = 0
        for word in words:
            j += 1
            results += "["
            if row == 0:
                results += f"{j}"
            elif len(words) == 1:
                results += f"{row}"
            else:
                results += f"{row}-{j}"
            results += "] "

            results += f"**{word['Navi']}** "

            ipa = word['IPA']
            breakdown = format_breakdown(word)
            if showIPA:
                ipa2 = ipa.replace("ʊ", "u")
                results += f"[{ipa2}] "
            results += f"({breakdown}) *{word['PartOfSpeech']}* {word[languageCode.upper()]}\n"

            results += format_prefixes(word)
            results += format_infixes(word)
            results += format_suffixes(word)
            results += format_lenition(word)
            results += format_comment(word)

    return results


def get_naive_plural_en(word_en: str) -> str:
    if word_en == 'stomach':
        return 'stomachs'
    endings_es = ['s', 'x', 'z', 'sh', 'ch']
    for ending in endings_es:
        if word_en.endswith(ending):
            return f"{word_en}es"
    return f"{word_en}s"


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
    return f"`  na'vi`: {name}\n`  octal`: {octal}\n`decimal`: {decimal}"


def get_fwew(languageCode: str, words: str, showIPA: bool = False, fixesCheck=True, reef=False, strict=False):
    embeds = []

    if words.lower() == "hrh":
        hrh = "https://youtu.be/-AgnLH7Dw3w?t=274\n"
        hrh += "> What would LOL be?\n"
        hrh += "> It would have to do with the word herangham... maybe HRH"
        embeds.append(disnake.Embed(color=Colour.blue(),
                      title="HRH", description=hrh))
        return embeds
    
    if reef == "true":
        reef = True
    else:
        reef = False

    if strict:
        if reef:
            res = requests.get(f"{api_url}/fwew-reef/true/{words}")
        elif fixesCheck:
            res = requests.get(f"{api_url}/fwew-strict/{words}")
        else:
            res = requests.get(f"{api_url}/fwew-simple/true/{words}")
    else:
        if reef:
            res = requests.get(f"{api_url}/fwew-reef/false/{words}")
        elif fixesCheck:
            res = requests.get(f"{api_url}/fwew/{words}")
        else:
            res = requests.get(f"{api_url}/fwew-simple/false/{words}")
    text = res.text
    words2 = json.loads(text)

    results, total = format_pages_dictionary(
        words2, languageCode, showIPA, reef)

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    hasWords = False

    for a in results:
        i += 1
        lastResult = 0
        for b in a.split("\n"):
            if len(b) > 0 and b[0] == "[":
                lastResult += 1
                if not b.endswith("not found"):
                    hasWords = True
        embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                      str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
        firstResult += lastResult

    if not hasWords:
        embeds = [disnake.Embed(color=Colour.orange(
        ), title="No words found", description="No Na'vi words found for:\n" + words)]

    return embeds


def get_fwew_reverse(languageCode: str, words: str, showIPA: bool = False):
    embeds = []

    if words.lower() == "hrh":
        hrh = "https://youtu.be/-AgnLH7Dw3w?t=274\n"
        hrh += "> What would LOL be?\n"
        hrh += "> It would have to do with the word herangham... maybe HRH"
        embeds.append(disnake.Embed(color=Colour.blue(),
                      title="HRH", description=hrh))
        return embeds

    res = requests.get(f"{api_url}/fwew/r/{languageCode.lower()}/{words}")
    text = res.text
    words2 = json.loads(text)
    results, total = format_pages_dictionary(words2, languageCode, showIPA)

    embeds = []

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    hasWords = False

    for a in results:
        i += 1
        lastResult = 0
        for b in a.split("\n"):
            if len(b) > 0 and b[0] == "[":
                lastResult += 1
                if not b.endswith("not found"):
                    hasWords = True
        embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                      str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
        firstResult += lastResult

    if not hasWords:
        embeds = [disnake.Embed(color=Colour.orange(
        ), title="No words found", description="No natural language words found for:\n" + words)]

    return embeds


def get_search(languageCode: str, words: str, showIPA: bool = False, reef: bool=False):
    embeds = []

    if words.lower() == "hrh":
        hrh = "https://youtu.be/-AgnLH7Dw3w?t=274\n"
        hrh += "> What would LOL be?\n"
        hrh += "> It would have to do with the word herangham... maybe HRH"
        embeds.append(disnake.Embed(color=Colour.blue(),
                      title="HRH", description=hrh))
        return embeds

    if reef:
        res = requests.get(f"{api_url}/search-reef/{languageCode.lower()}/{words}")
    else:
        res = requests.get(f"{api_url}/search/{languageCode.lower()}/{words}")
    text = res.text
    words2 = json.loads(text)
    results, total = format_pages_dictionary(words2, languageCode, showIPA, reef)

    embeds = []

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    hasWords = False

    for a in results:
        i += 1
        lastResult = 0
        for b in a.split("\n"):
            if len(b) > 0 and b[0] == "[":
                lastResult += 1
                if not b.endswith("not found"):
                    hasWords = True
        embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                      str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
        firstResult += lastResult

    if not hasWords:
        embeds = [disnake.Embed(color=Colour.orange(), title="No words found",
                                description="No Na'vi or natural language words found for:\n" + words)]

    return embeds


def get_profanity(lang: str, showIPA: bool) -> str:
    words = "skxawng kalweyaveng kurkung pela'ang pxasìk teylupil tsahey txanfwìngtu vitronvä' vonvä' wiya yayl"
    return get_fwew(lang, words, showIPA, fixesCheck=False)


def get_homonyms(showIPA: bool, languageCode: str, reef: bool):
    embeds = []

    res = requests.get(f"{api_url}/homonyms")
    text = res.text
    words2 = json.loads(text)
    results, total = format_pages_dictionary(words2, languageCode, showIPA, reef)

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    hasWords = False

    for a in results:
        i += 1
        lastResult = 0
        for b in a.split("\n"):
            if len(b) > 0 and b[0] == "[":
                lastResult += 1
                if not b.endswith("not found"):
                    hasWords = True
        embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                      str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
        firstResult += lastResult

    if not hasWords:
        embeds = [disnake.Embed(color=Colour.orange(
        ), title="No words found", description="No homonyms found:\n")]

    return embeds


def get_multi_ipa(languageCode: str, reef: bool):
    embeds = []

    res = requests.get(f"{api_url}/multi-ipa")
    text = res.text
    words2 = json.loads(text)
    results, total = format_pages_dictionary(words2, languageCode, True, reef)

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    hasWords = False

    for a in results:
        i += 1
        lastResult = 0
        for b in a.split("\n"):
            if len(b) > 0 and b[0] == "[":
                lastResult += 1
                if not b.endswith("not found"):
                    hasWords = True
        embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                      str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
        firstResult += lastResult

    if not hasWords:
        embeds = [disnake.Embed(color=Colour.orange(
        ), title="No words found", description="No multiple IPA words found:\n")]

    return embeds


def get_dict_len(lang):
    res = requests.get(f"{api_url}/total-words/{lang}")
    text = res.text
    return json.loads(text)


def get_source(words: str) -> str:
    results = ""

    res = requests.get(f"{api_url}/fwew/{words}")
    text = res.text
    words2 = json.loads(text)
    results += format_source(words2)
    if len(results.split()) < 1:
        return "Words not found: " + words
    return results


def get_audio(words: str) -> str:
    results = ""

    res = requests.get(f"{api_url}/fwew/{words}")
    text = res.text
    words2 = json.loads(text)
    results += format_audio(words2)
    if len(results) < 5:
        return "Words not found: " + words
    return results


def get_alphabet(letters: str) -> str:
    letters_dict = {
        "'": 1, "a": 2, "aw": 3, "ay": 4, "ä": 5, "e": 6, "ew": 7, "ey": 8,
        "f": 9, "h": 10, "i": 11, "ì": 12, "k": 13, "kx": 14, "l": 15, "ll": 16,
        "m": 17, "n": 18, "ng": 19, "o": 20, "p": 21, "px": 22, "r": 23, "rr": 24,
        "s": 25, "t": 26, "tx": 27, "ts": 28, "u": 29, "v": 30, "w": 31, "y": 32,
        "z": 33,
    }
    names_dict = {
        "tìftang": 1, "a": 2, "aw": 3, "ay": 4, "ä": 5, "e": 6, "ew": 7, "ey": 8,
        "fä": 9, "hä": 10, "i": 11, "ì": 12, "kek": 13, "kxekx": 14, "lel": 15,
        "'ll": 16, "mem": 17, "nen": 18, "ngeng": 19, "o": 20, "pep": 21,
        "pxepx": 22, "rer": 23, "'rr": 24, "sä": 25, "tet": 26, "txetx": 27,
        "tsä": 28, "u": 29, "vä": 30, "wä": 31, "yä": 32, "zä": 33
    }
    results = ""
    letter_list = letters.split()
    for i, letter in enumerate(letter_list):
        if i != 0:
            results += "\n"
        results += format_alphabet(letter, letters_dict, names_dict, i)
    return results


def get_list(languageCode: str, args: str, showIPA: bool, check_digraphs: bool) -> str:
    res = requests.get(f"{api_url}/list2/{check_digraphs}/{args}")
    text = res.text
    words2 = json.loads(text)
    results, total = format_pages_1d(words2, languageCode, showIPA)

    embeds = []

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    if type(results) == str:
        embeds.append(disnake.Embed(color=Colour.orange(), title="No words found",
                      description="No words matching your parameters:\n" + args))
    else:
        for a in results:
            i += 1
            lastResult = 0
            for b in a.split("\n"):
                if len(b) > 0 and b[0] == "[":
                    lastResult += 1

            embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                          str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
            firstResult += lastResult

    return embeds


def get_random(languageCode: str, n: int, showIPA: bool) -> str:
    res = requests.get(f"{api_url}/random2/{n}/True")
    text = res.text
    words2 = json.loads(text)
    results, total = format_pages_1d(words2, languageCode, showIPA)

    embeds = []

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    if type(results) == str:
        embeds.append(disnake.Embed(color=Colour.orange(
        ), title="Random failed", description="You should not be seeing this on Discord"))
    else:
        for a in results:
            i += 1
            lastResult = 0
            for b in a.split("\n"):
                if len(b) > 0 and b[0] == "[":
                    lastResult += 1
            embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                          str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
            firstResult += lastResult

    return embeds


def get_random_filter(languageCode: str, n: int, args: str, showIPA: bool, check_digraphs: str) -> str:
    res = requests.get(f"{api_url}/random2/{n}/{check_digraphs}/{args}")
    text = res.text
    words2 = json.loads(text)
    results, total = format_pages_1d(words2, languageCode, showIPA)

    embeds = []

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    if type(results) == str:
        embeds.append(disnake.Embed(color=Colour.orange(), title="No words found",
                      description="No words matching your parameters:\n" + args))
    else:
        for a in results:
            i += 1
            lastResult = 0
            for b in a.split("\n"):
                if len(b) > 0 and b[0] == "[":
                    lastResult += 1
            embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                          str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
            firstResult += lastResult

    return embeds


def get_number(word: str) -> str:
    res = requests.get(f"{api_url}/number/{word}")
    text = res.text
    return format_number(text)


def get_number_reverse(num: int) -> str:
    if int(num) > 32767:
        return "Error: Maximum is 32,767 (octal: 077777)"
    if int(num) < 0:
        return "Na'vi has no negative numbers"
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


def format_translation(words, languageCode: str) -> str:
    if isinstance(words, dict) and "message" in words:
        return "(?)"
    results = ""
    first = True
    
    for i in range(len(words)):
        word = words[i]
        if i == 0:
            continue
        definition = f"{word[languageCode.upper()]}"
        definition_clean = re.sub(paren_pattern, "", definition)
        prefixes = word['Affixes']['Prefix']
        suffixes = word['Affixes']['Suffix']
        infixes = word['Affixes']['Infix']
        # Find the fixes and stuff in the maps
        if prefixes is not None:
            for a in prefixes:
                if a in prefix_map_singular:
                    definition_clean = "(" + prefix_map_singular[a] + ") " + \
                        " " + definition_clean
                    break
                if a in prefix_map_plural:
                    definition_clean = "(" + prefix_map_plural[a] + ") " + \
                        " " + definition_clean #get_naive_plural_en(definition_clean)
                    break
        if suffixes is not None:
            for a in suffixes:
                if a in suffix_map:
                    definition_clean = "(" + suffix_map[a] + ") " + \
                        " " + definition_clean
                    break
        if infixes is not None:
            for a in infixes:
                if a in infix_map:
                    definition_clean = "(" + \
                        infix_map[a] + ") " + definition_clean
        if first:
            results += f"{definition_clean}"
            first = False
        else:
            results += f" / {definition_clean}"
    return results + " **|** "

# Discord right-click menu translator
def get_translation(text: str, languageCode: str) -> str:
    results = ""

    texts = text.replace("*", " ")  # *Italics* and **bold** and ***both***
    texts = texts.replace("~", " ")  # ~~Strikethrough~~
    texts = texts.replace("|", " ")  # ||Spoiler||
    texts = texts.replace("`", " ")  # `monospace` and ```code block```
    texts = texts.replace(">", " ")  # > line quote and >>> block quote
    texts = texts.replace(",", " ")
    texts = texts.replace("?", " ")
    texts = texts.replace("!", " ")
    texts = texts.replace("<", " <") # Help it detect custom emojis
    texts = texts.replace("‘", "'") # “Smart” asterisks
    texts = texts.replace("’", "'") # They can trip up the emoji detector
    texts = texts.replace("\"", " ")
    texts = texts.replace("“", " ")
    texts = texts.replace("”", " ")
    texts = texts.strip()
    while "  " in texts:
        texts = texts.replace("  ", " ")
    all_words = texts.split()
    navi_block = ""
    temp_result = ""

    # Enumarate the block of text
    for n, word in enumerate(all_words):
        word = all_words[n]

        #
        # Don't translate these words
        #
        if word.startswith("htt"):
            # Don't translate URLs
            temp_result += word + " **|** "
            found_separator = True
        elif word.startswith("<:"):
            # Don't translate custom emojis
            temp_result += word + "> **|** "
            found_separator = True
        elif word.startswith("<@"):
            # Don't translate user pings
            temp_result += "[Ping] **|** "
            found_separator = True
        elif len(word[0].encode("utf-8")) > 2:
            # Don't translate normal emojis
            temp_result += word + " **|** "
            found_separator = True

        #
        # Include these words
        #
        elif re.match(r"hrh", word):
            temp_result += f"lol{get_line_ending(word)} **|** "
            found_separator = True
        elif word == "a":
            temp_result += "that **|** "
            found_separator = True
        elif word == "srake":
            temp_result += "(yes/no question) **|** "
            found_separator = True
        elif re.match(r"srak", word):
            temp_result += f"(yes/no question){get_line_ending(word)} **|** "
            found_separator = True
        elif word == "ma":
            temp_result += "(I'm talking to) **|** "
            found_separator = True
        else:
            results2 = requests.get(f"{api_url}/fwew/{word}").text
            if results2 == '{"message":"no results"}\n':
                # Add non-translatable words
                temp_result += word + " **|** "
                found_separator = True
            # has only one result
            elif len(json.loads(results2)[0]) == 1:
                # Add non-translatable words
                temp_result += word + " **|** "
                found_separator = True
            else:
                navi_block += word + " "
                found_separator = False

        #
        # Found a block of Na'vi text.  Translate it
        #
        if found_separator:
            res = requests.get(f"{api_url}/fwew/{navi_block}")
            res_text = res.text
            if len(res_text) > 20:
                text = json.loads(res_text)
                for a in text:
                    if len(a) > 1: # don't do the last empty one
                        results += format_translation(a, languageCode)
                        results += get_line_ending(word)
            navi_block = ""
            results += temp_result
            temp_result = ""

    # Make sure we don't skip a final Na'vi block
    res = requests.get(f"{api_url}/fwew/{navi_block}")
    res_text = res.text
    if len(res_text) > 20:
        text = json.loads(res_text)
        for a in text:
            if len(a) > 0:
                results += format_translation(a, languageCode)
                results += get_line_ending(word)

    # Add any text that may have came after the Na'vi block
    results += temp_result
    if len(results) > char_limit:
        return f"translation exceeds character limit of {char_limit}"
    elif len(results) == 0:
        return "No results"
    return results.removesuffix(" **|** ")

# One-word names to be sent to Discord


def get_single_name_discord(n: int, dialect: str, s: int):
    return json.loads(requests.get(f"{api_url}/name/single/{n}/{s}/{dialect}").text)

# Full names to be sent to Discord


def get_name(ending: str, n: int, dialect: str, s1: int, s2: int, s3: int) -> str:
    # The "d" in the URL means "Discord".  It will stop before the 2000 character limit
    return json.loads(requests.get(f"{api_url}/name/full/d/{ending}/{n}/{s1}/{s2}/{s3}/{dialect}").text)

# [name] the [adjective] [noun] format names to be sent to Discord


def get_name_alu(n: int, dialect: str, s: int, noun_mode: str, adj_mode: str) -> str:
    return json.loads(requests.get(f"{api_url}/name/alu/{n}/{s}/{noun_mode}/{adj_mode}/{dialect}").text)


def chart_entry(x: str, y: int, width: int):
    spaces = width - len(x) - len(y)
    stringtsyìp = ""
    if x != "":
        stringtsyìp = x
    else:
        spaces = width - len(y) -1
    for i in range(0, spaces):
        stringtsyìp += " "
    stringtsyìp += y

    return stringtsyìp + "|"

def equals_separator(length) -> str:
    output = ""
    for a in length:
        i = 0
        output += "|"
        while i < a:
            output += "="
            i += 1
    return output + "|"

def get_phonemes(lang: str) -> str:
    all_frequencies = json.loads(
        requests.get(f"{api_url}/phonemedistros/{lang}").text)
    
    phoneme_frequences_lang = {
        "en": "Phoneme Frequencies",    # English
        "de": "Phoneme Frequencies 🇩🇪", # TODO: German (Deutsch)
        "es": "Phoneme Frequencies 🇪🇦", # TODO: Spanish (Español)
        "et": "Phoneme Frequencies 🇪🇪", # TODO: Estonian (Eesti)
        "fr": "Phoneme Frequencies 🇫🇷", # TODO: French (Français)
        "hu": "Phoneme Frequencies 🇭🇺", # TODO: Hungarian (Magyar)
        "ko": "음절 구성표",             # Korean (한국어)
        "nl": "Phoneme Frequencies 🇳🇱", # TODO: Dutch (Nederlands)
        "nx": "Ayfamrelvi",             # Na'vi
        "pl": "Phoneme Frequencies 🇵🇱", # TODO: Polish (Polski)
        "pt": "Phoneme Frequencies 🇵🇹", # TODO: Portuguese (Português)
        "ru": "Phoneme Frequencies 🇷🇺", # TODO: Russian (Русский)
        "sv": "Phoneme Frequencies 🇸🇪", # TODO: Swedish (Svenska)
        "tr": "Phoneme Frequencies 🇹🇷", # TODO: Turkish (Türkçe)
        "uk": "Phoneme Frequencies 🇺🇦", # TODO: Ukrainian (Українська)
        #"eo": "Phoneme Frequencies (Esperanto)", # Esperanto
    }
    
    entries = "## " + phoneme_frequences_lang[lang] + ":\n```\n"

    col_widths = [7,7,7]
    i = 0

    # Make sure that we account for longer names in different languages
    for a in all_frequencies[0][0]:
        if len(a) > col_widths[i]:
            col_widths[i] = len(a)
        i += 1
    
    i = 0
    for a in all_frequencies[0]:
        if i == 1:
            entries += equals_separator(col_widths) + "\n"
        new_entry = "|"
        j = 0
        for b in a:
            things = b.split()
            if len(things) == 2:
                new_entry += chart_entry(things[0], things[1], col_widths[j])
            else:
                new_entry += chart_entry("", b, col_widths[j]+1)
            j += 1
        entries += new_entry + "\n"
        i += 1
    
    entries += "\n" + all_frequencies[1][0][0] + ":\n"
    all_frequencies[1][0][0] = ""

    i = 0
    for a in all_frequencies[1]:
        if i == 1:
            entries += "==|===|===|===|\n"
        new_entry = ""
        for b in a:
            new_entry += chart_entry(" ", b, 3)
        entries += new_entry[1:] + "\n"
        i += 1

    entries += "```"
    return entries


def get_lenition() -> str:
    return """```
kx → k
px → p
tx → t

k  → h
p  → f
t  → s

ts → s

'  → (disappears, except before ll or rr)

leniting prefixes: me+, pxe+, ay+, pe+
leniting adpositions: fpi, ìlä, lisre, mì, nuä, pxisre, ro, sko, sre, wä
```"""


def get_len() -> str:
    return """```
kx, px, tx -> k, p, t
   k, p, t -> h, f, s
        ts -> s
         ' -> (disappears, except before ll or rr)

leniting prefixes: me+, pxe+, ay+, pe+
leniting adpositions: fpi, ìlä, lisre, mì, nuä, pxisre, ro, sko, sre, wä
```"""


def get_all_thats() -> str:
    return """```
Case|Noun |   Clause wrapper    |
    |     |prox.| dist.| answer |
====|=====|=====|======|========|
Sub.|Tsaw |Fwa  |Tsawa |Teynga  |
Agt.|Tsal |Fula |Tsala |Teyngla |
Pat.|Tsat |Futa |Tsata |Teyngta |
Gen.|Tseyä| N/A |  N/A |Teyngä  |
Dat.|Tsar |Fura |Tsara |Teyngra |
Top.|Tsari|Furia|Tsaria|Teyngria|

tsa-      pre.  that
tsa'u     n.    that (thing)
tsakem    n.    that (action)
fmawnta   sbd.  that news
fayluta   sbd.  these words
tsnì      sbd.  that (function word)
tsonta    conj. to (with kxìm)
kuma/akum conj. that (as a result)
a         part. clause level attributive marker
```"""


def get_cameron_words() -> str:
    return """## Cameron words:
- **A1 Names:** Akwey, Ateyo, Eytukan, Eywa, Mo'at, Na'vi, Newey, Neytiri, Ninat, Omatikaya, Otranyu, Rongloa, Silwanin, Tskaha, Tsu'tey
- **A2 Names:** Aonung, Kiri, Lo'ak, Neteyam, Ronal, Rotxo, Tonowari, Tuktirey, Tsireya
- **Nouns:** 'itan, 'ite, atan, au *(drum)*, eyktan, i'en, Iknimaya, mikyun, ontu, seyri, tsaheylu, tsahìk, unil
- **Life:** Atokirina', Ikran, Palulukan, Riti, talioang, teylu, Toruk
- **Other:** eyk, irayo, makto, taron, te"""


def get_validity(word: str, lang: str) -> str:
    # The "d" in the URL means "Discord".  It will stop before the 2000 character limit
    res = requests.get(f"{api_url}/valid/d/{lang}/{word}")
    text = res.text
    words2 = json.loads(text)

    return words2


def get_oddballs(showIPA: bool, languageCode: str, reef: bool) -> str:
    embeds = []

    res = requests.get(f"{api_url}/oddballs")
    text = res.text
    words2 = json.loads(text)
    results, total = format_pages_dictionary(words2, languageCode, showIPA, reef)

    # Create a list of embeds to paginate.
    i = 0
    firstResult = 0

    hasWords = False

    for a in results:
        i += 1
        lastResult = 0
        for b in a.split("\n"):
            if len(b) > 0 and b[0] == "[":
                lastResult += 1
                if not b.endswith("not found"):
                    hasWords = True
        embeds.append(disnake.Embed(color=Colour.blue(), title="Results " + str(firstResult + 1) + "-" +
                      str(firstResult + lastResult) + " of " + str(total) + " (page " + str(i) + ")", description=a))
        firstResult += lastResult

    if not hasWords:
        embeds = [disnake.Embed(color=Colour.orange(
        ), title="No words found", description="No oddballs found:\n")]

    return embeds


def get_version() -> str:
    res = requests.get(f"{api_url}/version")
    return format_version(res.text)
