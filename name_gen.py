# cSpell: disable
# Web-based Na'vi Name Generator! by Uniltìrantokx te Skxawng aka Irtaviš Ačankif
# Translated into Python3 by Tirea Aean

# For use with the commands "name", "name-alu" and "name-single"
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
