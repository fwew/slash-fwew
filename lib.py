import json
import re
import requests

from space_containing import *
from name_gen import *

version = "2.6.2"
api_url = "http://localhost:10000/api"
url_pattern = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
si_pattern = r"s(äp|eyk|äpeyk)?(iv|ol|er|am|ìm|ìy|ay|ilv|irv|imv|iyev|ìyev|alm|ìlm|ìly|aly|arm|ìrm|ìry|ary|ìsy|asy)?(eiy|äng|eng|uy|ats)?i"
paren_pattern = r"(\(.+\))"
char_limit = 2000

global_onset = ["",""]

def get_language(inter):
    channel_languages = {
        1104882512607576114: "fr", # LN/fr/#commandes-bot
        298701183898484737: "de",  # LN/other/#deutsch
        365987412163297284: "fr",  # LN/other/#français
        466721683496239105: "nl",  # LN/other/#nederlands
        649363324143665192: "pl",  # LN/other/#polski
        507306946190114846: "ru",  # LN/other/#русский
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
        1058520916612624536: "fr",
        1061696962304426025: "fr",
        1103339942538645605: "fr",
        1065673594354548757: "ru",
        1063774395748847648: "ru"
    }
    if inter.guild is None:
        return "en"
    if inter.guild_id not in server_languages:
        server_languages[inter.guild_id] = "en"
    return server_languages[inter.guild_id]


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
        results += format_comment(word)
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
    return f"`  na'vi`: {name}\n`  octal`: {octal}\n`decimal`: {decimal}"


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
        res = requests.get(f"{api_url}/fwew/{word}")
        text = res.text
        results += format_audio(text)
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

def single_name_discord(i: int, n: int):
    loader = ""
    
    if int(i) > 4 or int(i) < 0:
        return "Max b is 4, max n is 50"
    i = rand_if_zero(int(i))
    n = int(n)
    if n > 50 or n < 1:
        return "Max b is 4, max n is 50"

    for k in range(0,rand_if_zero(n)):
        loader += single_name(i) + "\n"
    return loader

def single_name(i: int):
    loader = ""
    onset = get_onset_2().strip()
    nucleus = get_nucleus_2()
    coda = get_coda_2(nucleus)
    if not (len(onset) > 0 and onset[0] == nucleus[0]): #disallow "lll" and "rrr"
        loader += onset
              
    loader += (nucleus + coda).strip()
            
    x = 0
    while x < (i - 1): #loop A times
        # some more CV until `a` syllables
        onset = get_onset_2().strip()
        if(onset == loader[-1]): #disallow "lll", "rrr", "eyy" and "aww"
            onset = ""

        #
        # "Superclusters" are whitelisted
        #

        if len(coda.strip()) > 0 and len(onset) > 1:
            # Decode the cluster
            a = ""
            b = ""
            i = 1
            cluster_possible = False
            if onset.startswith("ts") :
                a = "ts"
                i = 2
                cluster_possible = True
            elif onset[0] in ["f", "s"] :
                a = onset[0]
                cluster_possible = True
            
            if cluster_possible:
                b = onset[i:].strip()
                if len(b) > 0:
                    if not(coda in superclusters and a in superclusters[coda] and b in superclusters[coda][a]):
                        onset = b
                    #For debugging
                    #    print("Rejected: " + coda + a + b)
                    #else:
                    #    print("Accepted: " + coda + a + b)

        #
        # Nucleus and coda
        #

        nucleus = get_nucleus_2()
        # No identical adjacent vowels.  This isn't the reef
        if(onset == "" and nucleus[0] == loader[-1]):
            continue # Destruction of nucleus property.  Do not pass go, do not collect your x += 1
        coda = get_coda_2(nucleus)
        loader += (onset + nucleus + coda).strip()
        x += 1

    return glottal_caps(loader)

def rand_if_zero(x: int):
    if x == 0:
        return random.randint(2,4)
    return x

def get_name(a: int, b: int, c: int, ending: str, k: int = 1) -> str:
    results = ""
    # for temp storage before appending to results
    loader = ""
    if not valid(int(a), int(b), int(c), int(k)):
        results = "Max a, b and c are 4, max n is 50"
    else:
        a, b, c, k = int(a), int(b), int(c), int(k)
        mk = 0
        # Do entire generator process n times
        for mk in range(0,k):
            # BUILD FIRST NAME
            # first syllable: CV
            results += single_name(rand_if_zero(a))

            results += " te "

            # BUILD FAMILY NAME
            results += single_name(rand_if_zero(b))

            results += " "

            # BUILD PARENT'S NAME
            results += single_name(rand_if_zero(b))

            # ADD ENDING
            results += ending + "\n"

    return results


