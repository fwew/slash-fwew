# cSpell: disable
# Web-based Na'vi Name Generator! by Uniltìrantokx te Skxawng aka Irtaviš Ačankif
# Translated into Python3 by Tirea Aean
import random
import re
from frequencyscript_ipa import distros

# Import 3 dictionaries and get info from them
phonemes = distros()

#onset_distros = phonemes[0]
non_clusters = phonemes[0]
clusters = phonemes[1]
nucleus_distros = phonemes[2]
end_distros = phonemes[3]
triple_consonants = phonemes[4]

non_cluster_keys = list(non_clusters.keys())
cluster_keys = []
nucleus_keys = list(nucleus_distros.keys())
end_keys = list(end_distros.keys())
super_keys = list(triple_consonants.keys())

non_cluster_onset_numbers = {}
cluster_onset_numbers = []
nucleus_numbers = {}
end_numbers = {}
super_numbers = {}

# Onset calculations
max_non_cluster = 0
non_cluster_total = len(non_cluster_keys)
cluster_total = 0

x = 0
for i in range(0,non_cluster_total):
    non_cluster_onset_numbers[i] = x
    x += non_clusters[non_cluster_keys[i]]

max_non_cluster = x

x = 0
for i in clusters.keys():
    for j in clusters[i].keys():
        cluster_onset_numbers.append(x)
        cluster_keys.append([i,j])
        x += clusters[i][j]
        cluster_total += 1

max_rand_onsets = x + max_non_cluster

onsets = non_cluster_total + cluster_total

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

def get_onset():
    global max_non_cluster
    global max_rand_onsets

    x = random.randint(0,max_rand_onsets)

    # If it's high enough to be a cluster
    if(x > max_non_cluster):
        x -= max_non_cluster
        for i in range(0,cluster_total - 1):
            if cluster_onset_numbers[i] >= x:
                return cluster_keys[i]
        return cluster_keys[-1]
    # Else
    for i in range(0,non_cluster_total - 1):
        if non_cluster_onset_numbers[i + 1] >= x:
            return [non_cluster_keys[i]]
    return [non_cluster_keys[-1]]

def get_nucleus():
    global nuclei
    global max_rand_nuclei

    x = random.randint(0,max_rand_nuclei)
    for i in range(0,nuclei - 1):
        if nucleus_numbers[i + 1] >= x:
            return nucleus_keys[i]
    return nucleus_keys[-1]

def get_coda():
    global ends
    global max_rand_ends

    x = random.randint(0,max_rand_ends)
    for i in range(0,ends - 1):
        if end_numbers[i + 1] >= x:
            return end_keys[i]
    return end_keys[-1]

# Helper function to make ejectives into voiced plosives
def reef_ejective(loader: str):
    if loader[-1] != "x":
        return loader
    loader = loader[:-1]
    if loader[-1] == "p":
        loader = loader[:-1] + "b"
    elif loader[-1] == "t":
        loader = loader[:-1] + "d"
    elif loader[-1] == "k":
        loader = loader[:-1] + "g"
    return loader
    
# Returns a single name for the lib.py functions that forward it to Discord
def get_single_name(i: int, dialect: str):
    loader = ""
    onset = ""
    nucleus = ""
    coda = ""

    i = rand_if_zero(int(i))
            
    #x = 0
    for x in range(i): #loop I times
        onset = get_onset()

        #
        # "Triple consonants" are whitelisted
        #
        if len(onset) > 1 and len(coda) > 0: #don't want errors
            if not(coda == "t" and onset[0] == "s"): #t-s-kx is valid as ts-kx
                if not(coda in triple_consonants and onset[0] in triple_consonants[coda] and onset[1] in triple_consonants[coda][onset[0]]):
                    onset = [onset[1]]

        #
        # Nucleus
        #
        nucleus = get_nucleus()#.strip()

        psuedovowel = False
        # Disallow syllables starting with a psuedovowel
        if nucleus in {"rr","ll"}:
            psuedovowel = True
            # Disallow onsets from imitating the psuedovowel
            if len(onset[0]) > 0:
                if onset[-1][-1] == nucleus[0]:
                    onset = ["'"]
            # If no onset, disallow the previous coda from imitating the psuedovowel
            elif len(loader) > 0:
                if loader[-1] == nucleus[0] or loader[-1] in ["a", "e", "ì", "o", "u", "i", "ä", "ù"]:
                    onset = ["'"]
            # No onset or loader thing?  Needs a thing to start
            else:
                onset = ["'"]

        # No identical vowels togther in forest
        elif dialect == "forest" and onset[0] == "" and len(loader) > 0 and loader[-1] == nucleus[0]:
            onset = ["y"]

        # Now that the onsets have settled, make sure they don't repeat a letter from the coda
        # No "ng-n" "t-tx", "o'-lll" becoming "o'-'ll" or anything like that
        if len(onset[0]) > 0 and len(loader) > 0:
            length = -1
            if len(coda) > 1: #in case of ng, px, tx or kx
                length = -len(coda)
            if onset[0][0] == loader[length]:
                onset = [""] # disallow "l-ll", "r-rr", "ey-y" and "aw-w"
                
        #
        # Coda
        #
        if psuedovowel:
            coda = ""
        else:
            coda = get_coda().strip()
        
        #
        # Put everything into the string
        #

        # You shawm futa sy and tsy become sh and ch XD
        if dialect == "reef" and onset[-1] == "y":
            if onset[0] == "ts":
                onset = "ch"
            elif onset[0] == "s":
                onset = "sh"

        # Onset
        for k in onset:
            loader += k
        
        # Syllable-initial ejectives become voiced plosives in reef
        if dialect == "reef" and len(loader) > 1: # In reef dialect,
            if loader[-1] == "x": # If there's an ejective in the onset
                if not (len(loader) > 2 and loader[-3] in ["s", "f"]): # that's not in a cluster,
                    loader = reef_ejective(loader) # it becomes a voiced plosive
                    if len(loader) > 2 and loader[-2] == "x": # adge/egdu exception
                        loader = reef_ejective(loader[:-1]) + loader[-1]
            elif not psuedovowel and len(loader) > 2 and loader[-1] == "'" and loader[-2] != nucleus[0]: # 'a'aw is optionally 'aaw (the generator leaves it in)
                if loader[-2] in ["a", "e", "ì", "o", "u", "i", "ä", "ù"]:#, "w", "y"]: does kaw'it become kawit?
                    # if nucleus[0] in ["a", "e", "ì", "o", "u", "i", "ä", "ù"]: # psudeovowel boolean takes care of this
                    loader = loader[:-1]

        # Nucleus and coda
        loader += (nucleus + coda)

    # Forest has no u/ù distinction
    if dialect == "forest":
        loader = loader.replace("ù","u")

    return glottal_caps(loader)

