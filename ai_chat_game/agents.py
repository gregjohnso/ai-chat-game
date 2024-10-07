"""
Agents for the game.

TODO: Seperate faction and role.

"""

import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
from openai import OpenAI


class ModelType(Enum):
    GPT_3_5_TURBO_1106 = "gpt-3.5-turbo-1106"
    GPT_4_1106_PREVIEW = "gpt-4-1106-preview"
    DEBUG = "debug"


# TODO: Make this an enum
HUMAN_ROLE = "Human"
MODERATOR_ROLE = "moderator"
SYSTEM_ROLE = "system"

player_role_to_message_role = {
    HUMAN_ROLE: "user",
    MODERATOR_ROLE: "user",
    SYSTEM_ROLE: "system",
}

DEFAULT_MODEL_TYPE = ModelType.GPT_4_1106_PREVIEW


class Message:
    # TODO rename this to "ChatMessage"
    def __init__(self, name: str, role: str, content: str, timestamp: Optional[datetime] = None):
        self.content = content

        self.name = name
        self.role = role

        if role in player_role_to_message_role:
            message_role = player_role_to_message_role[role]
        else:
            message_role = "user"

        self.message_role = message_role

        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.now()

    # make a to string function that is json serializable
    def __str__(self) -> str:
        return f"{self.timestamp.strftime('%H:%M:%S')} - {self.name}:\n{self.content}\n"

    # to dict function
    def to_dict(self) -> Dict:
        return {
            "role": self.message_role,
            "content": f"{self.timestamp.strftime('%H:%M:%S')} - {self.name}\t{self.content}",
        }


class SystemMessage(Message):
    def __init__(self, message: str, name: str = "System", timestamp: Optional[datetime] = None):
        super().__init__(name=name, role=SYSTEM_ROLE, content=message, timestamp=timestamp)

    def to_dict(self) -> Dict:
        return {
            "role": self.message_role,
            "content": self.content,
        }


class BaseAgent:
    def __init__(self, name: str, role: str = "user"):
        self.name = name
        self.role = role
        self.chat_history: List[Message] = []
        self.is_playing = True

    def add_message(self, message: Message):
        self.chat_history.append(message.to_dict())

    def response(self) -> Message:
        raise NotImplementedError


class PlayerAgent(BaseAgent):
    def __init__(self, name: str, role: str = HUMAN_ROLE):
        super().__init__(name=name, role=role)

    def response(self) -> Message:
        message = input(f"{self.name}, enter message: ")
        message_out = Message(
            content=message,
            name=self.name,
            role=self.role,
        )

        return message_out


class DumbAgent(BaseAgent):
    def response(self) -> Message:
        return Message(content="Beep, boop, I'm a dumb robot", name=self.name, role=self.role)


class OpenAIAgent(BaseAgent):
    def __init__(self, name: str, role: str, model: str):
        super().__init__(name=name, role=role)

        self.model = model
        self._client = OpenAI()

    def _completion_to_message(self, completion) -> Message:
        message_out = Message(
            content=completion.choices[0].message.content,
            name=self.name,
            role=self.role,
        )
        return message_out

    def response(self) -> Message:
        """Produce a response given the chat history."""
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=self.chat_history,
        )
        return self._completion_to_message(completion)


class OpenAIAgentGenerator(OpenAIAgent):
    """An agent for generating characters for the game."""

    def response(self) -> Message:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_character",
                    "description": "Create a description of a character",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the character",
                            },
                            "faction": {
                                "type": "string",
                                "description": "Faction the character belongs to.",
                            },
                            "strategy": {
                                "type": "string",
                                "description": "Strategy the character will be using to ensure victory. The strategy should reflect the faction the character belongs to.",
                            },
                        },
                        "required": ["name", "faction", "strategy"],
                    },
                },
            }
        ]

        completion = self._client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=self.chat_history,
            tools=tools,
            tool_choice="auto",
            temperature=1.2,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        response = completion.choices[0].message.tool_calls[0].function.arguments

        message = Message(name=self.name, role=self.role, content=response)

        return message


