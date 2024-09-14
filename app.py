#!/usr/bin/env python3
from openai import OpenAI
import json
import os
import sys
import subprocess

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
client = OpenAI(api_key=api_key)

def get_response(conversation):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            stream=True
        )
        final_response = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                final_response += delta
                print("\033[92m" + delta + "\033[0m", end="", flush=True)

        return final_response
    except Exception as e:
        print("\033[91m" + f"Error while getting response: {e}" + "\033[0m")
        sys.exit(1)

def main():
    # Build the initial conversation history
    conversation = [{"role": "system", "content": "You are a helpful assistant."}]
    print()

    temp_filename = "/tmp/vim_prompt.txt"
    
    # Create the temp file to ensure it exists
    with open(temp_filename, 'w') as temp_file:
        temp_file.write("")
        
    while True:
        prompt = input("\033[94mPrompt: \033[0m").strip()
        print()

        if prompt.lower() == 'vi':
            subprocess.call(['vim', temp_filename])
            with open(temp_filename, 'r') as file:
                prompt = file.read().strip()
            if not prompt:
                print("\033[91mNo prompt entered in Vim. Please try again.\033[0m")
                continue
            print(f"\033[94m{prompt}\033[0m")
            print()
        elif prompt.lower() == 'n':
            conversation = [{"role": "system", "content": "You are a helpful assistant."}]
            print("\033[92mNew conversation started.\033[0m")
            continue

        if not prompt:
            print("\033[91mNo prompt entered. Please try again.\033[0m")
            continue

        conversation.append({"role": "user", "content": prompt})
        response = get_response(conversation)
        # Convert the response to a string and append it to the conversation
        conversation.append({"role": "assistant", "content": str(response)})
        print()
        print()

if __name__ == "__main__":
    main()
    print()

