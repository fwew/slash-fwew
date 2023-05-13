#!/usr/bin/env python3

import json
import requests

api_url = "http://localhost:10000/api"

freq_table_onset = {
    'p': 0,
    # Consonent clusters will be added in runtime
}

freq_table_nuclei = {
    'a': 0,
}

freq_table_end = {
    'p': 0
}

superclusters = {}

romanization = {
    # Vowels
    "a": "a",
    "i": "i",
    "ɪ": "ì",
    "o": "o",
    "ɛ": "e",
    "u": "u",
    "æ": "ä",
    # Diphthongs
    "aw": "aw",
    "ɛj": "ey",
    "aj": "ay",
    "ɛw": "ew",
    # Psuedovowels
    "ṛ": "rr",
    "ḷ": "ll",
    # Consonents
    "t": "t",
    "p": "p",
    "ʔ": "'",
    "n": "n",
    "k": "k",
    "l": "l",
    "s": "s",
    "ɾ": "r",
    "j": "y",
    "t͡s": "ts",
    "t'": "tx",
    "m": "m",
    "v": "v",
    "w": "w",
    "h": "h",
    "ŋ": "ng",
    "z": "z",
    "k'": "kx",
    "p'": "px",
    "f": "f",
    "r": "r",
    # Reef dialect
    "b": "px",
    "d": "tx",
    "g": "kx",
    "ʃ": "sy",
    "tʃ": "tsy",
    "ʊ": "ù",
    # mistakes and rarities
    "ʒ": "tsy",
    "": "",
    " ": ""
}

def table_manager_onset(x:str):
    if x in freq_table_onset:
        freq_table_onset[x] += 1
    else:
        freq_table_onset[x] = 1

def table_manager_nuclei(x:str):
    if x in freq_table_nuclei:
        freq_table_nuclei[x] += 1
    else:
        freq_table_nuclei[x] = 1

def table_manager_end(x:str):
    if x in freq_table_end:
        freq_table_end[x] += 1
    else:
        freq_table_end[x] = 1

def table_manager_supercluster(x:str, y:str):
    # Decode the cluster
    a = ""
    b = ""
    i = 1
    if y.startswith("ts") :
        a = "ts"
        i = 2
    elif y.startswith("s") :
        a = "s"
    elif y.startswith("f") :
        a = "f"
    else:
        print("Some weird consonent cluster beginning")

    b = y[i:]
    
    if x in superclusters:
        if a in superclusters[x]:
            if b in superclusters[x][a]:
                i += 1
            else:
                superclusters[x][a].append(b)
        else:
            superclusters[x][a] = [b]
    else:
        superclusters[x] = {}
        superclusters[x][a] = [b]