def rand_if_zero(x: int):
    if x == 0:
        return random.randint(2,4)
    return x

def chart_entry(x:str, y:int, width:int):
    ys = str(y)
    spaces = width - len(x) - len(ys)
    stringtsyìp = x
    for i in range(0,spaces):
        stringtsyìp += " "
    stringtsyìp += ys

    return stringtsyìp + "|"

def get_phoneme_frequency_chart():
    entries = ["| Onset:|Nuclei:|Ending:|", "|=======|=======|=======|"]

    # Onsets
    i = 2
    for a in non_clusters.keys():
        entries.append("|" + chart_entry(a, non_clusters[a],7))
        i += 1

    # Nuclei
    i = 2
    for a in nucleus_keys:
        entries[i] += chart_entry(a, nucleus_distros[a],7)
        i += 1

    while i < len(entries):
        entries[i] += "       |"
        i += 1

    # Ends
    i = 2
    for a in end_keys:
        entries[i] += chart_entry(a, end_distros[a],7)
        i += 1
    
    while i < len(entries):
        entries[i] += "       |"
        i += 1

    # Top
    entries_2 = "```Phoneme distributions:\n"
    for a in entries:
        entries_2 += a + "\n"

    # Clusters
    entries = ["\nClusters:", "  | f:| s:|ts:|", "==|===|===|===|"]
    
    cluster_ends = ["k", "kx", "l", "m", "n", "ng", "p", "px", "t", "tx", "r", "w", "y"]

    for a in cluster_ends:
        entries.append(chart_entry(a,"",2))
    
    # "f" clusters
    i = 3
    for part_two in cluster_ends:
        for part_one in clusters.keys():
            if part_two in clusters[part_one]:
                entries[i] += chart_entry("", clusters[part_one][part_two], 3)
            else:
                entries[i] += "   |"
        i += 1
    
    for a in entries:
        entries_2 += a + "\n"

    entries_2 += "```"

    return entries_2

# Assistant command to capitalize words that begin with a glottal stop
# If it begins with an apostrophe, capitalize the second letter
def glottal_caps(s: str):
    if s.startswith("'"):
        return s[:1].lower() + s[1:].capitalize()
    return s.capitalize()


# For use with the command "name"
def valid(n, s_arr) -> bool:
    """
    Validate the input vars from the URL - No ridiculousness this time -- at all. :P
    Acceptable Ranges:
    1 ≤ n ≤ 50 (more than that and you might exceed the 2000 character limit)
    1 ≤ any value in s_srr ≤ 4
    """
    def is_set(x):
        return x is not None and x != ""
    # n, s1, s2, s3, not set, usually a fresh referral from index.php
    # Requiring at least n=1 s1=1 s2=1 s3=1 is so lame. So having unset n, s1, s2, s3, is valid
    # Also happens if any or all elements in form are not selected and submitted. Should also be valid

    # Check all syllable values for validity
    set_syllables = False
    for s in s_arr:
        # See if the syllable count is specified
        if is_set(s):
            set_syllables = True
            break
    
    # Most common case is no numbers specified
    if not is_set(n) and not set_syllables:
        return True
    # They all need to be integers
    if not type(n) is int:
        return False
    # disallow generating HRH.gif amounts of names
    if n > 50:
        return False
    # lolwut, non-positive name count?
    if n < 1:
        return False

    # Not worth checking again if we know none of them are set
    if set_syllables:
        for s in s_arr:
            # They all need to be integers
            if not type(s) is int:
                return False
            # lolwut, negative syllables?
            if s < 0:
                return False
            # Probably Vawmataw or someone trying to be funny by generating HRH.gif amounts of syllables
            if s > 4:
                return False
    # they are all set and with values between and including 1 thru 4
    return True
