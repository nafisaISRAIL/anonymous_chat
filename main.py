import argparse
import asyncio
import logging
import os
from datetime import datetime

import aiofiles
import anyio
from anyio import create_task_group
from async_timeout import timeout

import gui
from auth_gui import registration
from server_connection import (check_connection_sender_service, get_user_info,
                               handle_connection, ping_pong, submit_message,
                               watch_for_connection)

logging.basicConfig(level=logging.DEBUG)

HOST = os.getenv("HOST", "minechat.dvmn.org")
SENDER_PORT = os.getenv("SENDER_PORT", 5050)
READER_PORT = os.getenv("READER_PORT", 5000)


async def read_msgs(host, port, message_queue, filepath, status_update_queue, watchdog_queue):
    status_update_queue.put_nowait(gui.ReadConnectionStateChanged.INITIATED)
    reader, _ = await handle_connection(host, port, watchdog_queue)
    status_update_queue.put_nowait(gui.ReadConnectionStateChanged.ESTABLISHED)
    while True:
        line = await reader.readline()
        if not line:
            break
        watchdog_queue.put_nowait("New message in chat")
        line = line.decode("utf-8")
        if line:
            date = datetime.now().strftime("%y.%m.%d %H:%M")
            line = f"[{date}] " + line
            message_queue.put_nowait(line)
            async with aiofiles.open(filepath, mode="a") as file:
                await file.write(line)

    status_update_queue.put_nowait(gui.ReadConnectionStateChanged.CLOSED)


async def display_saved_messages(filepath, saved_messages_queue):
    async with aiofiles.open(filepath, mode="r") as file:
        async for line in file:
            saved_messages_queue.put_nowait(line)


async def send_msgs(host, port, queue, token, watchdog_queue):
    while True:
        message = await queue.get()
        await submit_message(host, port, message, token, watchdog_queue)
        watchdog_queue.put_nowait("Message sent")


async def main():
    filepath = "history.txt"
    saved_messages_queue = asyncio.Queue()
    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    user_info = await get_user_info()
    token = user_info["account_hash"]
    nickname = user_info["nickname"]
    status_updates_queue.put_nowait(gui.NicknameReceived(nickname))

    # check connection of sending host
    await check_connection_sender_service(HOST, SENDER_PORT, token, status_updates_queue, watchdog_queue)

    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(gui.draw,
                *[messages_queue,
                sending_queue,
                status_updates_queue,
                saved_messages_queue])

            tg.start_soon(read_msgs, *[HOST, READER_PORT, messages_queue, filepath, status_updates_queue, watchdog_queue])
            tg.start_soon(display_saved_messages, *[filepath, saved_messages_queue])
            tg.start_soon(send_msgs, *[HOST, SENDER_PORT, sending_queue, token, watchdog_queue])
            tg.start_soon(watch_for_connection, watchdog_queue),
            tg.start_soon(ping_pong, *[HOST, SENDER_PORT, token, watchdog_queue])

    except gui.TkAppClosed:
        logging.info("The program was closed!")


if __name__ == "__main__":
    registration(HOST, SENDER_PORT)
    asyncio.run(main())