def distros():
    global freq_table_onset
    global freq_table_nuclei
    global freq_table_end
    global superclusters

    z = 0

    dictionary = requests.get(f"{api_url}/list")
    dictionary = json.loads(dictionary.text)
    
    #print(a[5]['IPA'])

    #with open('dictionary-v2.txt', 'r') as a:
    for entry in dictionary:
        coda = ""
        start_cluster = ""

        words = entry['IPA'].split(' ')
        
        for word in words:
            syllables = word.split('.')

            for syllable in syllables:
                # get rid of the garbage
                syllable = syllable.replace("·", "").replace("ˈ","").removeprefix("[").removesuffix("]").removeprefix('ˌ')

                # keep track of where we are in the syllable
                i = 0
                        
                #
                # Syllable part 1
                #
                start_cluster = ""
                
                # Affricative?
                if(syllable.startswith('t͡s')):
                    if(syllable[3] in {"p", "k", "t"}):
                        if(syllable[4] == "'"):
                            i = 5
                        else:
                            i = 4
                        start_cluster = romanization[syllable[0:3]] + romanization[syllable[3:i]]
                    elif(syllable[3] in {"l", "ɾ", "m", "n", "ŋ", "w", "j"}):
                        i = 4
                        start_cluster = romanization[syllable[0:3]] + romanization[syllable[3:i]]
                    else:
                        i = 3
                # Some other clustarable thing?
                elif(syllable[0] in {"f", "s"}):
                    if(syllable[1] in {"p", "k", "t"}):
                        if(syllable[2] == "'"):
                            i = 3
                        else:
                            i = 2
                        start_cluster = romanization[syllable[0]] + romanization[syllable[1:i]]
                    elif(syllable[1] in {"l", "ɾ", "m", "n", "ŋ", "w", "j"}):
                        i = 2
                        start_cluster = romanization[syllable[0]] + romanization[syllable[1:i]]
                    else:
                        i = 1
                # Something that can ejective?
                elif(syllable[0] in {"p", "k", "t"}):
                    if(syllable[1] in {"'", "ʃ"}):
                        i = 2
                    else:
                        i = 1
                # None of the above
                elif(syllable[0] in {"ʔ", "l", "ɾ", "h", "m", "n", "ŋ", "v", "w", "j", "z", "ʃ", "ʒ", "b", "d", "g"}):
                    i = 1
                    
                if(i > 1 and (syllable[0:i].startswith("f") or syllable[0:i].startswith("s"))):
                    table_manager_onset(romanization[syllable[0]] + romanization[syllable[1:i]])
                elif(i > 3 and syllable[0:i].startswith('t͡s')):
                    table_manager_onset(romanization[syllable[0:3]] + romanization[syllable[3:i]])
                else:
                    table_manager_onset(romanization[syllable[0:i]])

                if coda != "" and start_cluster != "":
                    table_manager_supercluster(coda, start_cluster)
                    coda = ""
                    start_cluster = ""

                #
                # Nucleus of the syllable
                #

                if(i + 1 < len(syllable) and syllable[i+1] in {'j', 'w'}):
                    table_manager_nuclei(romanization[syllable[i:i+2]])
                    i += 2
                elif(i + 1 < len(syllable) and syllable[i] in {'r', 'l'}):
                    table_manager_nuclei(romanization[syllable[i:i+2]])
                    continue # Do not count psuedovowels towards the final consonent distribution
                else:
                    table_manager_nuclei(romanization[syllable[i]])
                    i += 1

                #
                # Syllable-final consonents
                #

                if(i >= len(syllable)):
                    table_manager_end(" ")
                    coda = ""
                elif(i + 1 == len(syllable)):
                    if(not syllable[i] in {":", '̣', "'"}): # fìtsenge lu kxanì
                        table_manager_end(romanization[syllable[i]])
                        coda = romanization[syllable[i]]
                    else:
                        table_manager_end(" ")
                elif(i + 1 < len(syllable)):
                    if(syllable.endswith('k̚')):
                        table_manager_end(romanization['k'])
                        coda = romanization['k']
                    elif(syllable.endswith('p̚')):
                        table_manager_end(romanization['p'])
                        coda = romanization['p']
                    elif(syllable.endswith('t̚')):
                        table_manager_end(romanization['t'])
                        coda = romanization['t']
                    elif(syllable.endswith('ʔ̚')):
                        table_manager_end(romanization['ʔ'])
                        coda = romanization['ʔ']
                    elif (syllable[i:i+2] == "ss"):
                        table_manager_end(" ") # oìsss only
                    else:
                        table_manager_end(romanization[syllable[i:i+2]])
                        coda = romanization[syllable[i:i+2]]
                else:
                    print("You should not be seeing this")
    
    #
    # Format the output
    #

    freq_table_onset = dict(sorted(freq_table_onset.items(), key=lambda item: item[1], reverse = True))
    freq_table_nuclei = dict(sorted(freq_table_nuclei.items(), key=lambda item: item[1], reverse = True))
    freq_table_end = dict(sorted(freq_table_end.items(), key=lambda item: item[1], reverse = True))
    
    return [freq_table_onset, freq_table_nuclei, freq_table_end, superclusters]
