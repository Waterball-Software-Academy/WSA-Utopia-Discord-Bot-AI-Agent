import asyncio
import logging
import threading
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware import Middleware
from langserve import add_routes

import commons.discord_api.discord_api as discord_api
from commons.fastapi.middlewares import TraceIdToLoggerMiddleware
from commons.google.calendar import google_calendar
from commons.speech_ai_agent.agent import create_workflow
from speech.app.api.endpoints import router as speech_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # asyncio.create_task(start_discord_bot())
    await google_calendar.connect_to_service()
    yield


middleware = [
    Middleware(TraceIdToLoggerMiddleware)
]
app = FastAPI(middleware=middleware, lifespan=lifespan)
app.include_router(speech_router, prefix="/api/speeches")

agent = create_workflow()
add_routes(app, agent, path='/api/speeching')


async def start_discord_bot():
    _discord_app, bot_token = discord_api.init_bot()
    loop = asyncio.get_event_loop()
    print(f'Event loop started (start_discord_bot): LoopId={id(loop)}')
    await _discord_app.start(bot_token)
    # TODO: add all pending views to persist their states, otherwise views don't work after the discord bot restarted


async def start_fastapi_server():
    loop = asyncio.get_event_loop()
    print(f'Event loop started (start_fastapi_server): LoopId={id(loop)}')
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(start_discord_bot(), start_fastapi_server())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    child_thread = threading.Thread(target=asyncio.run, args=(start_fastapi_server(),))
    child_thread.start()

    asyncio.run(start_discord_bot())
    child_thread.join()
