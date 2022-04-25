import tkinter as tk

from server_connection import get_user_info_from_server


def process_nickname(input_field, root, main_label, some_queue):
    nickname = input_field.get()
    some_queue.put_nowait(nickname)
    main_label.config(text="The token has been received.")
    root.after(1000, lambda : root.destroy())


async def register_new_user(some_queue):
    root = tk.Tk()
    root.title("Chat authorisation")

    root_frame = tk.Frame()
    root_frame.pack(fill="both", expand=True)

    main_label = tk.Label(root_frame, text="Please enter a nickname", font="16", pady = 20)
    main_label.pack()

    input_frame = tk.Frame(root_frame)
    input_frame.pack(side="bottom", fill=tk.X)

    input_field = tk.Entry(input_frame)
    input_field.pack(side="left", fill=tk.X, expand=True)


    send_button = tk.Button(input_frame)
    send_button["text"] = "Authorise"
    send_button["command"] = lambda: process_nickname(input_field, root, main_label, some_queue)
    send_button.pack(side="left")

    input_frame.pack(padx=10,pady=10)
    root.bind('<Control-c>', lambda event: root.destroy())
    root.mainloop()
