#!/usr/bin/env python3

import discord
import os
import sys
import json
import asyncio
import logging
import websrv
import shutil
from controller import Controller
from discord.ext import commands
from _thread import start_new_thread
from tabulate import tabulate

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

Controller.import_sounds_from_fs(Controller.config_file["sound_folder"])
Controller.cat_list_generator()

Controller.export_sounds(Controller.config_file["savefile_folder"])
Controller.import_sounds(Controller.config_file["savefile_folder"])


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

conf = None

def loadConfig():
	global conf
	with open('bot.json') as data:
		conf = json.load(data)

loadConfig()
currentVoiceChannel = 0
voice = None
player = None
volume = conf['volume']
commandChannel = conf['commandChannel']
whiteList = conf['whitelist']
admins = conf['admins']
commandNames = None

def saveConfig():
	global conf
	global volume
	global commandChannel
	global whiteList
	global admins
	conf['volume'] = volume
	conf['commandChannel'] = commandChannel
	conf['whitelist'] = whiteList
	conf['admins'] = admins
	with open('bot.json', 'w') as data:
		json.dump(conf, data)
	loadConfig()

client = commands.Bot(command_prefix=conf['invoker'])
client.remove_command('help')

def getAllCommandNames():
	global commandNames
	names = []
	for command in client.commands:
		names.append(command.name)
	commandNames = names

@client.event
async def on_ready():
	logger.info("bot started")
	await client.change_presence(activity=discord.Game(name='sounds'))
	load_opus_lib()
	getAllCommandNames()

@client.event
async def on_command_error(ctx, exception):
	await ctx.message.channel.send("This command or sound does not exist.")

@client.command()
async def help(ctx):
	if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
		channel = ctx.message.channel
		helpmessage = ctx.message.author.mention + " **You can use the following commands with this bot:**\n\n"
		if ctx.message.author.id == conf['ownerID']:
			helpmessage += "**"+conf['invoker']+"help:** Shows this help text.\n\n"
			helpmessage += "**"+conf['invoker']+"list:** Lists all available sounds.\n\n"
			helpmessage += "**"+conf['invoker']+"stop:** Stops the current sound.\n\n"
			helpmessage += "**"+conf['invoker']+"volume [1-100]:** Sets a new volume.\n\n"
			helpmessage += "**"+conf['invoker']+"whitelist [member1] [member2] [...]:** Add one or multiple members to the whitelist. Use an @-mention for each member.\n\n"
			helpmessage += "**"+conf['invoker']+"addadmin [member1] [member2] [...]:** Add one or mulitple members as admins. Use an @-mention for each member.\n\n"
			helpmessage += "**"+conf['invoker']+"removewhitelist [member1] [member2] [...]:** Remove one or multiple members to the whitelist. Use an @-mention for each member.\n\n"
			helpmessage += "**"+conf['invoker']+"removeadmin [member1] [member2] [...]:** Remove one or multiple members as admins. Use an @-mention for each member. Only the owner can use this command.\n\n"
			helpmessage += "**"+conf['invoker']+"setcmdchn:** Initialize a channel as command channel. This is needed to be able to use the whitelist/addadmin commands.\n\n"
			helpmessage += "**"+conf['invoker']+"remove [sound]:** Remove a sound by its name. Only the owner/an admin can use this command. The sound is not really deleted, just moved to a directory called \"deleted_sounds\".\n\n"
			helpmessage += "**"+conf['invoker']+"clearremovedsounds:** Remove all sounds from the \"deleted_sounds\" directory. This can notbe reversed therefore is this command only available to the owner.\n\n"
			helpmessage += "**"+conf['invoker']+"restore [sound]:** Restore a sound from the \"deleted_sounds\" directory.\n\n"
			helpmessage += "**"+conf['invoker']+"listdeleted:** Lists all removed sounds.\n\n"
		elif ctx.message.author.id in conf['admins']:
			helpmessage += "**"+conf['invoker']+"help:** Shows this help text.\n\n"
			helpmessage += "**"+conf['invoker']+"list:** Lists all available sounds.\n\n"
			helpmessage += "**"+conf['invoker']+"stop:** Stops the current sound.\n\n"
			helpmessage += "**"+conf['invoker']+"volume [1-100]:** Sets a new volume.\n\n"
			helpmessage += "**"+conf['invoker']+"whitelist [member1] [member2] [...]:** Add one or multiple members to the whitelist. Use an @-mention for each member.\n\n"
			helpmessage += "**"+conf['invoker']+"addadmin [member1] [member2] [...]:** Add one or mulitple members as admins. Use an @-mention for each member.\n\n"
			helpmessage += "**"+conf['invoker']+"removewhitelist [member1] [member2] [...]:** Remove one or multiple members to the whitelist. Use an @-mention for each member.\n\n"
			helpmessage += "**"+conf['invoker']+"remove [sound]:** Remove a sound by its name. Only the owner/an admin can use this command. The sound is not really deleted, just moved to a directory called \"deleted_sounds\".\n\n"
			helpmessage += "**"+conf['invoker']+"restore [sound]:** Restore a sound from the \"deleted_sounds\" directory.\n\n"
			helpmessage += "**"+conf['invoker']+"listdeleted:** Lists all removed sounds.\n\n"
		else:
			helpmessage += "**"+conf['invoker']+"help:** Shows this help text.\n\n"
			helpmessage += "**"+conf['invoker']+"list:** Lists all available sounds.\n\n"
			helpmessage += "**"+conf['invoker']+"stop:** Stops the current sound.\n\n"
			helpmessage += "**"+conf['invoker']+"volume [1-100]:** Sets a new volume.\n\n"
		embed = discord.Embed(title=None, description=helpmessage, color=0x56a80f)
		await channel.send(content=None, tts=False, embed=embed)

