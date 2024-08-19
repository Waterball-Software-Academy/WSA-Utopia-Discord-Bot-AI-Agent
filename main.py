import asyncio
import os

import discord
import uvicorn
from discord.ext import commands
from dotenv import load_dotenv
from fastapi import FastAPI
from speech.app.api.endpoints import router as speech_router

load_dotenv()
bot_token = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')


@bot.event
async def on_message(message):
    print(message)


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send('Hello, World!')


middleware = [
]
app = FastAPI(middleware=middleware)
app.include_router(speech_router, prefix="/api")


async def start_discord_bot():
    await bot.start(bot_token)


async def start_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(start_server(), start_discord_bot())


if __name__ == "__main__":
    asyncio.run(main())