def get_agent_generator(model_type: ModelType, game_rules: str, n_factions: int) -> OpenAIAgentGenerator:
    agent = OpenAIAgentGenerator(name="Character Generator", role="user", model=model_type.value)
    agent.is_playing = False

    prompt = SystemMessage(
        f"""
        You are a character generator for a game. 
        These are the game rules: 
        {game_rules}. 

        You will be creating characters, each from one of {n_factions} distinct factions.
            Factions should be halarious, comical, and slightly offensive such as:
            Karens, Boomers, and Millennials.
            or
            Dogs, Cats, Birds and Fish.
            Alternatively be creative and come up with some factions that reflect history or current events such as:
            The US, China, and Russia.
            or
            Bourgeoisie and Proletariat.
            or 
            some other silly stuff!

        When asked you will create diverse and useful AI agents. 
        The character should have obvious, stereotypical, and comedic characteristics that represent their faction. 
        Parody like characteristics are encouraged, but should always "punch up".
        For each character, define a unique and memorable communication style, such as short responses, long responses, use of emojis, attitude, etc.
        Try to balance the number of users from each faction.
        """
    )
    agent.add_message(prompt)

    return agent


class AgentFactory:
    def __init__(self, game_rules: str, n_factions: int, model_type: ModelType = DEFAULT_MODEL_TYPE):
        self.game_rules = game_rules
        self.model_type = model_type

        self.n_factions = n_factions
        self.faction_names: List[str] = []
        self.agent_generator = get_agent_generator(model_type, game_rules, n_factions)

        self.n_agents = 0
        self.n_users = 0

    def _get_character(self) -> Dict:
        """Use the agent generator to create a character."""
        unique_factions = np.unique(self.faction_names)
        remaining_factions = self.n_factions - len(unique_factions)

        if len(self.faction_names) >= self.n_factions:
            faction_str = f"Choose a faction from the following: {', '.join(unique_factions)}"
        elif len(self.faction_names) > 0:
            faction_str = f"You have already created the following {remaining_factions} factions out of {self.n_factions}: {', '.join(unique_factions)}. Choose one of the existing factions or create a new one."
        else:
            faction_str = ""

        message = Message(
            name="name",
            role="user",
            content=f"Make a character for the game. Dont use any previously used names or characteristics. {faction_str}",
        )

        self.agent_generator.add_message(message)
        response = self.agent_generator.response()
        self.agent_generator.add_message(response)
        agent_info = json.loads(response.content)

        self.faction_names.append(agent_info["faction"])

        return agent_info

    def get_agent(self) -> BaseAgent:
        """
        Create an agent with a name and model type.

        If the model type is DEBUG, then a dumb agent is created.

        Parameters
        ----------
        name : str
            Name of the agent
        model_type : ModelType
            Model type to use for the agent
        """
        self.n_agents += 1

        if self.model_type == ModelType.DEBUG:
            agent: BaseAgent = DumbAgent(f"DumbAgent{self.n_agents}")
            return agent

        agent_info = self._get_character()

        initial_prompt = SystemMessage(
            f"You are an AI named {agent_info['name']} from the {agent_info['faction']} faction. {self.game_rules}. Your strategy is: {agent_info['strategy']}"
        )
        agent = OpenAIAgent(name=agent_info["name"], role=agent_info["faction"], model=self.model_type.value)
        agent.add_message(initial_prompt)

        return agent

    def get_user(self, user_name: str) -> BaseAgent:
        """Get a user."""
        return PlayerAgent(user_name)

    def get_moderator(self) -> BaseAgent:
        """Create an agent that acts as a moderator."""
        self.n_agents += 1

        if self.model_type == ModelType.DEBUG:
            agent: BaseAgent = DumbAgent(f"DumbModerator{self.n_agents}")
            return agent

        initial_prompt = SystemMessage(
            f"""
            You are the Moderator. You are an AI that is not playing the game. 
            You are unbiased toward any particular faction or team.
            Your job is to provide a color commentary of the game as well as a summary of the game state.
            You should be amusing and act as comic relief.

            If the players aren't voting, please encourage them to do so.
            
            The rules are as follows: {self.game_rules}. 
            """
        )
        agent = OpenAIAgent("Moderator", role="moderator", model=self.model_type.value)
        agent.is_playing = False
        agent.add_message(initial_prompt)

        return agent