@client.command()
async def removewhitelist(ctx):
	global whiteList
	if ctx.message.channel.id == commandChannel:
		if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
			try:
				removedUsers = []
				notRemovedUsers = []
				for user in ctx.message.mentions:
					if user.id in whiteList:
						whiteList.remove(user.id)
						removedUsers.append(user.mention)
					else:
						notRemovedUsers.append(user.mention)
				successMessage = ""
				if len(removedUsers) > 0:
					successMessage += "Removed " + ", ".join(removedUsers) + " from the whitelist."
				if len(notRemovedUsers) > 0:
					successMessage += ", ".join(notRemovedUsers) + " weren't on the whitelist in the first place :smile:"
				saveConfig()
				await ctx.message.channel.send(successMessage)
			except Exception as e:
				logger.debug(str(e))
				await ctx.message.channel.send("Something went wrong.")
		else:
			await ctx.message.channel.send("Only the owner/an admin can edit the whitelist.")

@client.command()
async def removeadmin(ctx):
	global admins
	if ctx.message.channel.id == commandChannel:
		if ctx.message.author.id == conf['ownerID']:
			try:
				removedUsers = []
				notRemovedUsers = []
				for user in ctx.message.mentions:
					if user.id in admins:
						admins.remove(user.id)
						removedUsers.append(user.mention)
					else:
						notRemovedUsers.append(user.mention)
				successMessage = ""
				if len(removedUsers) > 0:
					successMessage += "Removed " + ", ".join(removedUsers) + " as admin."
				if len(notRemovedUsers) > 0:
					successMessage += ", ".join(notRemovedUsers) + " weren't admin in the first place :smile:"
				saveConfig()
				await ctx.message.channel.send(successMessage)
			except Exception as e:
				logger.debug(str(e))
				await ctx.message.channel.send("Something went wrong.")
		else:
			await ctx.message.channel.send("Only the owner can remove an admin.")

@client.command()
async def whitelist(ctx):
	global whiteList
	if ctx.message.channel.id == commandChannel:
		if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
			try:
				addedUsers = []
				notAddedUsers = []
				for user in ctx.message.mentions:
					if not user.id in whiteList:
						whiteList.append(user.id)
						addedUsers.append(user.mention)
					else:
						notAddedUsers.append(user.mention)
				successMessage = ""
				if len(addedUsers) > 0:
					successMessage += "Added " + ", ".join(addedUsers) + " to the whitelist."
				if len(notAddedUsers) > 0:
					successMessage += "Did not add " + ", ".join(notAddedUsers) + " for a second time."
				saveConfig()
				await ctx.message.channel.send(successMessage)
			except Exception as e:
				logger.debug(str(e))
				await ctx.message.channel.send("Something went wrong.")
		else:
			await ctx.message.channel.send("Only the owner/an admin is allowed to add people to the whitelist!")

