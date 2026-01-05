#!/usr/bin/env python3
import os
from datetime import datetime
from pathlib import Path

from disnake import Intents, Embed
from disnake.ext import commands
from disnake.ext.commands import Param
from dotenv import load_dotenv

import Paginator
from lib import *

load_dotenv(os.path.join(Path.cwd(), ".env"))
token = os.environ.get("TOKEN")

logfile = "log.txt"

developer = 166401675840585728

authorized_servers = [
    935489523155075092,  # sndb0x
    395558141162422275,  # fbts
    154318499722952704,  # lnc
    860933619296108564,  # gfs
    1058520916612624536,  # fr
    1061696962304426025,  # fr
    1103339942538645605,  # fr
    1065673594354548757,  # ru
    1063774395748847648,  # ru
    1215999922470653982,  # ru
    1336266921070428192,  # sds
    1060288947596570624,  # 4023
    1067521820401619004,  # 0422
    1061325007998943392,  # 1537
    1075866581265043548,  # 2565
    1062822191961489408,  # nm01
    1130543222788194396,  # 5426
    1289130826902147124,  # 2380
    1326001509661540412,  # 4288
    1386631379554664528,  # 8400
    1429999273994621059,  # 6234
]

intents = Intents.default()
intents.message_content = True
flags = commands.CommandSyncFlags.default()
flags.sync_commands_debug = True
fwew_bot = commands.Bot(command_prefix="?", help_command=None, intents=intents,
                        command_sync_flags=flags)  # , sync_permissions=True #, test_guilds=authorized_servers)

languages = ["en", "de", "es", "et", "fr", "hu", "ko",
             "nl", "pl", "pt", "ru", "sv", "tr", "uk"]


