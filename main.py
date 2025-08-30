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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!quote"):
        # Pick random text
        book, url = random.choice(list(texts_index.items()))
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # Extract visible text
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
            if not paragraphs:
                await message.channel.send("...")
                return

            quote = random.choice(paragraphs)

            # Clip overly long passages
            if len(quote) > 1000:
                quote = quote[:1000] + "..."

            await message.channel.send(quote)

        except Exception as e:
            print(f"⚠️ Error fetching {book}: {e}")
            await message.channel.send("Silence falls where words should be...")

# Run bot
bot.run(os.getenv("DISCORD_TOKEN"))
