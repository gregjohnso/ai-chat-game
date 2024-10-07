"""Top-level package for ai_chat_game."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ai-chat-game")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "Gregory Johnson"
__email__ = "gregjohnso@gmail.com"
