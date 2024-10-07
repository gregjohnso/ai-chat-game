import random
from enum import Enum
from typing import List, Tuple

import numpy as np
from rich.prompt import Prompt

from ai_chat_game import agents, display
from ai_chat_game.agents import BaseAgent, Message, SystemMessage
from ai_chat_game.rules import GAME_RULES_KILL_HUMAN, VOTE_TO_REMOVE_KEY

from .display import print_title

DEFAULT_N_FACTIONS = 3
DEFAULT_N_AGENTS = 9
DEFAULT_N_USERS = 1


class GameMode(Enum):
    DEFAULT = "default"
    DEBUG = "debug"


DEFAULT_GAME_MODE = GameMode.DEFAULT

SYSTEM_NAME = "System"


class SimpleChatGame:
    def __init__(self, players: List[BaseAgent], game_rules: str, n_rounds: int = 10):
        self.players = players
        self.game_rules = game_rules
        self.scoreboard = {player.name: 0 for player in players}
        self.n_rounds = n_rounds

    def send_message(self, message: Message):
        """Send an agent message to all players."""
        for player in self.players:
            player.add_message(message)

        display.print_message(message)

    def send_system_message(self, message: str):
        """Send a system message to all players."""
        system_message = SystemMessage(name=SYSTEM_NAME, message=message)
        self.send_message(system_message)

    def vote_mode(self):
        # get the list of players
        player_dict = {}
        votes_dict = {}
        counter = 1
        command_str = ""
        for player in self.players:
            if not player.is_playing:
                continue

            player_dict[str(counter)] = player.name
            votes_dict[player.name] = 0

            command_str += f"press {counter} for {player.name}\n"
            counter += 1

        self.send_system_message(
            "Voting mode has been initialized.\n"
            "All players must vote with a numerical response.\n"
            f"{command_str}\n"
            "Let the voting commence."
        )

        for player in self.players:
            if not player.is_playing:
                continue

            message = player.response()

            self.send_message(message=message)

            first_part = message.content.split(" ")[0]

            if first_part in list(player_dict.keys()):
                votes_dict[player_dict[first_part]] += 1
                self.send_system_message(
                    f"{player.name} voted for {player_dict[first_part]}\n"
                    f"There are currently {votes_dict[player_dict[first_part]]} votes for {player_dict[first_part]}"
                )
            else:
                self.send_system_message(f"No number prefix detected from {player.name}. No vote registered.")

        # find all players with the max votes
        votes = np.array(list(votes_dict.values()))
        max_votes = np.max(votes)
        has_most_votes = votes == max_votes

        if np.sum(has_most_votes) == 1:
            player_ind = str(np.where(has_most_votes)[0][0] + 1)

            kick_player_name: str = player_dict[player_ind]
            # get the player object
            kick_player: BaseAgent = [player for player in self.players if player.name == kick_player_name][0]

            kick_player.is_playing = False

            remaining_factions = np.unique([player.role for player in self.players if player.is_playing])

            removed_player_message = (
                f"{kick_player.name} from the {kick_player.role} faction has been removed with {max_votes} votes.\n"
                f"Remaining factions are {', '.join(remaining_factions)}."
            )

        else:
            removed_player_message = "Vote resulted in a tie: No players have been removed"

        self.send_system_message(f"Voting has concluded.\n{removed_player_message}")

    def play_round(self, round_number: int):
        n_rounds_left = self.n_rounds - round_number
        remaining_factions = np.unique([player.role for player in self.players if player.is_playing])
        remaining_players = [player.name for player in self.players if player.is_playing]

        self.send_system_message(
            f"There are {n_rounds_left} turns left.\n"
            f"Remaining factions are {', '.join(remaining_factions)}.\n"
            f"Remaining players are {', '.join(remaining_players)}."
        )

        for player in self.players:
            if not player.is_playing and (player.role != agents.HUMAN_ROLE and player.role != agents.MODERATOR_ROLE):
                continue

            message = player.response()

            self.send_message(message=message)

            if VOTE_TO_REMOVE_KEY in message.content:
                if player.is_playing:
                    self.vote_mode()
                else:
                    self.send_system_message(
                        f"{player.name} has initialized a vote but they are inelligable. Moving on."
                    )

    def main_loop(self):
        for i in range(self.n_rounds):
            self.play_round(i)

        # get all the human players
        human_players = [player for player in self.players if player.role == agents.HUMAN_ROLE and player.is_playing]
        if len(human_players) == 0:
            self.send_system_message("No human players remain. The AI wins!")
            return
        else:
            self.send_system_message(
                f"Congratulations {', '.join([player.name for player in human_players])}. The humans survive another day!"
            )


def _get_settings(game_mode: GameMode) -> Tuple[List[str], int, int, agents.ModelType]:
    if game_mode == GameMode.DEBUG:
        n_agents = 3
        n_factions = 1
        user_names = []
        model_type = agents.ModelType.DEBUG
    else:
        n_factions = Prompt.ask(f"How many factions? (default={DEFAULT_N_FACTIONS})", default=DEFAULT_N_FACTIONS)
        n_factions = int(n_factions)

        n_agents = Prompt.ask(f"How many AI agents? (default={DEFAULT_N_AGENTS})", default=DEFAULT_N_AGENTS)
        n_agents = int(n_agents)

        n_users = Prompt.ask(f"How many human players? (default={DEFAULT_N_USERS})", default=DEFAULT_N_USERS)
        n_users = int(n_users)

        user_names = []
        for i in range(n_users):
            if i == 0:
                user_suffix = ""
            else:
                user_suffix = f"_{i + 1}"
            _user_name = f"User{user_suffix}"

            user_name = Prompt.ask(f"{_user_name}, what is your name? (default={_user_name})", default=_user_name)

            user_names.append(user_name)

        model_type = agents.ModelType.GPT_4_1106_PREVIEW

    return user_names, n_agents, n_factions, model_type


def _get_players(
    user_names: List[str],
    n_agents: int,
    n_factions: int,
    game_rules: str,
    model_type: agents.ModelType = agents.ModelType.GPT_4_1106_PREVIEW,
) -> List[BaseAgent]:
    player_list = []

    agent_factory = agents.AgentFactory(game_rules=game_rules, n_factions=n_factions, model_type=model_type)

    for user_name in user_names:
        player_list.append(agent_factory.get_user(user_name))

    for _ in range(n_agents):
        player_list.append(agent_factory.get_agent())

    random.shuffle(player_list)

    moderator = agent_factory.get_moderator()
    player_list.append(moderator)

    return player_list


def main(game_mode="default", game_rules: str = GAME_RULES_KILL_HUMAN):
    try:
        game_mode = GameMode(game_mode)
    except KeyError as e:
        raise ValueError(f"game_mode must be one of {list(GameMode)}") from e

    print_title()

    user_names, n_agents, n_factions, model_type = _get_settings(game_mode=game_mode)

    # use rich's loading spinner
    with display.console.status("[bold green]Loading game..."):
        players = _get_players(
            user_names=user_names,
            n_agents=n_agents,
            n_factions=n_factions,
            game_rules=game_rules,
            model_type=model_type,
        )

    game = SimpleChatGame(players=players, game_rules=game_rules)
    game.main_loop()
