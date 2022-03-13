import os
import asyncio
from tkinter import *

from server_connection import register
import logging


loop = asyncio.get_event_loop()

def get_token(input_field, root, main_label, host, port):
    nickname = input_field.get()
    try:
        loop.run_until_complete(register(host, port, nickname))
        main_label.config(text="The token was retreived.")
    finally:
        root.after(1000, lambda : root.destroy())


def registration(host, port):
    root = Tk()
    root.title("Chat authorization")

    root_frame = Frame()
    root_frame.pack(fill="both", expand=True)

    main_label = Label(root_frame, text="Please enter your nickname", font="16", pady = 20)
    main_label.pack()

    input_frame = Frame(root_frame)
    input_frame.pack(side="bottom", fill=X)

    input_field = Entry(input_frame)
    input_field.pack(side="left", fill=X, expand=True)


    send_button = Button(input_frame)
    send_button["text"] = "Authorize"
    send_button["command"] = lambda: get_token(input_field, root, main_label, host, port)
    send_button.pack(side="left")

    input_frame.pack(padx=10,pady=10)
    root.bind('<Control-c>', lambda event: root.destroy())
    root.mainloop()
