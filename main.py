from dotenv import load_dotenv
import asyncio
import uvicorn
from fastapi import FastAPI
import commons.discord_api.discord_api as discord_api
from speech.app.api.endpoints import router as speech_router

load_dotenv()
__discord_app, bot_token = discord_api.init_bot()


@__discord_app.event
async def on_ready():
    print(f'Logged in as {__discord_app.user.name}')
    print(f'Bot ID: {__discord_app.user.id}')
    print('------')


@__discord_app.event
async def on_message(message):
    print(message)


@__discord_app.command(name="hello")
async def hello(ctx):
    await ctx.send('Hello, World!')


middleware = [
]
app = FastAPI(middleware=middleware)
app.include_router(speech_router, prefix="/api")


async def start_discord_bot():
    await __discord_app.start(bot_token)


async def start_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(start_server(), start_discord_bot())


if __name__ == "__main__":
    asyncio.run(main())
