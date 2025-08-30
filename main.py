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

# Helper to load passages
def load_passages(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

# Preload all texts
books = {title: load_passages(path) for title, path in text_index.items()}

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
        book = random.choice(list(books.keys()))
        passage = random.choice(books[book])
        await message.channel.send(f"📖 **{book}**\n{passage}")

    # Specific book
    elif content.startswith("!quote "):
        query = content.replace("!quote ", "").strip().lower()
        for book in books:
            if query in book.lower():
                passage = random.choice(books[book])
                await message.channel.send(f"📖 **{book}**\n{passage}")
                return
        await message.channel.send("❌ Book not found.")

    # Search all books
    elif content.startswith("!search "):
        query = content.replace("!search ", "").strip().lower()
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
