from openai import AsyncOpenAI
import asyncio
from openai_streaming import process_response
from typing import AsyncGenerator, List, Dict
import json
import os
import sys

def find_config_file(filename, search_paths):
    for path in search_paths:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path):
            return full_path
    return None

# Define the possible locations for the config file
search_paths = [
    os.path.expanduser('~/Documents/'),
]

# Find the config file
config_filename = 'rgwml.config'
config_path = find_config_file(config_filename, search_paths)

if not config_path:
    sys.exit(1)

# Load the configuration file
with open(config_path, 'r') as file:
    config = json.load(file)

# Extract the OpenAI API key
api_key = config.get("open_ai_key")
client = AsyncOpenAI(api_key=api_key)

# Define a content handler
async def content_handler(content: AsyncGenerator[str, None]) -> str:
    response = ""
    async for token in content:
        response += token
        print("\033[92m" + token + "\033[0m", end="", flush=True)
    print()  # Print a newline at the end of the response for better readability
    return response

async def get_response(conversation: List[Dict[str, str]]) -> str:
    try:
        # Debugging: Print the conversation to ensure it's correct
        """
        print("Debug: Sending conversation to OpenAI API")
        for message in conversation:
            print(f"{message['role']}: {message['content']}")
        print("\n")
        """

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            stream=True
        )
        final_response = await process_response(response, content_handler)
        return final_response
    except Exception as e:
        print("\033[91m" + f"Error while getting response: {e}" + "\033[0m")
        sys.exit(1)

async def main():
    # Build the initial conversation history
    conversation = [{"role": "system", "content": "You are a helpful assistant."}]

    while True:
        prompt = input("\033[94mPrompt: \033[0m")
        print()
        conversation.append({"role": "user", "content": prompt})
        response = await get_response(conversation)
        # Convert the response to a string and append it to the conversation
        conversation.append({"role": "assistant", "content": str(response)})
        print()
        print()

if __name__ == "__main__":
    asyncio.run(main())
    print()

