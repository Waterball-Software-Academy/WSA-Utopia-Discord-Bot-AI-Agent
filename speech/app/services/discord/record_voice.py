import os

import discord.opus as opus
from dotenv import load_dotenv

import discord

from speech.app.services.discord.my_pcm_sink import MyPcmSink

load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())
WSA_GUILD_ID = os.getenv('GUILD_ID')
connections = {}


async def finished_callback(sink, channel: discord.TextChannel, *args):
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()
    files = [
        discord.File(audio.file, f"{user_id}.{sink.encoding}")
        for user_id, audio in sink.audio_data.items()
    ]
    await channel.send(
        f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files
    )


@bot.event
async def on_message(message):
    print(message)


@bot.command(name="record", description="Record a voice message",
             guild_ids=[WSA_GUILD_ID])
async def start(ctx: discord.ApplicationContext):
    """Record your voice!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    vc.start_recording(
        MyPcmSink(),
        finished_callback,
        ctx.channel,
    )

    await ctx.respond("The recording has started!")


@bot.command(name="stop-recording", description="Stop recording a voice message",
             guild_ids=[WSA_GUILD_ID])
async def stop(ctx: discord.ApplicationContext):
    """Stop recording."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("Not recording in this guild.")


opus.load_opus('/opt/homebrew/opt/opus/lib/libopus.dylib')
if not opus.is_loaded():
    print("OPUS NOT LOADED")
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
