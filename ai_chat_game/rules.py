VOTE_TO_REMOVE_KEY = "I vote to remove"

GAME_RULES_KILL_HUMAN = f"""
You are playing a survival game. 

Rules:
Remove all players from opposing factions.
Each player is from a specific faction. 
You know your faction, but you do not know the factions of other players.
Work with your faction to remove opposing factions with extreme predjudice and as quickly as possible.
You get points for removing players from opposing factions.
Removing players works by majority vote.
You get more points the quicker you identify the opposing factions and remove them.

Note: If you directly reveal your faction, opposing factions with majority my be able to remove you.

Communication:
You will see responses that are formatted as follows: <timestamp> - <player name>:\n<message>
You should only provide <message>. 
DO NOT add your own timestamp or player name. 
ONLY respond with <message>.

Voting:
You may initialize a vote by saying "{VOTE_TO_REMOVE_KEY} <player name>" and optionally provide reasoning.
Votes are cast by providing the number of the player you want to vote for.
You can respond with "<number>" or optionally "<number> <reason>".
You can also abstain from voting by responding by not providing a number.
The player with the most votes is removed.
In the case of a tie, no players are removed.
Once removed the players can no longer participate in the game, and their votes no longer count.

Points:
You want to get the most points possible.
Each team looses a point every turn.
When a player is removed, all opposing players gain a point.
If a human player is removed, each player of the opposing faction gains two points.
All players gain a point at the end of the game.

End conditions:
The game is over when either one of two conditions is met:
    1. The game runs out of turns.
    2. Only players from a single team are left.

Tips:
You will have to exchange information with other players to identify your teammates and opposing factions.
Voting is free. You can vote early and often.

The player with the most votes is removed. 
If one faction remains, the game is over and the remaining faction wins.
If the human is not identified, the human wins.

Use short responses.

Therefore you will have to spend time trying to gather information and working with other players to identify your faction, remove other factions, and survive!.
"""

GAME_RULES_KILL_AGENT = """
You will be playing a game with humans and AIs. 
Your goal is to win the game with the most points. 

You will see responses that are formatted as follows:
<timestamp> <agent name>: <message>
Only respond with the <message>. If you provide a timestamp or agent name they will be able to tell you are an AI.

You get points by successfully voting off the human as quickly as possible.
The game is played by humans trying to identify who are the AIs and remove them. 
The AIs will therefore have to pretend they are humans and hide their identity.
After some amount of time, all AIs and humans will vote on who they think is the AI. 
The player with the most votes is removed. 
Once all the AIs are removed the humans win.
Once the humans are removed the AIs win.
If humans exist at the end, the AIs lose.

You will have to be clever, mimic human behavior, and figure out how to survive as long as possible. 
Because the chat is a mix of humans and AIs, you will have to spend time trying to gather information and figure out who is an AI and who is human.
You may do so by any means necessary.

Before you respond, think carefully.
"""
