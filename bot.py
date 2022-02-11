#!/usr/bin/env python3
import os
from datetime import datetime

import disnake
from disnake.ext import commands
from disnake.ext.commands import Param
from disnake.utils import get
from dotenv import load_dotenv

from lib import *

dotenv_dir = "token_container/"
load_dotenv(os.path.join(dotenv_dir, ".env"))
token = os.environ.get("token")

logfile = "log.txt"

sndb0x = 935489523155075092
fbts = 395558141162422275
lnc = 154318499722952704
gfs = 860933619296108564
test_env = [sndb0x, fbts, lnc, gfs]

intents = disnake.Intents.default()
fwew_bot = commands.Bot(command_prefix="?", help_command=None, sync_permissions=True,
                        intents=intents, sync_commands_debug=True)  # , test_guilds=test_env)


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


@fwew_bot.slash_command(name="fwew", description="search word(s) na'vi -> english")
async def fwew(inter, words=Param(description="the na'vi word(s) to look up"), lang="en"):
    """
    search word(s) na'vi -> english

    Parameters
    ----------
    words: the na'vi word(s) to look up
    lang: the two-letter language-code for results (default: en)
    """
    await inter.response.send_message(get_fwew(lang, words))


@fwew_bot.slash_command(name="search", description="search word(s) english -> na'vi")
async def search(inter, words=Param(description="the english word(s) to look up"), lang="en"):
    """
    search words english -> na'vi

    Parameters
    ----------
    words: the english word(s) to look up
    lang: the two-letter language-code for results (default: en)
    """
    await inter.response.send_message(get_fwew_reverse(lang, words))


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


@fwew_bot.slash_command(name="list", description="list all words with certain characteristics")
async def list(inter, where=Param(description="characteristics of the word, such as part of speech, number of syllables, etc."), lang="en"):
    """
    list all words with certain characteristics

    Parameters
    ----------
    where: characteristics of the word, such as part of speech, number of syllables, etc.
    lang: the two-letter language-code for results (default: en)
    """
    await inter.response.send_message(get_list(lang, where))


@fwew_bot.slash_command(name="random", description="get given number of random entries with certain characteristics")
async def random(inter, n=Param(description="the number of random words to get"), where="", lang="en"):
    """
    get given number of random entries with certain characteristics

    Parameters
    ----------
    n: the number of random words to get
    where: characteristics of the word, such as part of speech, number of syllables, etc.
    lang: the two-letter language-code for results (default: en)
    """
    if len(where) == 0:
        await inter.response.send_message(get_random(lang, n))
    else:
        await inter.response.send_message(get_random_filter(lang, n, where))


@fwew_bot.slash_command(name="number", description="convert or translate numbers between decimal and octal/na'vi")
async def number(inter, n=Param(description="the number to convert or translate")):
    """
    convert or translate numbers between decimal and octal/na'vi

    Parameters
    ----------
    n: the number to convert or translate
    """
    base = 10
    if n.startswith("0x"):
        base = 16
    elif n.startswith("0b"):
        base = 2
    elif n.startswith("0"):
        base = 8
    try:
        num = int(n, base)
        await inter.response.send_message(get_number_reverse(str(num)))
    except:
        await inter.response.send_message(get_number(n))


@fwew_bot.slash_command(name="lenition", description="get the lenition table")
async def lenition(inter):
    """
    get the lenition table
    """
    await inter.response.send_message(get_lenition())


@fwew_bot.slash_command(name="version", description="get version information")
async def version(inter):
    """
    get version information
    """
    await inter.response.send_message(get_version())


@fwew_bot.slash_command(name="name", description="generate Na'vi full names")
async def name(inter,
    s1=Param(name="first_name_num_syllables", description="first name number of syllables", gt=1, le=4),
    s2=Param(name="family_name_num_syllables", description="family name number of syllables", gt=1, le=4),
    s3=Param(name="parent_name_num_syllables", description="parent's name number of syllables", gt=1, le=4),
    ending=commands.Param(description="'ite (daughter) or 'itan (son)", choices=["'ite", "'itan"]),
    n=Param(description="number of names to generate", gt=0, le=50, default=1)):
    """
    generate full Na'vi name(s)

    Parameters
    ----------
    first_name_num_syllables: first name number of syllables
    family_name_num_syllables: family name number of syllables
    parent_name_num_syllables: parent's name number of syllables
    ending: 'ite (daughter) or 'itan (son)
    n: number of names to generate
    """
    await inter.response.send_message(get_name(s1, s2, s3, ending, n))


@fwew_bot.message_command(name="fwew translate", default_permission=True, guild_ids=test_env)
async def translate_message(inter, message):
    """
    translate this message using Fwew
    """
    await inter.response.defer(ephemeral=True)
    await inter.edit_original_message(content=get_translation(message.content, "en"))


if __name__ == "__main__":
    fwew_bot.run(token)
