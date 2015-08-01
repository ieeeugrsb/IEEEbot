IEEEbot
=======

Karma bot for Telegram groups. Done for IEEE Student Branch of Granada

Installation
------------

```
cd IEEEbot
pip install .
```

To run the software you have to define its Telegram API token in 
```IEEEBOT_TOKEN``` environment variable. You can obtain a token from 
```@BotFather``` Telegram bot.

Additionally, ```OPENSHIFT_DATA_DIR``` must be defined with SQLite database
folder path.

The program can run in polling mode calling ```ieeebot.py``` or in web-app mode
calling ```flaskapp.py```.