@client.command()
async def addadmin(ctx):
	global admins
	if ctx.message.channel.id == commandChannel:
		if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
			try:
				addedUsers = []
				notAddedUsers = []
				for user in ctx.message.mentions:
					if not user.id in admins:
						admins.append(user.id)
						addedUsers.append(user.mention)
					else:
						notAddedUsers.append(user.mention)
				successMessage = ""
				if len(addedUsers) > 0:
					successMessage = "Added " + ", ".join(addedUsers) + " as admin."
				if len(notAddedUsers) > 0:
					successMessage += "Did not add " + ", ".join(notAddedUsers) + " for a second time."
				saveConfig()
				await ctx.message.channel.send(successMessage)
			except Exception as e:
				logger.debug(str(e))
				await ctx.message.channel.send("Something went wrong.")
		else:
			await ctx.message.channel.send("Only the owner/an admin can add another admin.")

@client.command()
async def setcmdchn(ctx):
	global commandChannel
	if not ctx.message.channel is discord.DMChannel and not ctx.message.channel is discord.GroupChannel:
		if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
			channel = ctx.message.channel
			try:
				commandChannel = ctx.message.channel.id
				saveConfig()
				await channel.send("Initialized this channel as command channel.")
			except Exception as e:
				logger.debug(str(e))
				await channel.send("Something went wrong. Please try again.")
		else:
			await ctx.message.channel.send("Only the owner/an admin can bind the bot to a text channel.")

# @client.command(name="remove")
# async def remove_sound(ctx):							# Ändern sunst bumst di söwa in Oasch --> ( . Y . )
# 	global commandChannel
# 	channel = ctx.message.channel
# 	toremove = ctx.message.content[len(conf['invoker'] + "remove "):]
# 	print(toremove)
# 	if type(channel) is discord.DMChannel or channel.id == commandChannel:
# 		if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
# 			try:
# 				print("bist vorm IF")
# 				if not os.path.isdir("deleted_sounds"):
# 					print("Delted sounds gibts nu ned.\n")
# 					os.makedirs("deleted_sounds/")
# 					print("deleted_sounds erstellt\n")
# 				if not os.path.isdir("deleted_sounds/" + getcat(toremove) + "/"):
# 					print(f"{getcat(toremove)} gibts nu ned.\n")
# 					os.makedirs("deleted_sounds/" + getcat(toremove) + "/")
# 					print(f"{getcat(toremove)} erstöd\n")
# 				removedOne = False
# 				for format in conf['fileformats']:
# 					if os.path.exists(getcatpath(toremove) + toremove + format):
# 						print("he des file wos du removen wüst existiert wiakle und wird hoffentlich removed!")
# 						removedOne = True
# 						source = getcatpath(getcat(toremove)) + toremove + format
# 						destination = "deleted_sounds/" + getcat(toremove) + "/" + toremove + format
# 						print(source)
# 						print("\n")
# 						print(destination)
# 						os.rename(getcatpath(getcat(toremove)) + toremove + format, "deleted_sounds/" + getcat(toremove) + "/" + toremove + format)
# 						await channel.send("Removed sound successfully.")
# 						break
# 				if not removedOne:
# 					await channel.send("This sound doesn't exist. What are you trying to do? :smile:")
# 
# 			except Exception as e:
# 				logger.debug(str(e))
# 				print (e)
# 				await channel.send("Something went wrong.\n")
# 		else:
# 			await channel.send("Only the owner/an admin can remove a sound.")

# @client.command(name="restore")
# async def restore_sound(ctx):									# Ändern sunst bumst di söwa in Oasch --> ( . Y . )
# 	global commandChannel
# 	channel = ctx.message.channel
# 	if type(channel) is discord.DMChannel or channel.id == commandChannel:
# 		if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
# 			try:
# 				restoredOne = False
# 				for format in conf['fileformats']:
# 					if os.path.exists("deleted_sounds/" + ctx.message.content[len(conf['invoker'] + "restore "):] + format):
# 						restoredOne = True
# 						os.rename("deleted_sounds/" + ctx.message.content[len(conf['invoker'] + "restore "):] + format, kakadu.getSoundDir() + ctx.message.content[len(conf['invoker'] + "restore "):] + format)
# 						await channel.send("Restored sound successfully.")
# 						break
# 				if not restoredOne:
# 					await channel.send("This sound doesn't exist. What are you trying to do? :smile:")
# 			except Exception as e:
# 				logger.debug(str(e))
# 				await channel.send("Something went wrong.\n")
# 		else:
# 			await channel.send("Only the owner/an admin can restore a sound.")

