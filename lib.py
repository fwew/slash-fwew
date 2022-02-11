import json
import re
import requests
import random

version = "1.3.0"
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


def get_name(a: int, b: int, c: int, ending: str, k: int = 1) -> str:
    results = ""
    def get_onset():
        c1type = ""
        result = ""
        # 70% of the time, the syllable will start with single letter
        # 30% of the time, the syllable will start with a consonant cluster
        if random.randint(0,100) <= 70:
            c1type="single"
        else:
            c1type="cluster"
        # single consonant starts the syllable
        # The way this is done, it appears that as we go down this list, they get more common
        if c1type == "single":
            rn = random.randint(0, 100)
            if rn <= 4:
                result = "px"
            elif rn <= 8:
                result = "tx"
            elif rn <= 12:
                result = "kx"
            elif rn <= 17:
                result = "p"
            elif rn <= 22:
                result = "t"
            elif rn <= 27:
                result = "k"
            elif rn <= 32:
                result = "ts"
            elif rn <= 37:
                result = "f"
            elif rn <= 42:
                result = "s"
            elif rn <= 47:
                result = "h"
            elif rn <= 52:
                result = "v"
            elif rn <= 57:
                result = "z"
            elif rn <= 62:
                result = "m"
            elif rn <= 67:
                result = "n"
            elif rn <= 72:
                result = "ng"
            elif rn <= 77:
                result = "r"
            elif rn <= 82:
                result = "l"
            elif rn <= 87:
                result = "w"
            elif rn <= 92:
                result = "n"
            else:
                result = "'"
        # consonant cluster starts the syllable
        else:
            ro = random.randint(1, 3)
            # start with f
            if ro == 1:
                rp = random.randint(1, 100)
                if rp <= 5:
                    result = "fpx"
                elif rp <= 11:
                    result = "fkx"
                elif rp <= 16:
                    result = "ftx"
                elif rp <= 25:
                    result = "ft"
                elif rp <= 33:
                    result = "fp"
                elif rp <= 42:
                    result = "fk"
                elif rp <= 50:
                    result = "fm"
                elif rp <= 57:
                    result = "fn"
                elif rp <= 63:
                    result = "fng"
                elif rp <= 70:
                    result = "fr"
                elif rp <= 78:
                    result = "fl"
                elif rp <= 86:
                    result = "fw"
                elif rp <= 94:
                    result = "fy"
                else:
                    result = "fr"
            # start with s
            elif ro == 2:
                rp = random.randint(1, 100)
                if rp <= 5:
                    result = "spx"
                elif rp <= 11:
                    result = "skx"
                elif rp <= 16:
                    result = "stx"
                elif rp <= 25:
                    result = "st"
                elif rp <= 33:
                    result = "sp"
                elif rp <= 42:
                    result = "sk"
                elif rp <= 50:
                    result = "sm"
                elif rp <= 57:
                    result = "sn"
                elif rp <= 63:
                    result = "sng"
                elif rp <= 70:
                    result = "sr"
                elif rp <= 78:
                    result = "sl"
                elif rp <= 86:
                    result = "sw"
                elif rp <= 94:
                    result = "sy"
                else:
                    result = "sr"
            # start with ts
            elif ro == 3:
                rp = random.randint(1, 100)
                if rp <= 5:
                    result = "tspx"
                elif rp <= 11:
                    result = "tskx"
                elif rp <= 16:
                    result = "tstx"
                elif rp <= 25:
                    result = "tst"
                elif rp <= 33:
                    result = "tsp"
                elif rp <= 42:
                    result = "tsk"
                elif rp <= 50:
                    result = "tsm"
                elif rp <= 57:
                    result = "tsn"
                elif rp <= 63:
                    result = "tsng"
                elif rp <= 70:
                    result = "tsr"
                elif rp <= 78:
                    result = "tsl"
                elif rp <= 86:
                    result = "tsw"
                elif rp <= 94:
                    result = "tsy"
                else:
                    result = "tsr"
        return result
    def get_nucleus():
        isDiphthong = ""
        result = ""
        # randomly select whether vowel or diphthong
        if random.randint(0,100) > 20:
            isDiphthong="kehe"
        else:
            isDiphthong="srane"
        # randomly select a diphthong
        if (isDiphthong == "srane"):
            rx = random.randint(0, 100)
            if rx <= 25:
                result = "ew"
            elif rx <= 50:
                result = "aw"
            elif rx <= 75:
                result = "ay"
            elif rx <= 100:
                result = "ey"
        # randomly select a vowel
        else:
            ry = random.randint(1, 100)
            if ry <= 25:
                result = "a"
            elif ry <= 40:
                result = "e"
            elif ry <= 55:
                result = "o"
            elif ry <= 70:
                result = "u"
            elif ry <= 80:
                result = "ì"
            elif ry <= 85:
                result = "ä"
            else:
                result = "a"
        return result
    def get_coda():
        result = ""
        rz = random.randint(0, 320)
        if rz <= 4:
            result = "px"
        elif rz <= 8:
            result = "tx"
        elif rz <= 12:
            result = "kx"
        elif rz <= 20:
            result = "p"
        elif rz <= 28:
            result = "t"
        elif rz <= 44:
            result = "k"
        elif rz <= 49:
            result = "k"
        elif rz <= 58:
            result = "m"
        elif rz <= 70:
            result = "n"
        elif rz <= 76:
            result = "ng"
        elif rz <= 80:
            result = "r"
        elif rz <= 85:
            result = "l"
        else:
            result=""  # syllable will end with the vowel from getNucleus()
        return result
    def valid(a, b, c, k) -> bool:
        """
        Validate the input vars from the URL - No ridiculousness this time -- at all. :P
        Acceptable Ranges:
        1 ≤ a, b, c ≤ 4
        1 ≤ k ≤ 100
        """
        def isset(x):
            return x is not None and x != ""
        # a, b, c, k not set, usually a fresh referal from index.php
        # Requiring at least a=1 b=1 c=1 k=1 is so lame. So having unset abck is valid
        # Also happens if any or all elements in form are not selected and submitted. Should also be valid
        if not isset(a) or not isset(b) or isset(c) or isset(k):
            return True
        # They all need to be integers
        if not re.match('/^\d+$/', a + b + c + k):
            return False
        # disallow generating HRH.gif amounts of names
        if k > 100:
            return False
        # lolwut, zero syllables? Negative syllables?
        if a < 1 or b < 1 or c < 1 or k < 1:
            return False;
        # Probably Vawmataw or someone trying to be funny by generating HRH.gif amounts of syllables
        elif a > 4 or b > 4 or c > 4:
            return False
        # they are all set and with values between and including 1 thru 4
        else:
            return True
    if not valid(a, b, c, k):
        results = "Nice try. ;D"
    else:
        a, b, c, k = int(a), int(b), int(c), int(k)
        mk = 0
        # Do entire generator process n times
        while (mk < k):
            i = 0
            # BUILD FIRST NAME
            results += f"{get_onset()}{get_nucleus()}".capitalize()  # first syllable: CV
            while i < a - 1:
                results += f"{get_onset()}{get_nucleus()}"  # some more CV until `a` syllables
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
'  → (disappears)
```"""


def get_version() -> str:
    res = requests.get(f"{api_url}/version")
    return format_version(res.text)
