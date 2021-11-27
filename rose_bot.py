import discord
import os
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import Bot
import youtube_dl
from discord import FFmpegPCMAudio
import pyttsx3
from gtts import gTTS
from datetime import date
from datetime import datetime
from time import sleep
from itertools import cycle
from dotenv.main import load_dotenv
from pytube import YouTube
import urllib.parse, urllib.request, re




status = cycle(["Gone" , "On the ground"])




client = commands.Bot(command_prefix='', intents = discord.Intents.all())




def doc_file_mp3(ctx,url):
	guild = ctx.guild
	voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=guild)
	audio_source = discord.FFmpegPCMAudio(url)
	if not voice_client.is_playing():
		voice_client.play(audio_source, after=None)




@client.event
async def on_ready():
	change_status.start()
	print("Rosé đang online .....")


@tasks.loop(seconds = 100)
async def change_status():
	await client.change_presence(activity = discord.Game(next(status)))


@client.command(pass_context = True)
async def xoa(ctx , amount = 1):
	await ctx.channel.purge(limit = amount+1)
	print("Rosé đã xóa {} dòng !" . format(amount))


@client.command()
async def ping(ctx):
	ping_ = client.latency
	ping =  round(ping_ * 1000)
	embed = discord.Embed(
		title = "Rosé !   {}ms" . format(ping), 
		colour = 0xff66ff , 
		)
	await ctx.send(embed = embed)
	print("Rosé ping: {}ms".format(ping))


@client.command()
async def disconnect(ctx):
	await ctx.send('Bye Bye !!')
	await ctx.voice_client.disconnect()
	print('Rosé đã rời phòng')	


@client.command()
async def join(ctx):
	if (ctx.author.voice):
		kenh = ctx.message.channel
		c = discord.utils.get(ctx.guild.channels)
		channel_id = c.id
		channel = ctx.message.author.voice.channel
		voice = await channel.connect()
		print("Rosé đã tham gia thoại {}    {}" .format(channel_id,kenh) )
		# source = FFmpegPCMAudio('hello.wav')
		# player = voice.play(source)
	else:
		await ctx.send("Có ai nói chuyện đâu mà vào" , delete_after=5)	


@client.command(pass_context = True)
async def play(ctx : commands.Context, *,send: str):
	#xem link hay search
	url = ""
	a = send[0:24]


	try:
		ctx.voice_client.stop()
	except Exception as ero:
		await ctx.send("Chị chưa tham gia thoại" , delete_after=5)	


	if a =="https://www.youtube.com/":
		url = str(send)
	else:
		query_string = urllib.parse.urlencode({'search_query': send})
		htm_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
		search_results = re.findall(r'/watch\?v=(.{11})',htm_content.read().decode())
		url = "http://www.youtube.com/watch?v=" + search_results[0]	

	try:
		yt = YouTube(url)
		time_msg = yt.length
		title_msg = yt.title
		views_msg = str(yt.views)
		thum_img = yt.thumbnail_url


		views_val = views_msg +" views"
		time_val = str(time_msg) +" s"
		title_val = "Rosé đang hát: "+title_msg
		embed = discord.Embed(
			title = title_val, 
			colour = 0xff66ff , 
		)
		embed.add_field(name = "Lượt xem" , value = views_val  , inline = True)
		embed.add_field(name = "Thời lượng" , value = time_val , inline = False)
		embed.set_image(url = thum_img)

		FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
		YDL_OPTIONS = {'format':'best'}
		vc = ctx.voice_client

		print("Rosé hát 1 lần bài {}".format( title_msg))
		await ctx.send(embed =embed)

		with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
			info = ydl.extract_info(url, download = False)
			url2 = info['formats'][0]['url']
			
			source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
			print("Rosé đang phát nhạc trên Youtube !")
			vc.play(source)

	except Exception as e:
		await ctx.send("Chị không tìm thấy bài hát" , delete_after=15)
		print (e)

	
@client.command()
async def pause(ctx):
	await ctx.channel.purge(limit = 1)
	await ctx.voice_client.pause()
	await ctx.send("Chị đã tạm dừng hát" , delete_after=10)
	print("Rosé đã tạm dừng hát")		


@client.command()
async def resume(ctx):
	await ctx.channel.purge(limit = 1)
	await ctx.voice_client.resume()
	await ctx.send("Chị lại tiếp tục hát",delete_after=10)
	print("Rosé đã tiếp tục hát")



@client.command()
async def hello(ctx):
	await ctx.channel.purge(limit = 1)
	try:
		doc_file_mp3(ctx,"hello.wav")
		print("Rosé nói: Hello")
	except Exception as e:
		print("Chị chưa vào làm sao chào em được")
		await ctx.send("Chị chưa vào làm sao chào em được",delete_after=10 )


@client.command()
async def time(ctx):
	robot_mouth = pyttsx3.init()
	now = datetime.now()
	h = int(now.strftime("%H"))
	m = int(now.strftime("%M"))
	s = int(now.strftime("%S"))+1
	if h>=23 or 0<= h <=5:
		robot_brain = "Bây giờ là {} giờ {} phút {} giây. Địt mẹ muộn rồi ngủ đi !!".format(h,m,s)
	else:	
		robot_brain = "Bây giờ là {} giờ {} phút {} giây".format(h,m,s)
	tts = gTTS(text =robot_brain,lang='vi')
	
	tts.save("thoigian.mp3")
	print("Rosé thông báo:  " +robot_brain)
	try:
		
		doc_file_mp3(ctx,"thoigian.mp3")
		await ctx.send(robot_brain , delete_after=300)
	except Exception as e:
		await ctx.send(robot_brain)
		print(e)		


@client.command()
async def read(ctx : commands.Context, *,txt: str):
	robot_mouth = pyttsx3.init()
	robot_brain = txt
	tts = gTTS(text =robot_brain,lang='vi')
	tts.save("doctiengviet.mp3")
	print("Rosé read:  " +txt)
	try:
		doc_file_mp3(ctx,"doctiengviet.mp3")
		await ctx.channel.purge(limit = 1)
	except Exception as e:
		print(e)


@client.command()
async def readeng(ctx : commands.Context, *,txt: str):
	robot_mouth = pyttsx3.init()
	robot_brain = txt
	tts = gTTS(text =robot_brain,lang='en' , tld ="com.au")
	tts.save("doctienganh.mp3")
	print("Rosé read english:  " +txt)
	try:
		doc_file_mp3(ctx,"doctienganh.mp3")
		await ctx.channel.purge(limit = 1)
	except Exception as e:
		print(e)


load_dotenv()
token = os.getenv("TOKEN")
client.run(token)
# https://discord.com/api/oauth2/authorize?client_id=912622098520875018&permissions=8&scope=bot



