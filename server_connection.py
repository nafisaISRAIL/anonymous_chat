import aiofiles
import argparse
import asyncio
import json
import logging

import gui

logging.basicConfig(level=logging.DEBUG)


async def submit_message(host, port, message, token):
    reader, writer = await connect(host, port, token)

    for _ in range(2):
        # pass returned authorized user data
        # pass rule of message sending
        await reader.readline()

    await send_data(writer, message)

    writer.close()
    logging.info("Message was sent")


async def authorise(nickname, host, sender_port, status_updates_queue):
    user_info = None
    async with aiofiles.open("token.txt", mode="r+") as token_file:
        user_info = await token_file.read()
        if not user_info:
            user_info = await register(host, sender_port, nickname)
            await token_file.write(user_info.decode())
            logging.info("The retreived token was saved.")

    try:
        user_info = json.loads(user_info)
        status_updates_queue.put_nowait(gui.NicknameReceived(user_info["nickname"]))
        return user_info
    except asyncio.CancelledError:
        logging.error("Error occurred while token was retrieving.")


async def register(host, port, nickname):
    reader, writer = await connect(host, port, '')
    try:
        nickname_ask_message = await reader.readline()
        logging.debug(nickname_ask_message.decode())

        await send_data(writer, nickname)

        user_data = await reader.readline()
        if not user_data:
            logging.error("Unknown token. Please check it or signup again.")
            raise asyncio.CancelledError
        return user_data
    except asyncio.CancelledError:
        logging.error("New account hash could not be retreived.")
    finally:
        writer.close()
    return user_data


async def connect(host, port, token):
    reader, writer = await asyncio.open_connection(host, port)
    greetings = await reader.readline()
    if not greetings:
        logging.error("Greeting message was not received.")
        raise asyncio.CancelledError
    logging.debug(greetings)
    await send_data(writer, token)
    return reader, writer


async def send_data(writer, data):
    data = data.replace("\\n", "")
    writer.write(f"{data}\n\n".encode())
    await writer.drain()

async def check_connection(host, port, token, status_update_queue):
    status_update_queue.put_nowait(gui.SendingConnectionStateChanged.INITIATED)
    reader, writer = await asyncio.open_connection(host, port)
    greetings = await reader.readline()
    if not greetings:
        logging.error("Greeting message was not received.")
        status_update_queue.put_nowait(gui.SendingConnectionStateChanged.CLOSED)
        raise asyncio.CancelledError
    status_update_queue.put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)
