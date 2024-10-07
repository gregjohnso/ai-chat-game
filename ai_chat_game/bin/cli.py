import fire

from ai_chat_game import main
from ai_chat_game.secrets import load_secrets

load_secrets()


def cli():
    fire.Fire(main.main)