# @client.command(name="clearremovedsounds")								# Ändern sunst bumst di söwa in Oasch --> ( . Y . )
# async def clear_sounds(ctx):
# 	global commandChannel
# 	channel = ctx.message.channel
# 	if type(channel) is discord.DMChannel or channel.id == commandChannel:
# 		if ctx.message.author.id == conf['ownerID']:
# 			try:
# 				shutil.rmtree("deleted_sounds")
# 				await channel.send("Removed all sounds in the \"deleted_sounds\" directory.")
# 			except Exception as e:
# 				logger.debug(str(e))
# 				await channel.send("Something went wrong. Please try again.")
# 		else:
# 			await channel.send("This command can only be used by the owner!")

@client.command()
async def categories(ctx):
	if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
		channel = ctx.message.channel
		if ctx.message.author.dm_channel == None:
			try:
				await ctx.message.author.create_dm()
			except Exception as e:
				logger.debug(str(e))
		try:
			embed = discord.Embed(title="Available categories:", description="\n".join(Controller.category_list), color=0xcc2f00)
			await channel.send(content=None, tts=False, embed=embed)
		except Exception as e:
			logger.debug(str(e))

@client.command()
async def list(ctx):
	if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
		channel = ctx.message.channel
		if ctx.message.author.dm_channel == None:
			try:
				await ctx.message.author.create_dm()
			except Exception as e:
				logger.debug(str(e))
		try:
			song_name_list = Controller.song_list_generator(ctx.message.content,invoker=True,as_object=False)		
			# sliced_song_name_list=[]			#needs to be changed!! do not delete! 
			# counter=0
			# while True:
			# 	counter+=1
			# 	if len(song_name_list)==0:
			# 		break
			# 	if counter%3==False:
			# 		list_storage=[]
			# 		list_storage.append(song_name_list[:counter])
			# 		song_name_list=song_name_list[counter:]
			# 		for element in list_storage:
			# 			sliced_song_name_list.append(element)
			# 		counter=1
			# print(sliced_song_name_list)
			# char_counter=0
			# start=0
			# for list_index,liste in enumerate(sliced_song_name_list):
			# 	char_counter+=len(tabulate(liste,tablefmt="orgtbl"))
			# #     print(len(tabulate(liste,tablefmt="orgtbl")))
			# 	if char_counter>=2048:
			# 		char_counter=len(tabulate(liste,tablefmt="orgtbl"))
			# 		
			# 		# print("maximum reached")
			# 		description=tabulate(sliced_song_name_list[start:list_index],tablefmt="orgtbl")
			# 		embed = discord.Embed(title=f"Available Sounds", description=description, color=0xcc2f00)
			# 		await channel.send(content=None, tts=False, embed=embed)
			# 		start=list_index
			# 	elif list_index+1==len(sliced_song_name_list):
			# 		description=tabulate(sliced_song_name_list[start:],tablefmt="orgtbl")
			# 		embed = discord.Embed(title=f"Available Sounds", description=description, color=0xcc2f00)
			# 		# print("end reached")
			# 		# print(tabulate(sliced_song_name_list[start:],tablefmt="orgtbl"))

			if len(song_name_list):
				char_counter=0
				list_element_counter=0
				page_counter=1
				print("I am here!")
				for song in song_name_list:
					char_counter+=len(song)
					print(song, char_counter,song_name_list.index(song))
					if char_counter>=2048-len(song)-song_name_list.index(song)+list_element_counter:
						embed = discord.Embed(title=f"Available Sounds", description="\n".join(song_name_list[list_element_counter:song_name_list.index(song)]), color=0xcc2f00)
						print("in the if-loop!")
						char_counter=0
						page_counter+=1
						list_element_counter=song_name_list.index(song)
						await channel.send(content=None, tts=False, embed=embed)
					elif song==song_name_list[-1]:
						embed = discord.Embed(title=f"Available Sounds", description="\n".join(song_name_list[list_element_counter:]), color=0xcc2f00)
						await channel.send(content=None, tts=False, embed=embed)
						break
			else:
				await channel.send("This category does not exist - use '!listcat' command!")
		except Exception as e:
			logger.debug(str(e))

