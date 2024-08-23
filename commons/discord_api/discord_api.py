import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

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


async def async_wrapper(func, *args):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, func, *args)


async def main():
    bot, token = init_bot()
    asyncio.create_task(bot.start(token))
    await asyncio.sleep(5)

    # You can write Discord feature testing code here:
    wsa = await get_wsa_guild(bot)
    discord_event = await wsa.fetch_scheduled_event(1276190206999134301)
    await discord_event.delete()


if __name__ == '__main__':
    asyncio.run(main())
