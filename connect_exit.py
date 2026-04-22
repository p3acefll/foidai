import discord
from discord.ext import commands
from discord.ext import voice_recv
import numpy as np
import asyncio
import wave
import io
from faster_whisper import WhisperModel

print(discord.__version__)
print(discord.__file__)

token = 'MTQ5NjUzOTE0Mzk2OTE4MTc4Ng.GcVZnY.gbRS-iCPwytF12ozhKmBtiTCfzMb-6odt_PqYg'
prefix = '/'

intents = discord.Intents.all()

#декоратор
bot = commands.Bot(command_prefix=prefix, intents=intents)

#канал в который выводит speechtotext
TEXT_CHANNEL_ID = 1496569411614801980

#модель whisper
model = WhisperModel("small", compute_type="int8")

#тест команда
@bot.command()
async def hello(ctx):
    await ctx.reply("Hello")

#коннект команда
@bot.command()
async def connect(ctx):
    if not ctx.author.voice:
        await ctx.reply("ты не в войсе")

    await ctx.author.voice.channel.connect()
    await ctx.reply("зашел в войс")
    print("в канале")

#дисконнект команда
@bot.command()
async def disconnect(ctx):
    await ctx.voice_client.disconnect()
    await ctx.reply("вышел")




bot.run(token)