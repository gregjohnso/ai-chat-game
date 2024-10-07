"""
Test that we can access the OpenAI API.
"""

from ai_chat_game.secrets import load_secrets

from openai import OpenAI


def test_openai_api_access():
    load_secrets()

    # test that we can access the OpenAI API
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, world!"}],
    )

    # This _should_ throw an error if the API key is not valid
    print(response)
