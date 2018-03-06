#!/usr/bin/env python3

import discord
import os
import sys
import json
import asyncio
import logging
import websrv
from discord.ext import commands
from _thread import start_new_thread

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

def load_opus_lib(opus_libs=OPUS_LIBS):
	if discord.opus.is_loaded():
		return True
	for opus_lib in opus_libs:
		try:
			discord.opus.load_opus(opus_lib)
			return
		except OSError:
			pass
	raise RuntimeError('Could not load an opus lib.')

with open('bot.json') as data:
	conf = json.load(data)

client = commands.Bot(command_prefix=conf['invoker'])
client.remove_command('help')

@client.event
async def on_ready():
	logger.info("bot started")
	await client.change_presence(game=discord.Game(name='sounds'))
	load_opus_lib()

oldchannel = 0
voice = None
player = None
volume = conf['volume']

@client.command(pass_context=True)
async def test(ctx):
	print("command test")
	if type(ctx.message.channel) is discord.DMChannel:
		print("sending reply")
		await ctx.message.author.dm_channel.send("hello")

@client.command()
async def help(ctx):
	if not ctx.guild:
		helpmessage = ctx.message.author.mention + "You can use the following commands with this bot:\n\n"
		helpmessage += "**"+conf['invoker']+"help:** Shows this help text.\n\n"
		helpmessage += "**"+conf['invoker']+"list:** Lists all available sounds.\n\n"
		await ctx.message.author.dm_channel.send(helpmessage)


@client.command()
async def list(ctx):
	if type(ctx.message.channel) is discord.DMChannel:
		try:
			f = []
			dirs = os.listdir("sounds/")
			for file in dirs:
				f.append(conf['invoker'] + file[:file.rfind('.')])
			f.sort()
			fs = "\n".join(f)
			embed = discord.Embed(title="Use one of the following commands to play a sound:", description=fs, color=0xcc2f00)
			await ctx.message.author.dm_channel.send(content=None, tts=False, embed=embed)
		except Exception as e:
			logger.debug(str(e))

@client.command()
async def stop(ctx):
	global voice
	if type(ctx.message.channel) is discord.DMChannel:
		if voice != None:
			voice.stop()

@client.command(name="volume")
async def set_volume(ctx):
	global volume
	if type(ctx.message.channel) is discord.DMChannel:
		try:
			v = int(ctx.message.content[ctx.message.content.find(' ')+1:])
			if v < 1:
				volume = 0.01
			elif v > 100:
				volume = 1.0
			else:
				volume = float(v/100)
			await ctx.message.author.dm_channel.send(content="Changed the volume to " + str(volume*100))
		except Exception as e:
			await ctx.message.author.dm_channel.send(content="There was an error setting the volume.")
			logger.debug(str(e))

def getListOfAliases():
	f = []
	dirs = os.listdir("sounds/")
	for file in dirs:
		f.append(file[:file.rfind('.')])
	return f

@client.command(aliases=getListOfAliases())
async def play_sound(ctx):
	global oldchannel
	global voice
	global volume
	logger.info("message received")
	if not ctx.message.author.bot and ctx.message.content.startswith(conf['invoker']) and type(ctx.message.channel) is discord.DMChannel:
		guild = None
		for guilds in client.guilds:
			guild = guilds
			vchannel = guild.get_member(ctx.message.author.id).voice.channel
		if vchannel:
			try:
				if voice != None:
					voice.stop()
				if oldchannel != vchannel:
					if voice != None:
						await voice.disconnect()
					voice = await vchannel.connect()
					oldchannel = vchannel
				for format in conf['fileformats']:
					if os.path.exists("sounds/" + ctx.message.content.lower()[len(conf['invoker']):] + format):
						sourceToPlay = discord.FFmpegPCMAudio('sounds/' + ctx.message.content.lower()[len(conf['invoker']):] + format)
						sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
						sourceToPlay.volume = volume
						voice.play(sourceToPlay)
						break
			except Exception as e:
				logger.debug("error while playing sound" + str(e))
		else:
			await ctx.message.author.dm_channel.send("You're not in a voice channel")

@client.event
async def on_voice_state_update(member,before,after):
	global voice
	global oldchannel
	user = member
	newUserChannel = after.channel
	oldUserChannel = before.channel

	if not user.bot and newUserChannel != None and newUserChannel != oldUserChannel:
		vchannel = newUserChannel

		if vchannel:
			try:
				if voice != None:
					voice.stop()

				if oldchannel != vchannel:
					if voice != None:
						await voice.disconnect()
					logger.debug("joining voice channel")
					voice = await newUserChannel.connect()
					oldchannel=vchannel
				for format in conf['fileformats']:
					if os.path.exists("sounds/" + user.name.lower() + format):
						sourceToPlay = discord.FFmpegPCMAudio('sounds/' + user.name.lower() + format)
						sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
						sourceToPlay.volume = volume
						voice.play(sourceToPlay)
						break
			except Exception as e:
				logger.debug("error in playing join sound" + str(e))

	elif newUserChannel == None:
		pass

def srv_sound(sound):
	global voice
	logger.info("message received")
	if voice != None:
		voice.stop()
		if voice.is_connected():
			for format in conf['fileformats']:
				if os.path.exists("sounds/" + sound + format):
					sourceToPlay = discord.FFmpegPCMAudio('sounds/' + sound + format)
					sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
					sourceToPlay.volume = volume
					voice.play(sourceToPlay)

def srv_volume(vol):
	global volume
	try:
		v = int(vol)
		if v < 1:
			volume = 0.01
		elif v > 100:
			volume = 1.0
		else:
			volume = float(v/100)
		print("set volume to" + str(volume))

	except Exception as e:
		logger.debug(str(e))

websrv.play_sound=srv_sound
websrv.set_volume=srv_volume
start_new_thread(websrv.app.run, (conf['host'], conf['port']))
client.run(conf['token'])
