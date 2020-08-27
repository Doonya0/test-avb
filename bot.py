import discord
from discord.ext import commands
from discord.utils import get 
import youtube_dl

import os
from time import sleep
import requests

PREFIX = '.'

client = commands.Bot( command_prefix = PREFIX )
client.remove_command( 'help' )

@client.event

async def on_ready():
	print( 'Bot ONLINE' )

	await client.change_presence( status = discord.Status.online, activity = discord.Game( '.help' ) )

@client.event

async def on_member_join( member ):
	channel = client.get_channel( 748334249542811650 )

	role = discord.utils.get( member.guild.roles, id = 748333584951279786 )

	await member.add_roles( role )
	await channel.send( f'{ member.mention } зашёл на сервер' ) 

# Clear message
@client.command( pass_context = True )
@commands.has_permissions( administrator = True )

async def clear( ctx, amount : int ):
	await ctx.channel.purge( limit = amount )

	await ctx.send( f'Удалено {amount} сообщений' )

#Kick
@client.command( pass_context = True )
@commands.has_permissions( administrator = True )

async def kick( ctx, member: discord.Member, *, reason = None ):
	await ctx.channel.purge( limit = 1 )

	await member.kick( reason = reason )
	await ctx.send( f'Был кинут { member.mention }' )

#Ban
@client.command( pass_context = True )
@commands.has_permissions( administrator = True )

async def ban( ctx, member: discord.Member, *, reason = None ):
	emb = discord.Embed( colour = discord.Color.red(), )
	await ctx.channel.purge( limit = 1 )
	await member.ban( reason = reason )

	emb.set_author( name = member.name, icon_url = member.avatar_url )
	emb.add_field( name = 'Был забанен:', value = ' ---- {}'.format( member.mention )  )
	emb.set_footer( text = 'Забанен : {}'.format( ctx.author.name ), icon_url = ctx.author.avatar_url )

	await ctx.send( embed = emb )

	#await ctx.send( f' Был забанен { member.mention }' )


# Unban
@client.command( pass_context = True )
@commands.has_permissions( administrator = True )

async def unban( ctx, *, member ):
	await ctx.channel.purge( limit = 1 )

	banned_users = await ctx.guild.bans()

	for ban_entry in banned_users:
		user = ban_entry.user

		await ctx.guild.unban( user )
		await ctx.send( f'Был разбанен {user.mention}' )

		return

#.help
@client.command( pass_context = True )
@commands.has_permissions( administrator = True )

async def help( ctx ):
	emb = discord.Embed( title = 'Навигация по командам', colour = 5295734 )

	emb.add_field( name = '{}clear'.format( PREFIX ), value = 'Удалить n сообщений в текущем канале' )
	emb.add_field( name = '{}ban'.format( PREFIX ), value = 'Забанить пользователя' )	
	emb.add_field( name = '{}kick'.format( PREFIX ), value = 'Выгнать пользователя' )
	emb.add_field( name = '{}unban'.format( PREFIX ), value = 'Разбанить пользователя' )
	emb.add_field( name = '{}mute'.format( PREFIX ), value = 'Выдать роль мута' )
	emb.add_field( name = '{}play'.format( PREFIX ), value = 'Позвать бота в канал' )
	emb.add_field( name = '{}stop'.format( PREFIX ), value = 'Выгнать бота из канала' )

	await ctx.author.send( embed = emb )

# Mute
@client.command()
@commands.has_permissions( administrator = True )

async def mute( ctx, member: discord.Member ):
	await ctx.channel.purge( limit = 1 )

	mute_role = discord.utils.get( ctx.message.guild.roles, name = 'Mute' )

	await member.add_roles( mute_role )
	await ctx.send( f'{ member.mention } получил(-а) роль мута!' )

#Ошибки 
@clear.error
async def clear_error( ctx, error ):
	if isinstance( error, commands.MissingRequiredArgument ):
		await ctx.send( f'{ ctx.author.name }, введите n количество аргумента!' )

	if isinstance( error, commands.MissingPermissions ):
		await ctx.send( f'{ ctx.author.name }, недостаточно прав!' )

#Подключение бота
@client.command()
async def join( ctx ):
	global voice
	channel = ctx.message.author.voice.channel
	voice = get(client.voice_clients, guild = ctx.guild)

	if voice and voice.is_connected():
		await voice.move_to(channel)
	else:
		voice = await channel.connect()
		#await ctx.send( f'Бот присойденился к каналу - {channel}' )

@client.command()
async def leave( ctx ):
	channel = ctx.message.author.voice.channel
	voice = get(client.voice_clients, guild = ctx.guild)

	if voice and voice.is_connected():
		await voice.disconnect()
	else:
		voice = await channel.connect()
		#await ctx.send(f'Бот отключился от канала - {channel}')
# Music
@client.command()
async def play( ctx, url : str ):
	song_there = os.path.isfile( 'song.mp3' )

	try:
		if song_there:
			os.remove( 'song.mp3' )
			print( '[log] Старый файл удалён ' )
	except PermissionError:
		print( '[log] Не удалось удалить файл' )

	await ctx.send( 'Пожалуйста ожидайте' ) 

	voice = get( client.voice_clients, guild = ctx.guild )


	ydl_opts = {
		'format' : 'bestaudio/best',
		'postprocessors' : [{
			'key' : 'FFmpegExtactAudio',
			'preferredcodec' : 'mp3',
			'preferredquality' : '192'
		}]
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		print( '[log] Загружаю музыку...' )	
		ydl.download([url])

	for file in os.listdir( './' ):
		if file.endswith( '.mp3' ):
			name = file
			print( f'[log] Переименовываю файл: {file}' )
			os.rename( file, 'song.mp3' )

	voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log] {name}, музыка закончила своё поигрование'))
	voice.source = discord.PCMVolumeTransformer(voice.source)
	voice.source.volume = 0.07

	song_name = name.rsplist('-', 2)
	await ctx.send(f'Сейчас поигрывает музыка: {song_name[0]}')

#Get TOKEN
#token = open( 'token.txt', 'r' ).readline()

#client.run( token ) 
token = os.environ.get('BOT_TOKEN')

bot.run(str(token))
