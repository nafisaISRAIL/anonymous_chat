import asyncio
import json
import logging
from datetime import datetime

import aiofiles
from anyio import TASK_STATUS_IGNORED
from async_timeout import timeout

import gui

logger = logging.getLogger("secret_chat")


async def watch_for_connection(watch_queue):
    timestamp = int(datetime.timestamp(datetime.now()))
    while True:
        message = await watch_queue.get()
        logging.info(f"[{timestamp}] Connection is alive. {message}")

# user info functions

async def get_user_info_from_file():
    user_info = None
    async with aiofiles.open("token.txt", mode="r") as token_file:
        user_info = await token_file.read()
        if user_info:
            try:
                user_info = json.loads(user_info)
            except asyncio.CancelledError:
                logging.error("Error occurred while token was retrieving.")
    return user_info


async def get_user_info_from_server(host, port, get_token_queue):
    nickname = await get_token_queue.get()
    reader, writer = await connect_to_sender_server(host, port, '')
    try:
        # nickname ask message
        await reader.readline()

        await send_data(writer, nickname)

        user_info = await reader.readline()
        if not user_info:
            logging.error("Unknown token. Please check it or signup again.")
            raise asyncio.CancelledError

        async with aiofiles.open("token.txt", mode="w") as token_file:
            await token_file.write(user_info.decode())

    except asyncio.CancelledError:
        logging.error("New account hash could not be retreived.")
    finally:
        writer.close()


# send message functions
async def submit_message(host, port, message, token, watchdog_queue):
    reader, writer = await connect_to_sender_server(host, port, token, watchdog_queue)
    for _ in range(2):
        # pass returned authorized user data
        # pass rule of message sending
        await reader.readline()
    await send_data(writer, message)
    writer.close()


async def send_data(writer, data):
    data = data.replace("\\n", "")
    writer.write(f"{data}\n\n".encode())
    await writer.drain()


# network connection functions

async def handle_connection(host, port, watchdog_queue=None):
    try:
        async with timeout(5):
            reader, writer = await asyncio.open_connection(host, port)
            return reader, writer
    except asyncio.TimeoutError:
        if watchdog_queue:
            watchdog_queue.put_nowait("1s timeout is elapsed")


async def connect_to_sender_server(host, port, token, watchdog_queue=None):
    reader, writer = await handle_connection(host, port, watchdog_queue)
    greetings = await reader.readline()
    
    if not greetings:
        logging.error("Greeting message was not received.")
        raise asyncio.CancelledError
    await send_data(writer, token)
    return reader, writer

async def check_connection_sender_service(host, port, token, status_update_queue, watchdog_queue):
    status_update_queue.put_nowait(gui.SendingConnectionStateChanged.INITIATED)
    await connect_to_sender_server(host, port, token, watchdog_queue)
    status_update_queue.put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)


async def ping_pong(host, port, token, watchdog_queue):
    while True:
        async with timeout(2.5):
            logging.info("ping ************")
            await submit_message(host, port, "", token, watchdog_queue)
            logging.info("pong ************")
