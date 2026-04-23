import discord
from discord.ext import commands
from discord.ext import voice_recv
import numpy as np
import asyncio
from faster_whisper import WhisperModel
import scipy.signal
import logging

# Убираем бесконечный спам RTCP
logging.getLogger('discord.ext.voice_recv.reader').setLevel(logging.ERROR)
logging.getLogger('discord.ext.voice_recv.gateway').setLevel(logging.ERROR)
logging.getLogger('discord.ext.voice_recv.router').setLevel(logging.WARNING)

print(discord.__version__)
print(discord.__file__)

token = ''
prefix = '/'

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=prefix, intents=intents)

# Канал для вывода текста (можно оставить или убрать)
TEXT_CHANNEL_ID = 1496569411614801980

# Модель (small — быстро, medium/large-v3-turbo — точнее)
model = WhisperModel("small", device="cpu", compute_type="int8")


class VoiceSink(voice_recv.AudioSink):
    def __init__(self, bot):
        self.bot = bot
        self.buffers = {}
        self.buffer_size = 160
        print("✅ VoiceSink создан (small + улучшенная обработка)")

    def wants_opus(self):
        return False

    def cleanup(self):
        self.buffers.clear()

    def write(self, user, data):
        if user is None or not data.pcm:
            return

        user_id = user.id
        if user_id not in self.buffers:
            self.buffers[user_id] = []

        self.buffers[user_id].append(data.pcm)

        if len(self.buffers[user_id]) >= self.buffer_size:
            audio_bytes = b"".join(self.buffers[user_id])
            self.buffers[user_id] = []
            asyncio.run_coroutine_threadsafe(self.process(user, audio_bytes), self.bot.loop)

    async def process(self, user, audio_bytes):
        try:
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            if len(audio_np.shape) > 1 and audio_np.shape[1] == 2:
                audio_mono = audio_np.mean(axis=1)
            else:
                audio_mono = audio_np

            audio_16k = scipy.signal.resample_poly(audio_mono, up=1, down=3)

            # Нормализация громкости
            rms = np.sqrt(np.mean(audio_16k ** 2))
            if rms > 0:
                audio_16k = audio_16k / rms * 0.2

            segments, info = model.transcribe(
                audio_16k,
                language="ru",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                beam_size=7,
                best_of=7,
                temperature=0.0,
                condition_on_previous_text=False
            )

            text = " ".join(seg.text for seg in segments).strip()

            if text and len(text) > 2:
                print(f"🎤 {user.name}: {text}")
                channel = self.bot.get_channel(TEXT_CHANNEL_ID)
                if channel:
                    await channel.send(f"🎤 **{user.name}**: {text}")

        except Exception as e:
            print(f"❌ ОШИБКА В PROCESS у {user.name}: {e}")


@bot.command()
async def hello(ctx):
    await ctx.reply("Hello")


@bot.command()
async def connect(ctx):
    if not ctx.author.voice:
        await ctx.reply("Ты не в войсе")
        return

    vc = await ctx.author.voice.channel.connect(cls=voice_recv.VoiceRecvClient)

    sink = VoiceSink(bot)
    vc.listen(sink)

    await ctx.reply("Зашёл в войс и слушаю")
    print(f"✅ Бот подключился к каналу {ctx.author.voice.channel.name}")


@bot.command()
async def disconnect(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.reply("Вышел из войса")
    else:
        await ctx.reply("Я и так не в войсе")


bot.run(token)