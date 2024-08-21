import os

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv
from fastapi import Depends

load_dotenv()
__discord_app = None
guild_id = os.getenv('GUILD_ID')
mod_speech_application_review_channel_id = os.getenv('MOD_SPEECH_APPLICATION_REVIEW_CHANNEL_ID')
speech_voice_channel_id = os.getenv('SPEECH_VOICE_CHANNEL_ID')


def init_bot() -> tuple[Bot, str | None]:
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    global __discord_app
    __discord_app = commands.Bot(command_prefix="!", intents=intents)
    return __discord_app, bot_token


def get_discord_app() -> discord.Bot:
    return __discord_app


DiscordAppDependency = Depends(get_discord_app)


async def get_wsa_guild(discord_app: discord.Bot = DiscordAppDependency) -> discord.Guild:
    wsa = await discord_app.fetch_guild(int(guild_id))
    return wsa


WsaGuildDependency = Depends(get_wsa_guild)
