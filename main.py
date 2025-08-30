import discord
import os
import random
import requests
from bs4 import BeautifulSoup
import json

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Load the expanded texts index
with open("texts_index.json", "r", encoding="utf-8") as f:
    texts_index = json.load(f)

def fetch_random_quote(url):
    """Fetches a random passage from a text URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract paragraphs or other text containers
        paragraphs = soup.find_all(["p", "div", "blockquote", "span"])
        clean_passages = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 100]

        if not clean_passages:
            return "⚠️ No readable passages found."

        quote = random.choice(clean_passages)

        # Clip very long passages
        if len(quote) > 1000:
            quote = quote[:1000] + "..."

        return quote
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return "⚠️ Could not retrieve a passage at this time."

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!quote"):
        args = message.content.split(" ", 1)

        # Random passage from any text
        if len(args) == 1:
            book = random.choice(texts_index)
            quote = fetch_random_quote(book["url"])
            await message.channel.send(quote)
            return

        # Specific text search by keyword
        keyword = args[1].lower()
        matches = [
            entry for entry in texts_index
            if keyword in entry["title"].lower() or keyword in " ".join(entry["aliases"]).lower()
        ]

        if not matches:
            await message.channel.send("⚠️ No matching text found.")
            return

        book = random.choice(matches)
        quote = fetch_random_quote(book["url"])
        await message.channel.send(quote)

client.run(TOKEN)
