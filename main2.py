import discord
print(discord.__version__)
print(discord.__file__)

from discord.ext import commands

# ВАЖНО: Никогда не выкладывай токен в открытый доступ! 
# Сбрось его в Discord Developer Portal прямо сейчас.
token = ''
prefix = '/'

# Исправленное создание интентов
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=prefix, intents=intents)

# Исправленный декоратор (bot.command вместо bot_command)
@bot.command()
async def hello(ctx):
    await ctx.reply("Hello")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.reply("Не в войсе")
    await ctx.author.voice.channel.connect()
    await ctx.reply("Я зашел в войс")

bot.run(token)