def get_name_alu(a: int, adj_mode: str = "something", k: int = 1) -> str:
    results = ""
    if not valid_alu(adj_mode, int(a), int(k)):
        results = "Max b is 4, max n is 50"
    else:
        
        a, k = int(a), int(k)

        # Adjectives and nouns can be shared across loops
        buffer = ""

        mode = 3
        if adj_mode == "none":
            mode = 1
        elif adj_mode == "normal adjective":
            mode = 2
        elif adj_mode == "genitive noun":
            mode = 3
        elif adj_mode == "origin noun":
            mode = 4

        # Do entire generator process n times
        for mk in range(k): #loop k times
            # For building names before appending them to results
            loader = ""

            if a == 0:
                b = random.randint(2,4)
            else:
                b = a

            results += single_name(b) + " alu "

            # if not specified, pick randomly
            if adj_mode == "any" or adj_mode == "something":
                mode = random.randint(1,4)
            
            if adj_mode == "something" and mode == 1:
                mode = 2

            # ADJECTIVE
            if mode == 2:
                loader = ""
                # Get adjectives
                query = requests.get(f"{api_url}/random/1/pos is adj.")
                buffer = json.loads(query.text)
                loader += buffer[0]['Navi']
                # Make sure there's no a before we add an a (like in "hona" or "apxa")
                if(len(loader) > 0 and loader[len(loader) - 1] != 'a'):
                    loader += "a "
                else:
                    loader += " "
                
                results += glottal_caps(loader.capitalize())
            # ATTRIBUTIVE NOUN
            elif mode == 3 or mode == 4:
                loader = ""
                # Get nouns
                query = requests.get(f"{api_url}/random/1/pos is n.")

                buffer = json.loads(query.text)

                words = buffer[0]['Navi']
                wordList = words.split()
                # Genitive noun
                if mode == 3:
                    # The only nouns put together using a space
                    if words == "tsko swizaw":
                        results += "Tsko Swizawyä "
                    # the only noun with two spaces
                    elif words == "mo a fngä'":
                        results += "Moä a Fgnä' "
                    # Watch your profanity
                    # elif words in ["kalweyaveng", "kurkung", "la'ang",
                    #               "skxawng", "teylupil", "txanfwìngtu", "vonvä'"]:
                    #    results += "Skxawngä "
                    else:
                        yvowels = ['a', 'ä', 'e', 'i', 'ì']
                        for i in range(len(wordList) - 1, -1, -1):
                            loader = ""
                            # The only a-attributed word in the dictionary, part of "swoasey ayll"
                            if wordList[i] == "ayll":
                                loader += "Ylla "
                            elif wordList[i].startswith("le"):
                                loader += wordList[i] + "a "
                            elif wordList[i].endswith("yä"):
                                loader += wordList[i] + " "
                            elif wordList[i].endswith("ia"): # aungia, meuia, soaia, tìftia, kemuia
                                loader += wordList[i]
                                loader.removesuffix('a')
                                loader += "ä "
                            elif wordList[i][-1] in yvowels:
                                loader += wordList[i] + "yä "
                            else: #If's it's a conosonent, psuedovowel, xdiphthong, o or u
                                loader += wordList[i] + "ä "
                            results += glottal_caps(loader.capitalize())
                # Origin noun
                elif mode == 4:
                    # The only nouns put together using a space
                    if words == "tsko swizaw":
                        results += "Tsko Swizawta "
                    # the only noun with two spaces
                    elif words == "mo a fngä'":
                        results += "ta Mo a Fgnä' "
                    # Watch your profanity
                    # elif words in ["kalweyaveng", "kurkung", "la'ang",
                    #                "skxawng", "teylupil", "txanfwìngtu", "vonvä'"]:
                    #     results += "Skxawngta "
                    else:
                        for i in range(len(wordList) - 1, -1, -1):
                            loader = ""
                            # The only a-attributed word in the dictionary, part of "swoasey ayll"
                            if wordList[i] == "ayll":
                                loader += "Ylla "
                            elif wordList[i].startswith("le"):
                                loader += wordList[i] + "a "
                            elif wordList[i].endswith("yä"):
                                loader += wordList[i]
                            else:
                                loader += wordList[i] + "ta "
                            results += glottal_caps(loader.capitalize())
            
            # GET PRIMARY NOUN
            loader = ""
            query = requests.get(f"{api_url}/random/1/pos is n.")
            buffer = json.loads(query.text)
            loader = buffer[0]['Navi']
            # Wivatch youä profanitit
            # if loader in ["kalweyaveng", "kurkung", "la'ang",
            #            "skxawng", "teylupil", "txanfwìngtu", "vonvä'"]:
            #    loader = "Skxawng"
            results += glottal_caps(loader.capitalize())

            # ADD ENDING
            results += "\n"

    return results


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
```"""

def get_len() -> str:
    return """```
kx, px, tx -> k, p, t
   k, p, t -> h, f, s
        ts -> s
         ' -> (disappears, except before ll or rr)
```"""

def get_all_thats() -> str:
    return """```
Case|Noun |   Clause wrapper   |
    |     |prox.| dist.|answer |
====|=====|=====|======|=======|
Sub.|Tsaw |Fwa  |Tsawa |Teynga |
Agt.|Tsal |Fula |Tsala |Teyngla|
Pat.|Tsat |Futa |Tsata |Teyngta|
Gen.|Tseyä| N/A |  N/A |
Dat.|Tsar |Fura |Tsara |
Top.|Tsari|Furia|Tsaria|

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


def get_version() -> str:
    res = requests.get(f"{api_url}/version")
    return format_version(res.text)
