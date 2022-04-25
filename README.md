# Secret chat.

Desktop application which uses asynchronous socket connection to send and get messages.

## Description

The project has file **main.py**  as an entrypoint of the project. 

## Prerequisites
To start and run this application have to create a virtual environment and installs the project dependencies into the environment. Run the following command from the base directory of the project:
1. Create virtual environment:
    ```bash
    python3.8 -m venv env
    ```
2. Activate the virtualenv:
    ```bash
    source env/bin/activate
    ```
3. Install dependencies:
    ```bash 
    pip install -r requirements.txt
    ```
4. Set ENV variables (_the example shows the default values_):
    ```bash
    export HOST=minechat.dvmn.org
    export SENDER_PORT=5050
    export READER_PORT=5000
    ```
4. Create files for saving messages and user infomation:
    ```bash
    touch token.txt history.txt
    ```

5. Run the application:
    ```bash
    python3 main.py
    ```

##### Description
All messages are saved in a file histroy.txt, which will be displayed when the program is restarted. The file token.txt stores the nickname and access token received from the server. 