import discord
import os
import json
import random

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Load text index
with open("texts/texts_index.json", "r", encoding="utf-8") as f:
    text_index = json.load(f)

# Helper to load book passages
def load_passages(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

# Preload all texts into memory
books = {title: load_passages(path) for title, path in text_index.items()}

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Random passage from any book
    if message.content.strip() == "!quote":
        book = random.choice(list(books.keys()))
        passage = random.choice(books[book])
        await message.channel.send(f"📖 **{book}**\n{passage}")

    # Random passage from a specific book
    elif message.content.startswith("!quote "):
        query = message.content.replace("!quote ", "").strip().lower()
        for book in books:
            if query in book.lower():
                passage = random.choice(books[book])
                await message.channel.send(f"📖 **{book}**\n{passage}")
                return
        await message.channel.send("❌ Book not found. Try again!")

    # Search text
    elif message.content.startswith("!search "):
        query = message.content.replace("!search ", "").strip().lower()
        results = []
        for book, lines in books.items():
            matches = [line for line in lines if query in line.lower()]
            if matches:
                results.append(f"**{book}**: {random.choice(matches)}")
        if results:
            await message.channel.send("\n\n".join(results[:5]))
        else:
            await message.channel.send("❌ No results found.")

client.run(TOKEN)
