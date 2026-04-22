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

token = ''
prefix = '/'

intents = discord.Intents.all()

#декоратор
bot = commands.Bot(command_prefix=prefix, intents=intents)

#канал в который выводит speechtotext
TEXT_CHANNEL_ID = 1496569411614801980

#модель whisper
model = WhisperModel("small", compute_type="int8")


#логика speechtotext
class VoiceSink(voice_recv.AudioSink):
    def __init__(self, bot):
        self.bot = bot
        self.buffers = {}

    def wants_opus(self):
        return False

    def cleanup(self):
        pass

    def write(self, user, data):
        if user is None:
            return

        if user.id not in self.buffers:
            self.buffers[user.id] = []

        self.buffers[user.id].append(data.pcm)

        if len(self.buffers[user.id]) > 50:
            audio_bytes = b"".join(self.buffers[user.id])
            self.buffers[user.id] = []

            asyncio.create_task(self.process(user, audio_bytes))

    async def process(self, user, audio_bytes):
        try:
            audio_np = np.frombuffer(audio_bytes, np.int16).astype(np.float32) / 32768.0
            segments, _ = model.transcribe(audio_np, language="ru")

            text = " ".join([seg.text for seg in segments]).strip()

            if text:
                channel = self.bot.get_channel(TEXT_CHANNEL_ID)
                if channel:
                    await channel.send(f"🎤 {user.name}: {text}")

        except Exception as e:
            print("Ошибка распознавания:", e)

#тест команда
@bot.command()
async def hello(ctx):
    await ctx.reply("Hello")


#коннект команда
@bot.command()
async def connect(ctx):
    if not ctx.author.voice:
        await ctx.reply("ты не в войсе")
        return

    vc = await ctx.author.voice.channel.connect(cls=voice_recv.VoiceRecvClient)

    sink = VoiceSink(bot)
    vc.listen(sink)

    await ctx.reply("зашел в войс и слушаю")
    print("в канале")

#дисконнект команда
@bot.command()
async def disconnect(ctx):
    await ctx.voice_client.disconnect()
    await ctx.reply("вышел")




bot.run(token)