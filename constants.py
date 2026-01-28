import os

from dotenv import load_dotenv

# Загружает переменные из .env в окружение
load_dotenv()

# get token using BotFather
TOKEN = os.getenv("TG_TOKEN")

CONTINUE_GAME, FINISH_GAME = range(2)

FREE_SPACE: str = "."
CROSS: str = "X"
ZERO: str = "O"

HELP_TURN_MESSAGE = "{sign} (your) turn! Please, put {sign} to the free place"
END_MESSAGE = "The {sign} won!"

WIDTH = 3

DEFAULT_STATE = [ [FREE_SPACE for _ in range(WIDTH) ] for _ in range(WIDTH) ]
