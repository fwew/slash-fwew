# slash-fwew

Fwew Na'vi Dictionary for Discord, "slash commands" edition.

Requires Python3.10.x

## install & launch (GNU/Linux or macOS)

```shell
# create .env file
cp .example.env .env

# EDIT the .env file

# install dependencies and virtual environment
./install.sh

# actiavte virtual environment
source venv/bin/activate

# run the bot
./bot.py
```

## install & launch (Windows)

using Windows CMD, run:

```cmd
REM create .env file
copy .example.env .env

REM EDIT the .env file

REM install dependencies and virtual environment
install.bat

REM activate virtual environment
venv\Scripts\activate

REM run the bot
python bot.py
```

OR, with Windows PowerShell, run:
```powershell
# create .env file
Copy-Item .example.env .env

# EDIT the .env file

# install dependencies and virtual environment
.\install.bat

# activate virtual environment
venv\Scripts\Activate.ps1

# run the bot
python bot.py
```