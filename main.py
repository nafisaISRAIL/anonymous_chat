import argparse
import asyncio
from async_timeout import timeout
import logging
from datetime import datetime

import aiofiles

import gui
from server_connection import (authorise, check_connection_sender_service, connect,
                               submit_message, watch_for_connection)

logging.basicConfig(level=logging.DEBUG)


async def read_msgs(host, port, message_queue, filepath, status_update_queue, watch_queue):

    status_update_queue.put_nowait(gui.ReadConnectionStateChanged.INITIATED)
    reader, _ = await asyncio.open_connection(host, port)
    status_update_queue.put_nowait(gui.ReadConnectionStateChanged.ESTABLISHED)
    while True:
        line = await reader.readline()
        if not line:
            break
        watch_queue.put_nowait("New message in chat")
        line = line.decode("utf-8")
        if line:
            date = datetime.now().strftime("%y.%m.%d %H:%M")
            line = f"[{date}] " + line
            message_queue.put_nowait(line)
            async with aiofiles.open(filepath, mode="a") as file:
                await file.write(line)

    status_update_queue.put_nowait(gui.ReadConnectionStateChanged.CLOSED)


async def saved_messages(filepath, saved_messages_queue):
    saved_messages_queue.put_nowait("in saved messages")
    async with aiofiles.open(filepath, mode="r") as file:
        async for line in file:
            saved_messages_queue.put_nowait(line)


async def send_msgs(host, port, queue, token, watch_queue):
    while True:
        message = await queue.get()
        await submit_message(host, port, message, token)
        watch_queue.put_nowait("Message sent")


async def main(host, reader_port, sender_port, filepath, nickname="Devman"):
    saved_messages_queue = asyncio.Queue()
    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    user_info = await authorise(nickname, host, sender_port, status_updates_queue, watchdog_queue)
    token = user_info["account_hash"]

    # check connection of sending host
    await check_connection_sender_service(host, sender_port, reader_port, status_updates_queue, watchdog_queue)

    await asyncio.gather(
        gui.draw(
            messages_queue,
            sending_queue,
            status_updates_queue,
            saved_messages_queue),

        saved_messages(filepath, saved_messages_queue),
        read_msgs(host, reader_port, messages_queue, filepath, status_updates_queue, watchdog_queue),
        saved_messages(filepath, saved_messages_queue),
        send_msgs(host, sender_port, sending_queue, token, watchdog_queue),
        watch_for_connection(watchdog_queue)
    )


parent_parser = argparse.ArgumentParser(prog="listen-minechat")
parent_parser.add_argument("--host", type=str, default="minechat.dvmn.org", help="Connection host.")
parent_parser.add_argument("--sender_port", type=int, default=5000, help="Connection port - reader.")
parent_parser.add_argument("--reader_port", type=int, default=5050, help="Connection port - sender.")
parent_parser.add_argument("--history", type=str, default="history.txt", help="Store file location.")

args = parent_parser.parse_args()
asyncio.run(main(args.host, args.sender_port, args.reader_port,"history.txt"))
