import discord
import os
import json
import random
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Load archive index (title → url)
with open("texts_index.json", "r", encoding="utf-8") as f:
    text_index = json.load(f)

# Cache to avoid refetching
cache = {}

def fetch_passages(title, url):
    if title in cache:
        return cache[title]

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = [p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip()]
    cache[title] = paragraphs
    return paragraphs

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()

    # Random passage from any book
    if content == "!quote":
        title, url = random.choice(list(text_index.items()))
        passages = fetch_passages(title, url)
        passage = random.choice(passages)
        await message.channel.send(passage)

    # Specific book
    elif content.startswith("!quote "):
        query = content.replace("!quote ", "").strip().lower()
        for title, url in text_index.items():
            if query in title.lower():
                passages = fetch_passages(title, url)
                passage = random.choice(passages)
                await message.channel.send(passage)
                return
        await message.channel.send("No matching text found.")

    # Search across all texts
    elif content.startswith("!search "):
        query = content.replace("!search ", "").strip().lower()
        results = []
        for title, url in text_index.items():
            passages = fetch_passages(title, url)
            matches = [p for p in passages if query in p.lower()]
            if matches:
                results.append(random.choice(matches))
        if results:
            await message.channel.send("\n\n".join(results[:5]))
        else:
            await message.channel.send("No results found.")

client.run(TOKEN)
