import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv
from fastapi import Depends

from commons.utils import logging

load_dotenv()
logger = logging.get_logger("discord_api")

guild_id = os.getenv('GUILD_ID')
mod_speech_application_review_channel_id = os.getenv('MOD_SPEECH_APPLICATION_REVIEW_CHANNEL_ID')
speech_voice_channel_id = os.getenv('SPEECH_VOICE_CHANNEL_ID')

_discord_app = None
_discord_app_event_loop = None
_wsa = None


def init_bot() -> tuple[Bot, str | None]:
    discord_bot_loop = asyncio.get_event_loop()
    print(f"Event Loop(init_bot): {id(discord_bot_loop)}")
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    global _discord_app
    _discord_app = commands.Bot(command_prefix="!", intents=intents)

    @_discord_app.event
    async def on_ready():
        loop = asyncio.get_event_loop()
        logger.trace(f"Discord bot on ready. EventLoop id:(@_discord_app.event on_ready()) {id(loop)}")
        print('------')
        print(f'Logged in as {_discord_app.user.name}')
        print(f'Bot ID: {_discord_app.user.id}')
        print('------')
        global _wsa, _discord_app_event_loop
        _discord_app_event_loop = discord_bot_loop
        _wsa = await _discord_app.fetch_guild(int(guild_id))

    return _discord_app, bot_token


def get_discord_app() -> discord.Bot:
    global _discord_app
    return _discord_app


DiscordAppDependency = Depends(get_discord_app)


async def get_wsa_guild() -> discord.Guild:
    global _wsa
    return _wsa


WsaGuildDependency = Depends(get_wsa_guild)


async def schedule_task(coro_func, *args, **kwargs):
    _discord_app_event_loop.create_task(coro_func(*args, **kwargs))

async def execute_task_and_get_result(coro_func, *args, **kwargs):
    future = asyncio.Future()

    def callback(future_task):
        if not future.done():  # 確保 future 尚未完成或被取消
            try:
                result = future_task.result()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)

    task = asyncio.run_coroutine_threadsafe(coro_func(*args, **kwargs), _discord_app_event_loop)
    task.add_done_callback(callback)

    return await future

async def async_wrapper(func, *args):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, func, *args)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    bot, token = init_bot()
    asyncio.create_task(bot.start(token))
    await asyncio.sleep(3)

    # You can write Discord feature testing code here:
    wsa = await get_wsa_guild(bot)
    from speech.app.services.speech_service import SpeechService
    speech_service = SpeechService(bot, wsa, None, None, None, None)
    discord_event = await wsa.fetch_scheduled_event(1276491267978694727)
    await discord_event.delete()


if __name__ == '__main__':
    asyncio.run(main())