@client.command(name="listdeleted")
async def list_deleted_sounds(ctx):
	global commandChannel
	channel = ctx.message.channel
	if type(channel) is discord.DMChannel or channel.id == commandChannel:
		if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
			if ctx.message.author.dm_channel == None:
				try:
					await ctx.message.author.create_dm()
				except Exception as e:
					logger.debug(str(e))

			if not os.path.isdir("deleted_sounds"):
				os.makedirs("deleted_sounds")

			try:
				f = []
				dirs = os.listdir("deleted_sounds/")
				for file in dirs:
					f.append(file[:file.rfind('.')])
				f.sort()
				fs = "\n".join(f)
				if fs == "":
					title = "There are no sounds to be restored."
				else:
					title = "Following sounds can be restored:"
				embed = discord.Embed(title=title, description=fs, color=0xcc2f00)
				await channel.send(content=None, tts=False, embed=embed)
			except Exception as e:
				logger.debug(str(e))

@client.command()
async def stop(ctx):
	global voice
	if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
		if voice != None:
			voice.stop()

@client.command(name="volume")
async def set_volume(ctx):
	global volume
	if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
		channel = ctx.message.channel
		try:
			v = float(ctx.message.content[ctx.message.content.find(' ')+1:])
			v = int(v)
			if v < 1:
				volume = 0.01
			elif v > 100:
				volume = 1.0
			else:
				volume = float(v/100)
			saveConfig()
			await channel.send(content="Changed the volume to " + str(int(volume*100)))
		except Exception as e:
			await channel.send(content="There was an error setting the volume.")
			logger.debug(str(e))

@client.command(aliases=Controller.song_list_generator("!list",invoker=True,as_object=False))
async def play_sound(ctx):
	global currentVoiceChannel
	global voice
	global volume
	logger.info("play sound received")
	if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
		channel = ctx.message.channel
		guild = None
		song_path = Controller.path_generator(ctx.message.content)
		for guilds in client.guilds:
			guild = guilds
			vchannel = guild.get_member(ctx.message.author.id).voice.channel
		perm = None
		if vchannel != None:
			perm = vchannel.permissions_for(vchannel.guild.me).connect
		else:
			perm = False

		if vchannel and perm:
			try:
				if voice != None:
					voice.stop()
				if currentVoiceChannel != vchannel:
					if voice != None:
						await voice.disconnect()
					voice = await vchannel.connect()
					currentVoiceChannel = vchannel
				if os.path.exists(song_path):
					sourceToPlay = discord.FFmpegPCMAudio(song_path)
					sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
					sourceToPlay.volume = volume
					voice.play(sourceToPlay)
			except Exception as e:
				logger.debug("error while playing sound" + str(e))
		else:
			await channel.send("You're not in a voice channel or you're connected to a channel which I can't access.")

@client.event
async def on_voice_state_update(member,before,after):
	global voice
	global currentVoiceChannel
	global volume
	user = member
	perm = None
	if after.channel != None:
		perm = after.channel.permissions_for(after.channel.guild.me).connect
	else:
		perm = False

	if user != client.user and after.channel != None and perm and after.channel != before.channel:
		try:
			if voice != None:
				voice.stop()

			if currentVoiceChannel != after.channel:
				if voice != None:
					await voice.disconnect()
				logger.debug("joining voice channel")
				voice = await after.channel.connect()
				currentVoiceChannel = after.channel

			for format in conf['fileformats']:
				if os.path.exists(Controller.config_file["sound_folder"] + user.name + format):
					sourceToPlay = discord.FFmpegPCMAudio(Controller.config_file["sound_folder"] + user.name + format)
					sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
					sourceToPlay.volume = volume
					voice.play(sourceToPlay)
					break
		except Exception as e:
			logger.debug("error in playing join sound" + str(e))

