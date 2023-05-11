#!/usr/bin/env python3

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
    "ɛw": "ey",
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
    # mistakes and rarities
    "ʒ": "tsy",
    "ʃ": "sy",
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

def chart_entry(x:str, y:int):
    ys = str(y)
    spaces = 7 - len(x) - len(ys)
    stringtsyìp = x
    for i in range(0,spaces):
        stringtsyìp += " "
    stringtsyìp += ys

    return stringtsyìp

def distros():
    global freq_table_onset
    global freq_table_nuclei
    global freq_table_end
    global superclusters

    z = 0
    with open('dictionary-v2.txt', 'r') as a:
        for b in a:
            # skip the first line
            if z == 0:
                z += 1
                continue

            coda = ""
            start_cluster = ""

            c = b.split('\t')

            d = c[2].split('.')

            #print(d)
            for e in d:

                f = e.split(' ')

                for g in f:
                    # get rid of the garbage
                    h = g.replace("·", "").replace("ˈ","").removeprefix("[").removesuffix("]").removeprefix('ˌ')

                    # keep track of where we are in the syllable
                    i = 0
                    
                    #
                    # Syllable part 1
                    #
                    start_cluster = ""

                    # Affricative?
                    if(h.startswith('t͡s')):
                        if(h[3] in {"p", "k", "t"}):
                            if(h[4] == "'"):
                                i = 5
                            else:
                                i = 4
                            start_cluster = romanization[h[0:3]] + romanization[h[3:i]]
                        elif(h[3] in {"l", "ɾ", "m", "n", "ŋ", "w", "j"}):
                            i = 4
                            start_cluster = romanization[h[0:3]] + romanization[h[3:i]]
                        else:
                            i = 3
                    # Some other clustarable thing?
                    elif(h[0] in {"f", "s"}):
                        if(h[1] in {"p", "k", "t"}):
                            if(h[2] == "'"):
                                i = 3
                            else:
                                i = 2
                            start_cluster = romanization[h[0]] + romanization[h[1:i]]
                        elif(h[1] in {"l", "ɾ", "m", "n", "ŋ", "w", "j"}):
                            i = 2
                            start_cluster = romanization[h[0]] + romanization[h[1:i]]
                        else:
                            i = 1
                    # Something that can ejective?
                    elif(h[0] in {"p", "k", "t"}):
                        if(h[1] == "'"):
                            i = 2
                        else:
                            i = 1
                    # None of the above
                    elif(h[0] in {"ʔ", "l", "ɾ", "h", "m", "n", "ŋ", "v", "w", "j", "z", "ʃ", "ʒ"}):
                        i = 1
                    
                    if(i > 1 and (h[0:i].startswith("f") or h[0:i].startswith("s"))):
                        table_manager_onset(romanization[h[0]] + romanization[h[1:i]])
                    elif(i > 3 and h[0:i].startswith('t͡s')):
                        table_manager_onset(romanization[h[0:3]] + romanization[h[3:i]])
                    else:
                        table_manager_onset(romanization[h[0:i]])

                    if coda != "" and start_cluster != "":
                        table_manager_supercluster(coda, start_cluster)
                        coda = ""
                        start_cluster = ""

                    #
                    # Nucleus of the syllable
                    #

                    if(i + 1 < len(h) and h[i+1] in {'j', 'w'}):
                        table_manager_nuclei(romanization[h[i:i+2]])
                        i += 2
                    elif(i + 1 < len(h) and h[i] in {'r', 'l'}):
                        table_manager_nuclei(romanization[h[i:i+2]])
                        continue # Do not count psuedovowels towards the final consonent distribution
                    else:
                        table_manager_nuclei(romanization[h[i]])
                        i += 1

                    #
                    # Syllable-final consonents
                    #

                    if(i >= len(h)):
                        table_manager_end(" ")
                        coda = ""
                    elif(i + 1 == len(h)):
                        if(not h[i] in {":", '̣', "'"}): # fìtsenge lu kxanì
                            table_manager_end(romanization[h[i]])
                            coda = romanization[h[i]]
                        else:
                            table_manager_end(" ")
                    elif(i + 1 < len(h)):
                        if(h.endswith('k̚')):
                            table_manager_end(romanization['k'])
                            coda = romanization['k']
                        elif(h.endswith('p̚')):
                            table_manager_end(romanization['p'])
                            coda = romanization['p']
                        elif(h.endswith('t̚')):
                            table_manager_end(romanization['t'])
                            coda = romanization['t']
                        elif(h.endswith('ʔ̚')):
                            table_manager_end(romanization['ʔ'])
                            coda = romanization['ʔ']
                        elif (h[i:i+2] == "ss"):
                            table_manager_end(" ") # oìsss only
                        else:
                            table_manager_end(romanization[h[i:i+2]])
                            coda = romanization[h[i:i+2]]
                    else:
                        print("You should not be seeing this")
        
    #
    # Format the output
    #

    freq_table_onset = dict(sorted(freq_table_onset.items(), key=lambda item: item[1], reverse = True))
    freq_table_nuclei = dict(sorted(freq_table_nuclei.items(), key=lambda item: item[1], reverse = True))
    freq_table_end = dict(sorted(freq_table_end.items(), key=lambda item: item[1], reverse = True))
    #superclusters = dict(sorted(superclusters.items(), key=lambda item: item[1], reverse = True))
    
    return [freq_table_onset, freq_table_nuclei, freq_table_end, superclusters]
