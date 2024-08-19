import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

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


bot.run(bot_token)
