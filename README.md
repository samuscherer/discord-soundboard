# Discord Soundboard

[![Python](https://img.shields.io/badge/python-3.5%2C%203.6-blue.svg?style=flat-square)](https://www.python.org/downloads/)

This bot was created to play sounds in a voice channel of a Discord server. It's written in [Python](https://www.python.org "Python homepage") 3.5+, using the [discord.py](https://github.com/Rapptz/discord.py) library.

## Setup

To set up the bot you need to:
* create a bot account (You can find a guide [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token))
* install the discord.py library (rewrite branch needed: `pip3 install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]`)
* install ffmpeg (e.g. on Debian: `[sudo] apt install ffmpeg`; make sure to check that it's in the PATH: `which ffmpeg`)
* install flask (`pip install flask`)
* modify the config file. Insert all your desired configuration and rename the file to bot.json.
* create a folder named `sounds` and move all your sound files into this folder. You can also add sounds by sending them to the bot via DM.

That's pretty much it! If you run into any problems don't hesitate to create an issue.

## Usage
You can either use the bot by sending a command as a DM or by opening the webinterface which is hosted on `0.0.0.0:8080` by default. Use the `help` command to show all available commands.

There is a permission system implemented. The owner (don't forget to set the owner ID) can add admins who are allowed to add people to the whitelist. You need to use the `init` command in one of your server's text channels (can be a private one too) first.  Every whitelisted person can add sounds via DM. 

## Other

I'm a student at the University of Heidelberg in Germany - I created this project to have fun and improve my Python skills. Feel free to modify the bot, I will check your pull request asap!

