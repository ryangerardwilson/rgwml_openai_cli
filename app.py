from openai import OpenAI
import json
import os
import sys
import time

def find_config_file(filename, search_paths):
    for path in search_paths:
        full_path = os.path.join(path, filename)
        print(f"Checking path: {full_path}") 
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
    print(f"Configuration file '{config_filename}' not found in search paths.")
    sys.exit(1)

# Load the configuration file
with open(config_path, 'r') as file:
    config = json.load(file)

# Extract the OpenAI API key
api_key = config.get("open_ai_key")
client = OpenAI(api_key=api_key)

def get_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    return response

def main():
    if len(sys.argv) < 2:
        print("Usage: python openai_cli.py <prompt>")
        return

    prompt = " ".join(sys.argv[1:])
    print(f"Prompt: {prompt}\n")

    response = get_response(prompt)

    for chunk in response:
        if 'choices' in chunk and 'delta' in chunk.choices[0]:
            content = chunk.choices[0].delta.get('content', '')
            print(content, end='', flush=True)
            time.sleep(0.02)

    print("\n")

if __name__ == "__main__":
    main()

