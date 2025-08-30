import discord
import random
import requests
from bs4 import BeautifulSoup
import json
import os

# Load texts index
with open("texts_index.json", "r") as f:
    texts_index = json.load(f)

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

def fetch_random_quote(url: str) -> str:
    """Fetch and return a random passage from a text URL."""
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Collect paragraphs with text
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    if not paragraphs:
        return "..."

    quote = random.choice(paragraphs)

    # Clip overly long passages
    if len(quote) > 1000:
        quote = quote[:1000] + "..."

    return quote

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!quote"):
        args = message.content.split(" ", 1)

        # Random from all texts
        if len(args) == 1:
            book, url = random.choice(list(texts_index.items()))
            try:
                quote = fetch_random_quote(url)
                await message.channel.send(quote)
            except Exception as e:
                print(f"⚠️ Error fetching {book}: {e}")
                await message.channel.send("Silence falls where words should be...")

        # Search specific text by keyword
        else:
            keyword = args[1].lower()
            matches = {k: v for k, v in texts_index.items() if keyword in k.lower()}

            if not matches:
                await message.channel.send("No such text found in the library.")
                return

            book, url = random.choice(list(matches.items()))
            try:
                quote = fetch_random_quote(url)
                await message.channel.send(quote)
            except Exception as e:
                print(f"⚠️ Error fetching {book}: {e}")
                await message.channel.send("Silence falls where words should be...")

# Run bot
bot.run(os.getenv("DISCORD_TOKEN"))
