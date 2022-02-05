import json
import re
import requests

version = "1.2.0"
api_url = "http://localhost:10000/api"
url_pattern = r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
si_pattern = r"s(äp|eyk|äpeyk)?(iv|ol|er|am|ìm|ìy|ay|ilv|irv|imv|iyev|ìyev|alm|ìlm|ìly|aly|arm|ìrm|ìry|ary|ìsy|asy)?(eiy|äng|eng|uy|ats)?i"
paren_pattern = r"(\(.+\))"
char_limit = 2000


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


def format_breakdown(w) -> str:
    breakdown = do_underline(w['Stressed'], w['Syllables'])
    if w['InfixDots'] != "NULL":
        breakdown += f", {w['InfixDots']}"
    return breakdown


def format_prefixes(w) -> str:
    results = ""
    len_pre_list = ["me", "pxe", "ay", "fay",
                    "tsay", "fray", "pe", "pem", "pep", "pay"]
    prefixes = w['Affixes']['Prefix']
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


def format_infixes(w) -> str:
    results = ""
    infixes = w['Affixes']['Infix']
    if infixes is not None and len(infixes) > 0:
        results += "      infixes: "
        for k, infix in enumerate(infixes):
            if k != 0:
                results += ", "
            results += f"<**{infix}**>"
        results += "\n"
    return results


def format_suffixes(w) -> str:
    results = ""
    suffixes = w['Affixes']['Suffix']
    if suffixes is not None and len(suffixes) > 0:
        results += "      suffixes: "
        for k, suffix in enumerate(suffixes):
            if k != 0:
                results += ", "
            results += f"-**{suffix}**"
        results += "\n"
    return results


def format_lenition(w) -> str:
    results = ""
    lenition = w['Affixes']['Lenition']
    if lenition is not None and len(lenition) > 0:
        results += "      lenition: "
        for k, lenite in enumerate(lenition):
            if k != 0:
                results += ", "
            results += f"{lenite}"
        results += "\n"
    return results


def format_source(word: str) -> str:
    data = json.loads(word)
    if isinstance(data, dict) and "message" in data:
        return data["message"]
    results = ""
    for i in range(1, len(data) + 1):
        w = data[i - 1]
        if w['Source'] is None:
            results += f"[{i}] **{w['Navi']}**: no source results\n"
        else:
            w['Source'] = re.sub(url_pattern, r"<\1>", w['Source'])
            results += f"[{i}] **{w['Navi']}** @ {w['Source']}\n"
    return results


def format_audio(word: str) -> str:
    data = json.loads(word)
    if isinstance(data, dict) and "message" in data:
        return data["message"]
    results = ""
    for i in range(1, len(data) + 1):
        w = data[i - 1]
        syllables = do_underline(w['Stressed'], w['Syllables'])
        results += f"[{i}] **{w['Navi']}** ({syllables}) :speaker: [click here to listen](https://s.learnnavi.org/audio/vocab/{w['ID']}.mp3)\n"
    return results


def format(word: str, languageCode: str) -> str:
    data = json.loads(word)
    if isinstance(data, dict) and "message" in data:
        return data["message"]
    results = ""
    for j in range(1, len(data) + 1):
        w = data[j - 1]
        breakdown = format_breakdown(w)
        results += f"[{j}] **{w['Navi']}** ({breakdown}) *{w['PartOfSpeech']}* {w[languageCode.upper()]}\n"
        results += format_prefixes(w)
        results += format_infixes(w)
        results += format_suffixes(w)
        results += format_lenition(w)
    if len(results) > char_limit:
        return f"{len(data)} results. please search a more specific list, or use /random with number and same args"
    return results


def format_translation(word: str, languageCode: str) -> str:
    data = json.loads(word)
    if isinstance(data, dict) and "message" in data:
        return "(?)"
    results = ""
    index = -1
    for i, wd in enumerate(data):
        prefixes = wd['Affixes']['Prefix']
        infixes = wd['Affixes']['Infix']
        suffixes = wd['Affixes']['Suffix']
        lenition = wd['Affixes']['Lenition']
        if prefixes is None and infixes is None and suffixes is None and lenition is None:
            index = i
            break
    if index != -1:
        w = data[index]
        defn = f"{w[languageCode.upper()]}"
        defc = re.sub(paren_pattern, "", defn)
        results += f"{defc}"
    else:
        for i in range(len(data)):
            w = data[i]
            if i != 0:
                results += " / "
            defn = f"{w[languageCode.upper()]}"
            defc = re.sub(paren_pattern, "", defn)
            prefix = w['Affixes']['Prefix']
            if prefix is not None:
                if "fì" in prefix:
                    defc = f"this {defc}"
                elif "tsa" in prefix:
                    defc = f"that {defc}"
                elif "fay" in prefix:
                    defc = f"these {defc}"
                elif "tsay" in prefix:
                    defc = f"those {defc}"
                elif "fray" in prefix or "fra" in prefix:
                    defc = f"every {defc}"
            results += f"{defc}"
    return results


def format_version(text: str) -> str:
    w = json.loads(text)
    ver = "```\n"
    ver += f"slash-fwew: {version}\n"
    ver += f"fwew-api:   {w['APIVersion']}\n"
    ver += f"fwew-lib:   {w['FwewVersion']}\n"
    ver += f"dictionary: {w['DictVersion']}\n"
    ver += "```"
    return ver


def format_number(text: str) -> str:
    w = json.loads(text)
    if isinstance(w, dict) and "message" in w:
        return w["message"]
    name = w["name"]
    octal = w["octal"]
    decimal = w["decimal"]
    return f"**na'vi**: {name} | **octal**: {octal} | **decimal**: {decimal}"


def get_fwew(languageCode: str, words: str) -> str:
    results = ""
    word_list = words.split()
    for i, word in enumerate(word_list):
        if i != 0:
            results += "\n"
        word = word_list[i]
        res = requests.get(f"{api_url}/fwew/{word}")
        text = res.text
        results += format(text, languageCode)
    return results


def get_fwew_reverse(languageCode: str, words: str) -> str:
    results = ""
    word_list = words.split()
    for i, word in enumerate(word_list):
        if i != 0:
            results += "\n"
        word = word_list[i]
        res = requests.get(f"{api_url}/fwew/r/{languageCode.lower()}/{word}")
        text = res.text
        results += format(text, languageCode)
    return results


def get_source(words: str) -> str:
    results = ""
    word_list = words.split()
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
    word_list = words.split()
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
    word_list = text.split()
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


def get_lenition() -> str:
    return """```
kx → k
px → p
tx → t
k  → h
p  → f
ts → s
t  → s
'  → (disappears)
```"""


def get_version() -> str:
    res = requests.get(f"{api_url}/version")
    return format_version(res.text)
