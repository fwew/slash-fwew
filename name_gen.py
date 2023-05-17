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
superclusters = phonemes[4]

non_cluster_keys = list(non_clusters.keys())
cluster_keys = []
nucleus_keys = list(nucleus_distros.keys())
end_keys = list(end_distros.keys())
super_keys = list(superclusters.keys())

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

def get_onset_2():
    global onsets
    global non_cluster_onsets
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

def get_nucleus_2():
    global nuclei
    global max_rand_nuclei

    x = random.randint(0,max_rand_nuclei)
    for i in range(0,nuclei - 1):
        if nucleus_numbers[i + 1] >= x:
            return nucleus_keys[i]
    return nucleus_keys[-1]

def get_coda_2():
    global ends
    global max_rand_ends

    x = random.randint(0,max_rand_ends)
    for i in range(0,ends - 1):
        if end_numbers[i + 1] >= x:
            return end_keys[i]
    return end_keys[-1]

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
        entries.append("|" + chart_entry(a, non_clusters    [a],7))
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
    entries = ["\nClusters:\n", "  | f:| s:|ts:|", "==|===|===|===|"]
    
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
