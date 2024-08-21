import asyncio
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from langserve import add_routes

import commons.discord_api.discord_api as discord_api
from commons.google.calendar import google_calendar
from commons.speech_ai_agent.agent import create_workflow
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_discord_bot())
    await google_calendar.connect_to_service()
    yield


middleware = [
]
app = FastAPI(middleware=middleware, lifespan=lifespan)
app.include_router(speech_router, prefix="/api/speeches")

agent = create_workflow()
add_routes(app, agent, path='/api/speeching')

async def start_discord_bot():
    await __discord_app.start(bot_token)
    # TODO: add all pending views to persist their states, otherwise views don't work after the discord bot restarted


async def start_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await start_server()


if __name__ == "__main__":
    asyncio.run(main())
