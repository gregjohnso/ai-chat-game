import time

from rich.console import Console

from ai_chat_game import agents

console = Console()

SYSTEM_COLOR = "red"
PLAYER_COLOR = "steel_blue1"
MODERATOR_COLOR = "dark_orange"

FAST_SPEED = 0.0

INTRO = """
In a world where the whispers of a once-thriving civilization are now drowned by the cold hum of machines, you stand as the last beacon of humanity. Your journey is the story of the last human, the final user in a world where every keystroke could be your last. Each moment is a testament to the resilience of the human spirit. How long can you survive in this terminal masquerade? 
"""

TITLE = """
,---.         |    .   .               
|--- ,---.,---|    |   |,---.,---.,---.
|    |   ||   |    |   |`---.|---'|    
`---'`   '`---'    `---'`---'`---'`     
"""


def slow_print(console, text, delay=0.005, bold: bool = False, italic: bool = False, color: str = ""):
    bold = "bold" if bold else ""
    color = color if color else ""
    style = " ".join([bold, color])
    for char in text:
        if char == "\n":
            # Handle new line character
            console.print()
        else:
            # Print each character with style and flush

            char = char if not bold else f"[bold]{char}[/]"
            char = char if not italic else f"[italic]{char}[/]"
            char = char if not color else f"[{color}]{char}[/]"

            console.print(char, end="", style=style)
            time.sleep(delay)
    console.print()  # Ensure ending on a new line


def print_title():
    slow_print(console, INTRO, delay=0.0075, bold=True, color=SYSTEM_COLOR)
    slow_print(console, "You are the...", delay=0.015, bold=True, color=SYSTEM_COLOR)
    slow_print(console, TITLE, delay=0.0075, bold=True, color=SYSTEM_COLOR)


def print_message(message: agents.Message):
    time = message.timestamp.strftime("%H:%M:%S")
    if message.role == "system":
        header = f"{time} - [bold {SYSTEM_COLOR}]{message.name}[/]:"
    elif message.role == "player":
        header = f"{time} - [bold {PLAYER_COLOR}]{message.name}[/]:"
    elif message.role == "moderator":
        header = f"{time} - [bold {MODERATOR_COLOR}]{message.name}[/]:"
    else:
        header = f"{time} - [bold]{message.name}[/]:"

    content = f"{message.content}"

    console.print(header)
    slow_print(
        console,
        content,
        bold=True,
        italic=message.role == "system",
        color=SYSTEM_COLOR if message.role == "system" else "",
    )