@fwew_bot.event
async def on_ready():
    with open(logfile, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        log.write(timestamp)
        log.write(" | ")
        log.write("login: ")
        log.write(fwew_bot.user.name)
        log.write(" ")
        log.write(str(fwew_bot.user.id))
        log.write("\n")


@fwew_bot.event
async def on_guild_join(guild):
    if guild.id not in authorized_servers:
        await guild.leave()


@fwew_bot.slash_command(name="fwew", description="search word(s) na'vi -> english")
async def fwew(inter,
               words=Param(description="the na'vi word(s) to look up"),
               ipa=Param(description="set to true to show IPA",
                         default=False,
                         choices=["true", "false"]),
               lang=Param(description="Language for results",
                          default=None,
                          choices=languages),
               check_fixes=Param(name="check_fixes",
                                 description="Search faster by not checking for prefixes, suffixes and infixes",
                                 default="true",
                                 choices=["true", "false"]),
               reef=Param(description="Show reef dialect stuff",
                          default=False,
                          choices=["true", "false"]),
               strict=Param(description="Search forest words only",
                          default=False,
                          choices=["true", "false"])):
    """
    search word(s) na'vi -> english

    Parameters
    ----------
    words: the na'vi word(s) to look up
    ipa: set to true to show IPA
    lang: the two-letter language-code for results (default: en)
    """
    if lang is None:
        lang = get_language(inter)
    showIPA = True if ipa == "true" else False
    checkFixesString = True if check_fixes == "true" else False
    strict = True if strict == "true" else False
    await Paginator.Simple().start(inter, pages=get_fwew(lang, words, showIPA, checkFixesString, reef, strict))


@fwew_bot.slash_command(name="search-classic", description="search word(s) english -> na'vi")
async def search_classic(inter,
                         words=Param(
                             description="the english word(s) to look up"),
                         ipa=Param(description="set to true to show IPA",
                                   default=False,
                                   choices=["true", "false"]),
                         lang=Param(description="Language for results",
                                    default=None,
                                    choices=languages)):
    """
    search words english -> na'vi

    Parameters
    ----------
    words: the english word(s) to look up
    lang: the two-letter language-code for results (default: en)
    """
    if lang is None:
        lang = get_language(inter)
    showIPA = True if ipa == "true" else False
    await Paginator.Simple().start(inter, pages=get_fwew_reverse(lang, words, showIPA))


@fwew_bot.slash_command(name="translate", description="Concise sentence-like translations")
async def translate(inter,
                        words=Param(
                            description="the Na'vi word(s) to look up"),
                        lang=Param(description="Language for results",
                            default=None,
                            choices=languages)):
    """
    search words english -> na'vi

    Parameters
    ----------
    words: the english word(s) to look up
    lang: the two-letter language-code for results (default: en)
    """
    if lang is None:
        lang = get_language(inter)
    await inter.response.send_message(get_translation(words, lang))


@fwew_bot.slash_command(name="search", description="search word(s) any direction")
async def search(inter,
                 words=Param(description="the word(s) to look up"),
                 ipa=Param(description="set to true to show IPA",
                           default=False,
                           choices=["true", "false"]),
                 lang=Param(description="Language for results",
                            default=None,
                            choices=languages),
                 reef=Param(description="Allow reef dialect searches",
                            default=False,
                            choices=["true", "false"])):
    """
    search words (direction idependent)

    Parameters
    ----------
    words: the word(s) to look up
    lang: the two-letter language-code for results (default: en)
    """
    if lang is None:
        lang = get_language(inter)
    showIPA = True if ipa == "true" else False
    await Paginator.Simple().start(inter, pages=get_search(lang, words, showIPA, reef))
    # await inter.response.send_message(get_search(lang, words, showIPA))


@fwew_bot.slash_command(name="profanity", description="get the list of Na'vi vulgar curse words / profanity")
async def profanity(inter,
                    ipa=Param(description="set to true to show IPA",
                              default=False,
                              choices=["true", "false"]),
                    lang=Param(description="Language for results",
                               default=None,
                               choices=languages)):
    """
    get the list of Na'vi vulgar curse words / profanity

    Parameters
    ----------
    ipa: set to true to show IPA
    lang: the two-letter language-code for results (default: en)
    """
    if lang is None:
        lang = get_language(inter)
    showIPA = True if ipa == "true" else False
    await Paginator.Simple().start(inter, pages=get_profanity(lang, showIPA))


@fwew_bot.slash_command(name="homonyms", description="list all words with more than one meaning")
async def homonyms(inter,
                   ipa=Param(description="set to true to show IPA",
                             default=False,
                             choices=["true", "false"]),
                   lang=Param(description="Language for results",
                              default=None,
                              choices=languages),
                   reef=Param(description="Show reef dialect stuff",
                              default=False,
                              choices=["true", "false"])):
    """
    list all words with more than one meaning
    """
    if lang is None:
        lang = get_language(inter)
    await Paginator.Simple().start(inter, pages=get_homonyms(ipa, lang, reef))


@fwew_bot.slash_command(name="multi-ipa", description="list all words with more than one meaning")
async def multi_ipa(inter,
                    lang=Param(description="Language for results",
                               default=None,
                               choices=languages),
                    reef=Param(description="Show reef dialect stuff",
                               default=False,
                               choices=["true", "false"])):
    """
    list all words with more than one meaning
    """
    if lang is None:
        lang = get_language(inter)
    await Paginator.Simple().start(inter, pages=get_multi_ipa(lang, reef))


@fwew_bot.slash_command(name="dict-len", description="list the number of words in the dictionary")
async def dict_len(inter,
                   lang=Param(description="Language for results",
                              default=None,
                              choices=languages)):
    """
    list the number of words in the dictionary
    """
    if lang is None:
        lang = get_language(inter)
    await inter.response.send_message(get_dict_len(lang))


@fwew_bot.slash_command(name="source", description="look up the source of na'vi word(s)")
async def source(inter, words=Param(description="the na'vi word(s) for which to find source")):
    """
    look up the source of na'vi word(s)

    Parameters
    ----------
    words: the na'vi word(s) for which to find source
    """
    await inter.response.send_message(get_source(words))


@fwew_bot.slash_command(name="audio", description="get audio for na'vi word(s)")
async def audio(inter, words=Param(description="the na'vi word(s) for which to get audio")):
    """
    get audio for na'vi word(s)

    Parameters
    ----------
    words: the na'vi word(s) for which to get audio
    """
    await inter.response.send_message(get_audio(words))


@fwew_bot.slash_command(name="alphabet", description="get audio for na'vi alphabet letter(s)")
async def alphabet(inter, letters=Param(description="the na'vi letter(s) for which to get audio")):
    """
    get audio for na'vi letter(s)

    Parameters
    ----------
    letters: the na'vi letter(s) for which to get audio
    """
    await inter.response.send_message(get_alphabet(letters))


@fwew_bot.slash_command(name="list", description="list all words with certain characteristics")
async def list(inter,
               where=Param(
                   description="characteristics of the word, such as part of speech, number of syllables, etc."),
               ipa=Param(description="set to true to show IPA",
                         default=False,
                         choices=["true", "false"]),
               lang=Param(description="Language for results",
                          default=None,
                          choices=languages),
               check_digraphs=Param(description="Are the things that look like digraphs in the query actually digraphs?",
                                    default="true",
                                    choices=["true", "maybe", "false"])):
    """
    list all words with certain characteristics

    Parameters
    ----------
    where: characteristics of the word, such as part of speech, number of syllables, etc.
    lang: the two-letter language-code for results (default: en)
    check_digraphs: Should it pay attention to just the letters or what digraphs they represent, too?
    """
    if lang is None:
        lang = get_language(inter)
    await Paginator.Simple().start(inter, pages=get_list(lang, where, ipa, check_digraphs))


@fwew_bot.slash_command(name="random", description="get given number of random entries with certain characteristics")
async def random(inter,
                 n=Param(name="number",
                         description="the number of random words to get"),
                 where=Param(
                     description="characteristics of the word, such as part of speech, number of syllables, etc.",
                     default=None),
                 ipa=Param(description="set to true to show IPA",
                           default=False,
                           choices=["true", "false"]),
                 lang=Param(description="Language for results",
                            default=None,
                            choices=languages),
                 check_digraphs=Param(description="Are the things that look like digraphs in the query actually digraphs?",
                                      default="true",
                                      choices=["true", "maybe", "false"])):
    """
    get given number of random entries with certain characteristics

    Parameters
    ----------
    n: the number of random words to get
    where: characteristics of the word, such as part of speech, number of syllables, etc.
    lang: the two-letter language-code for results (default: en)
    check_digraphs: Should it pay attention to just the letters or what digraphs they represent, too?
    """

    if not n.isdigit():
        await inter.response.send_message("Invalid string in number field")
        return

    if lang is None:
        lang = get_language(inter)
    if where is None:
        await Paginator.Simple().start(inter, pages=get_random(lang, n, ipa))
    else:
        await Paginator.Simple().start(inter, pages=get_random_filter(lang, n, where, ipa, check_digraphs))


@fwew_bot.slash_command(name="number", description="convert or translate numbers between decimal and octal/na'vi")
async def number(inter, n=Param(name="number", description="the number to convert or translate")):
    """
    convert or translate numbers between decimal and octal/na'vi

    Parameters
    ----------
    n: the number to convert or translate
    """
    n2 = n.replace(",", "")
    base = 10
    if n2.startswith("0x"):
        base = 16
    elif n2.startswith("0b"):
        base = 2
    elif n2.startswith("0"):
        base = 8
    try:
        num = int(n2, base)
        await inter.response.send_message(get_number_reverse(str(num)))
    except:
        await inter.response.send_message(get_number(n2))


@fwew_bot.slash_command(name="lenition", description="get the lenition table")
async def lenition(inter):
    """
    get the lenition table
    """
    await inter.response.send_message(get_lenition())


@fwew_bot.slash_command(name="len", description="get the compact lenition table")
async def len(inter):
    """
    get the compact lenition table
    """
    await inter.response.send_message(get_len())


@fwew_bot.slash_command(name="that", description="show all possible \"that\"s in Na'vi")
async def that(inter):
    """
    get the possible translations of "that" into Na'vi
    """
    await inter.response.send_message(get_all_thats())


@fwew_bot.slash_command(name="cameron-words", description="Words that James Cameron made")
async def cameron_words(inter):
    """
    get the Na'vi words James Cameron made
    """
    await inter.response.send_message(get_cameron_words())


@fwew_bot.slash_command(name="version", description="get version information")
async def version(inter):
    """
    get version information
    """
    await inter.response.send_message(get_version())


@fwew_bot.slash_command(name="name-single", description="Generate a valid Na'vi word to use as a name")
async def name_single(inter,
                      n=Param(name="name-count",
                              description="number of names to generate",
                              gt=1,
                              le=50,
                              default=1),
                      dialect=Param(name="dialect",
                                    description="which dialect the names should fit",
                                    choices=["interdialect", "forest", "reef"],
                                    default="interdialect"),
                      s=Param(name="syllables",
                              description="name syllable count",
                              gt=0,
                              le=4,
                              default=0)):
    """
    generate one-word Na'vi name(s)

    Parameters
    ----------
    syllables: name number of syllables
    dialect: dialect the names would fit into (interdialect, forest, reef)
    name-count: number of names to generate
    """
    await inter.response.send_message(get_single_name_discord(n, dialect, s))


@fwew_bot.slash_command(name="name", description="generate Na'vi full names")
async def name(inter,
               ending=commands.Param(
                   description="'ite (daughter), 'itan (son) or 'itu (genderless, non-canon)",
                   choices=["random", "'ite", "'itan", "'itu"],
                   default="random"),
               n=Param(name="name-count",
                       description="number of names to generate",
                       gt=1,
                       le=50,
                       default=1),
               dialect=Param(name="dialect",
                             description="which dialect the names should fit",
                             choices=["interdialect", "forest", "reef"],
                             default="interdialect"),
               s1=Param(name="syllables-1",
                        description="first name syllable count",
                        gt=0,
                        le=4,
                        default=0),
               s2=Param(name="syllables-2",
                        description="family name syllable count",
                        gt=0,
                        le=4,
                        default=0),
               s3=Param(name="syllables-3",
                        description="parent's name syllable count",
                        gt=0,
                        le=4,
                        default=0)):
    """
    generate full Na'vi name(s)

    Parameters
    ----------
    syllables-1: first name number of syllables
    syllables-2: family name number of syllables
    syllables-3: parent's name number of syllables
    dialect: dialect the names would fit into (interdialect, forest, reef)
    ending: 'ite (daughter), 'itan (son) or 'itu (genderless, non-canon)
    name-count: number of names to generate
    """
    await inter.response.send_message(get_name(ending, n, dialect, s1, s2, s3))


@fwew_bot.slash_command(name="name-alu", description="Use existing Na'vi words to generate Na'vi names")
async def name_alu(inter,
                   n=Param(name="name-count",
                           description="number of names to generate",
                           gt=1,
                           le=50,
                           default=1),
                   dialect=Param(name="dialect",
                                 description="which dialect the names should fit",
                                 choices=["interdialect", "forest", "reef"],
                                 default="interdialect"),
                   s=Param(name="syllables",
                           description="name syllable count",
                           gt=0,
                           le=4,
                           default=0),
                   noun_mode=commands.Param(name="noun-mode",
                                            description="type of noun",
                                            choices=["something",
                                                     "normal noun", "verb-er"],
                                            default="something"),
                   adj_mode=commands.Param(name="adjective-mode",
                                           description="type of adjective for the noun",
                                           choices=["any", "something", "none", "normal adjective", "genitive noun", "origin noun",
                                                    "participle verb", "active participle verb", "passive participle verb"],
                                           default="something")):
    """
    generate full Na'vi name(s) out of preexisting Na'vi words

    Parameters
    ----------
    adj-mode: What to put next to the noun
    noun-mode: What kind of noun should go next toafter "alu"
    dialect: The Na'vi dialect the names should fit
    syllables: name number of syllables
    dialect: dialect the names would fit into (interdialect, forest, reef)
    name-count: number of names to generate
    """
    await inter.response.send_message(get_name_alu(n, dialect, s, noun_mode, adj_mode))


@fwew_bot.slash_command(name="phoneme-frequency", description="show how often a phoneme appears")
async def phoneme_frequency(inter,
                            lang=Param(description="Language for results",
                                       default=None,
                                       choices=languages),):
    """
    Show how likely each phoneme or consonent cluster is to start, end, or center a syllable
    """
    if lang is None:
        lang = get_language(inter)
    await inter.response.send_message(get_phonemes(lang))


@fwew_bot.slash_command(name="servers", description="list all servers the bot is in")
async def servers(inter):
    """
    list all servers the bot is in
    """
    if inter.user.id == developer:
        count = 0
        embed = Embed(
            title="Servers",
            description="",
            color=0x7494BA,
            timestamp=datetime.now(),
        )

        for guild in fwew_bot.guilds:
            count += 1
            embed.description += f"[{count}] {guild.name} ({guild.id}) by ({guild.owner_id}) - {guild.member_count} members\n"

        embed.description = f"currently in {count} servers:\n\n{embed.description}"

        await inter.response.send_message(embed=embed)
    else:
        await inter.response.defer(ephemeral=True)
        await inter.edit_original_message(content="you are not authorized to use this command")


@fwew_bot.slash_command(name="leave", description="leave the given server")
async def leave(inter, server_id=Param(description="the server id")):
    """
    leave the given server

    Parameters
    ----------
    server_id: the server id
    """
    if inter.user.id == developer:
        await inter.response.defer(ephemeral=True)
        guild = fwew_bot.get_guild(int(server_id))
        await guild.leave()
        await inter.edit_original_message(content=f"left {guild.name} ({guild.id})")
    else:
        await inter.response.defer(ephemeral=True)
        await inter.edit_original_message(content="you are not authorized to use this command")


@fwew_bot.message_command(name="fwew translate")  # default_permission=True)
async def fwew_translate(inter, message):
    """
    translate this message using Fwew
    """
    await inter.response.defer(ephemeral=True)
    await inter.edit_original_message(content=get_translation(message.content, "en"))


@fwew_bot.slash_command(name="valid", description="see if a possible Na'vi word is valid")
async def list(inter,
               word=Param(
                   description="Word to check for phonotactic validity in Na'vi"),
               lang=Param(description="Language for results",
                          default=None,
                          choices=languages)):
    """
    Take a word and determine whether or not it's phonotactically valid in Na'vi
    """
    if lang is None:
        lang = get_language(inter)
    await inter.response.send_message(get_validity(word, lang))


@fwew_bot.slash_command(name="oddballs", description="see which words bend or break Na'vi phonotactics")
async def list(inter,
               ipa=Param(description="set to true to show IPA",
                         default=False, choices=["true", "false"]),
               lang=Param(description="Language for results",
                          default=None, choices=languages),
               reef=Param(description="Show reef dialect stuff",
                          default=False, choices=["true", "false"])):
    """
    Take a word and determine whether or not it's phonotactically valid in Na'vi
    """
    if lang is None:
        lang = get_language(inter)
    await Paginator.Simple().start(inter, pages=get_oddballs(ipa, lang, reef))


if __name__ == "__main__":
    fwew_bot.run(token)
