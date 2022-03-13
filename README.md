# Secret chat.

Desktop application which uses asynchronous socket connection to send and get messages.

## Description

The project has file **main.py**  as an entrypoint of the project. 

Before run the application have to install libraries from _requirements.txt_ files and sent environment variables.

##### ENV variables
- HOST _(by default "minechat.dvmn.org")_
- SENDER_PORT _(by default 5050)_
- READER_PORT _(by default 5000)_

Run the application:

```bash
python3 main.py
```

##### Files
The retreived messages (history.txt) and user information (token.txt) will be saved in running directory.