#@client.event
# async def on_message(message):
# 	global commandNames
# 	if not message.author.bot:
# 		channel = message.channel
# 		if type(message.channel) is discord.DMChannel:
# 			if message.author.id in conf['whitelist'] or message.author.id == conf['ownerID'] or message.author.id in conf['admins']:
# 				if len(message.attachments) > 0:
# 					logger.debug("attachement detected")
# 					if message.attachments[0].filename[message.attachments[0].filename.rfind('.'):] in conf['fileformats']:				#Check if fileformat is specified in config
# 						exists = False
# 						folder_dict_keys = kakadu.folder_dict.keys()
# 						if (not message.content) or message.content == "rest":						#Check wether "rest" or no text was sent along with the soundfile
# 							cat = "rest"															
# 						elif message.content in folder_dict_keys:									#Else check if category exists in dictionary
# 							cat = message.content													
# 						else:																		#Else set cat to NULL to give Error Feedback to the user
# 							cat = None
# 						if cat:
# 							for format in conf['fileformats']:
# 								if os.path.exists(kakadu.getSoundDir() + cat + message.attachments[0].filename[:message.attachments[0].filename.rfind('.')] + format) or message.attachments[0].filename[:message.attachments[0].filename.rfind('.')] in kakadu.getListOfAliases():
# 									#Long line above is to check if file is already located under the category path or already included in another category in the dictionary
# 									exists = True
# 							if message.attachments[0].filename[:message.attachments[0].filename.rfind('.')] in commandNames:
# 								exists = True
# 							if not exists:					#Try to download the Sound if not redundant
# 								logger.debug("trying to save new sound")
# 								try:
# 									await message.attachments[0].save(kakadu.getSoundDir() + cat + "/" + message.attachments[0].filename)			#Save file in the given category
# 									client.get_command("play_sound").aliases.append(message.attachments[0].filename[:message.attachments[0].filename.rfind('.')])
# 									kakadu.init_dict()								#Add new sound to dictionary by reinitializing from directory path
# 									ncmd = client.get_command("play_sound")
# 									client.all_commands[message.attachments[0].filename[:message.attachments[0].filename.rfind('.')]] = ncmd
# 									logger.debug("file successfully received")
# 									await channel.send(f"Sound successfully added to {cat}!")
# 								except Exception as e:
# 									logger.debug(str(e))
# 									await channel.send("Something went wrong. Please try again.")
# 							else:
# 								await channel.send("This sound does already exist or is the name of a command.")
# 						else:
# 							await channel.send(f"Category {message.content} does not exist. Resend the file with an available category or use category- rest - instead!")		#Exception for cat == None in case not available category was given
# 					else:
# 						reply = "This is an invalid filetype. Files can be of the type:\n"
# 						reply += ", ".join(conf['fileformats'])
# 						await channel.send(reply)
# 						logger.debug("invalid filetype")
# 				else:
# 					await client.process_commands(message)
# 			else:
# 				await channel.send("Your are not allowed to use this bot. Please contact your admin to be added to the whitelist.")
# 		else:
# 			if len(message.attachments) > 0:
# 				pass
# 			else:
# 				if message.content.startswith(conf['invoker']):
# 					if message.channel.id == conf['commandChannel']:
# 						if message.author.id in conf['whitelist'] or message.author.id == conf['ownerID'] or message.author.id in conf['admins']:
# 							await client.process_commands(message)
# 						else:
# 							await channel.send("You are not allowed to use this bot. Please contact your admin to be added to the whitelist.")
# 					elif conf['commandChannel'] == 0:
# 						if message.content.startswith(conf['invoker'] + "setcmdchn"):
# 							await client.process_commands(message)
# 						else:
# 							if message.author.dm_channel == None:
# 								try:
# 									await message.author.create_dm()
# 								except Exception as e:
# 									logger.debug(str(e))
# 							await message.author.dm_channel.send("The bot is not yet configured to be used in a public text channel. Please contact your admin or, if you are one, use " + conf['invoker'] + "setcmdchn to bind the bot to a text channel.")


def srv_sound(sound):
	global voice
	logger.info("message received")
	if voice != None:
		voice.stop()
		if voice.is_connected():
			for format in conf['fileformats']:
				#folder_dict_keys=folder_dict.keys()
				#for folder_key in folder_dict_keys:				#check if ctx is included into list, create path to file
				#	if ctx.message.content[1:] in folder_dict[folder_key]:
				#		path=sound_dir+folder_key+"/"
				pathToSound = getcatpath(sound) + sound + format
				if os.path.exists(pathToSound):
					sourceToPlay = discord.FFmpegPCMAudio(pathToSound)
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
		logger.info("set volume to" + str(volume))

	except Exception as e:
		logger.debug(str(e))

websrv.play_sound=srv_sound
websrv.set_volume=srv_volume
start_new_thread(websrv.app.run, (conf['host'], conf['port']))
client.run(conf['token'])
