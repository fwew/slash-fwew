# cSpell: disable
# Web-based Na'vi Name Generator! by Uniltìrantokx te Skxawng aka Irtaviš Ačankif
# Translated into Python3 by Tirea Aean
import random
import re
from frequencyscript_ipa import distros

# Import 3 dictionaries and get info from them
phonemes = distros()

onset_distros = phonemes[0]
nucleus_distros = phonemes[1]
end_distros = phonemes[2]
superclusters = phonemes[3]

onset_keys = list(onset_distros.keys())
nucleus_keys = list(nucleus_distros.keys())
end_keys = list(end_distros.keys())
super_keys = list(superclusters.keys())

onset_numbers = {}
nucleus_numbers = {}
end_numbers = {}
super_numbers = {}

# Onset calculations
onsets = len(onset_keys)

x = 0
for i in range(0,onsets):
    onset_numbers[i] = x
    x += onset_distros[onset_keys[i]]

max_rand_onsets = x

# Nucleus calculations
nuclei = len(nucleus_keys)

x = 0
for i in range(0,nuclei):
    nucleus_numbers[i] = x
    x += nucleus_distros[nucleus_keys[i]]

max_rand_nuclei = x

# End calculations
ends = len(end_keys)

x = 0
for i in range(0,ends):
    end_numbers[i] = x
    x += end_distros[end_keys[i]]

max_rand_ends = x

# Supercluster calculations
supers = len(super_keys)

#
# Methods
#

def get_onset_2():
    global onsets
    global max_rand_onsets

    x = random.randint(0,max_rand_onsets)
    for i in range(0,onsets - 1):
        if onset_numbers[i + 1] > x:
            return onset_keys[i]
    return onset_keys[-1]

def get_nucleus_2():
    global nuclei
    global max_rand_nuclei

    x = random.randint(0,max_rand_nuclei)
    for i in range(0,nuclei - 1):
        if nucleus_numbers[i + 1] > x:
            return nucleus_keys[i]
    return nucleus_keys[-1]

def get_coda_2(nucleus: str):
    if(nucleus in {"ll", "rr"}):
        return ""

    global ends
    global max_rand_ends

    x = random.randint(0,max_rand_ends)
    for i in range(0,ends - 1):
        if end_numbers[i + 1] > x:
            return end_keys[i]
    return end_keys[-1]

# Assistant command to capitalize words that begin with a glottal stop
# If it begins with an apostrophe, capitalize the second letter
def glottal_caps(s: str):
    if s.startswith("'"):
        return s[:1].lower() + s[1:].capitalize()
    return s.capitalize()

def get_onset():
    c1type = ""
    result = ""
    # 70% of the time, the syllable will start with single letter
    # 30% of the time, the syllable will start with a consonant cluster
    if random.randint(0, 100) <= 70:
        c1type = "single"
    else:
        c1type = "cluster"
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
    if random.randint(0, 100) > 20:
        isDiphthong = "kehe"
    else:
        isDiphthong = "srane"
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
        result = ""  # syllable will end with the vowel from getNucleus()
    return result


# For use with the command "name"
def valid(a, b, c, k) -> bool:
    """
    Validate the input vars from the URL - No ridiculousness this time -- at all. :P
    Acceptable Ranges:
    1 ≤ a, b, c ≤ 4
    1 ≤ k ≤ 40 (more than that and you might exceed the 2000 character limit)
    """
    def is_set(x):
        return x is not None and x != ""
    # a, b, c, k not set, usually a fresh referral from index.php
    # Requiring at least a=1 b=1 c=1 k=1 is so lame. So having unset a, b, c, k is valid
    # Also happens if any or all elements in form are not selected and submitted. Should also be valid
    if not is_set(a) and not is_set(b) and is_set(c) and is_set(k):
        return True
    # They all need to be integers
    if not type(a) is int or not type(b) is int or not type(c) is int or not type(k) is int:
        return False
    # disallow generating HRH.gif amounts of names
    if k > 50:
        return False
    # lolwut, negative syllables?
    if a < 0 or b < 0 or c < 0 or k < 1:
        return False
    # Probably Vawmataw or someone trying to be funny by generating HRH.gif amounts of syllables
    elif a > 4 or b > 4 or c > 4:
        return False
    # they are all set and with values between and including 1 thru 4
    else:
        return True

# For use with the command "name-alu"
def valid_alu(adj_mode: str, b, k) -> bool:
    """
    Validate the input vars from the URL - No ridiculousness this time -- at all. :P
    Acceptable Ranges:
    1 ≤ b ≤ 4
    1 ≤ k ≤ 50 (more than that and you might exceed the 2000 character limit)
    """
    def is_set(x):
        return x is not None and x != ""
    # b, k not set, usually a fresh referral from index.php
    # Requiring at least b=1 k=1 is so lame. So having unset b, k is valid
    # Also happens if any or all elements in form are not selected and submitted. Should also be valid

    # But adj_mode works differently
    if not adj_mode in ["any", "something", "none", "normal adjective", "genitive noun", "origin noun"]:
        return False
    if not is_set(b) and is_set(k):
        return True
    # They all need to be integers
    if not type(b) is int or not type(k) is int:
        return False
    # disallow generating HRH.gif amounts of names
    if k > 50:
        return False
    # lolwut, zero syllables? Negative syllables?
    if b < 0 or k < 1:
        return False
    # Probably Vawmataw or someone trying to be funny by generating HRH.gif amounts of syllables
    elif b > 4:
        return False
    # they are all set and with values between and including 1 thru 4
    else:
        return True
