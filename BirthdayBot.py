import json
import os
from telethon import TelegramClient, events

api_id = 24466492
api_hash = 'b6a4612c17ab6b4aae5cb875caf44b13'
bot_token = '7407378272:AAEI69bXQUEaeMvAo6WfKsa39E5dZNCIVks'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Absolute path to save the JSON file
data_dir = r'data'
os.makedirs(data_dir, exist_ok=True)
json_file_path = os.path.join(data_dir, 'gift_ideas.json')

# Load gift ideas from a JSON file
def load_gift_ideas():
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Error loading gift ideas: {e}")
        return {}

# Save gift ideas to a JSON file
def save_gift_ideas(gift_ideas):
    try:
        with open(json_file_path, 'w') as file:
            json.dump(gift_ideas, file, indent=4)
    except Exception as e:
        print(f"Error saving gift ideas: {e}")

gift_ideas = load_gift_ideas()

async def handle_start(event):
    await event.respond('Hi, I am the Birthday-gift-bot! You can save and retrieve gift ideas by using /add, /get, /remove, and /listall commands.')

async def handle_add(event):
    try:
        user_id = str(event.message.peer_id.user_id)
        _, name, *idea = event.message.text.split()
        idea = ' '.join(idea)
        
        if user_id not in gift_ideas:
            gift_ideas[user_id] = {}
        
        if name in gift_ideas[user_id]:
            gift_ideas[user_id][name].append(idea)
        else:
            gift_ideas[user_id][name] = [idea]
        
        save_gift_ideas(gift_ideas)
        await event.respond(f"Gift idea added for {name}.")
    except ValueError:
        await event.respond("Usage: /add <name> <gift idea>")

async def handle_get(event):
    try:
        user_id = str(event.message.peer_id.user_id)
        _, name = event.message.text.split()
        
        if user_id in gift_ideas and name in gift_ideas[user_id]:
            ideas = '\n'.join(gift_ideas[user_id][name])
            await event.respond(f"Gift ideas for {name}:\n{ideas}")
        else:
            await event.respond(f"No gift ideas found for {name}.")
    except ValueError:
        await event.respond("Usage: /get <name>")

async def handle_remove(event):
    try:
        user_id = str(event.message.peer_id.user_id)
        _, name, *idea = event.message.text.split()
        idea = ' '.join(idea) if idea else None
        
        if user_id in gift_ideas and name in gift_ideas[user_id]:
            if idea:
                if idea in gift_ideas[user_id][name]:
                    gift_ideas[user_id][name].remove(idea)
                    if not gift_ideas[user_id][name]:  # Remove the name if no ideas are left
                        del gift_ideas[user_id][name]
                    save_gift_ideas(gift_ideas)
                    await event.respond(f"Removed gift idea for {name}.")
                else:
                    await event.respond(f"Gift idea not found for {name}.")
            else:
                del gift_ideas[user_id][name]
                save_gift_ideas(gift_ideas)
                await event.respond(f"Removed all gift ideas for {name}.")
        else:
            await event.respond(f"No gift ideas found for {name}.")
    except ValueError:
        await event.respond("Usage: /remove <name> [<gift idea>]")

async def handle_listall(event):
    if not gift_ideas:
        await event.respond("No gift ideas found.")
        return
    
    response = ""
    for user_id, names in gift_ideas.items():
        for name, ideas in names.items():
            ideas_str = '\n'.join(f"  - {idea}" for idea in ideas)
            response += f"{name}:\n{ideas_str}\n\n"

    await event.respond(response if response else "No gift ideas found.")

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await handle_start(event)

@bot.on(events.NewMessage(pattern='/add'))
async def add_handler(event):
    await handle_add(event)

@bot.on(events.NewMessage(pattern='/get'))
async def get_handler(event):
    await handle_get(event)

@bot.on(events.NewMessage(pattern='/remove'))
async def remove_handler(event):
    await handle_remove(event)

@bot.on(events.NewMessage(pattern='/listall'))
async def listall_handler(event):
    await handle_listall(event)

@bot.on(events.NewMessage())
async def default_handler(event):
    if event.message.text and not event.message.text.startswith('/'):
        await event.respond("I don't know what to do with this. Use /add, /get, /remove, or /listall commands.")

# Print the JSON file path for debugging
print(f"JSON file path: {json_file_path}")

bot.run_until_disconnected()
