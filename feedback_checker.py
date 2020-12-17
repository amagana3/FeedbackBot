# Author: Andrew Magana
# timezone_bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following GUILD:\n'
        f'{guild.name} (id: {guild.id})'
    )


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # pseudocode:
    # Problem: When someone adds a new link (soundcloud) or mp3 - we should check if that person has given feedback.
    # Solution:
    # To determine if there is feedback, look for previous messages within the channel.
    # In the beginning, we can assume any previous message is feedback,
    # otherwise we could look for keywords most feedback.
    # Or there could be a rule that if you leave feedback,
    # you should label it as "FEEDBACK" to a track for better visibility by the bot.

    print()

    print("Content:", message.content)
    print("Channel:", message.channel)
    print("Attachments: ", message.attachments)

    print("----")

    # Should be in feedback channel
    if message.channel.name == 'feedback':
        # For SoundCloud submissions.
        if 'soundcloud.com' in message.content:
            # See who posted their track.
            author_id = message.author.id
            counter = 0

            # Loop through last 100  messages
            async for m in message.channel.history(limit=200):
                # Check if user has given feedback before
                if m.author.id == author_id:
                    counter += 1

            # if they have submitted at least 2 messages, they're fine.
            if counter > 2:
                # TODO: We need to make sure that the messages don't contain links,
                #  or they could be spamming feedback submissions.
                return
            else:
                # Give user a warning.
                await message.channel.send(
                    "Excuse me! You must submit feedback to a track above you to receive feedback!")
        # For .mp3 or .wav submissions
        if any('.mp3' or '.wav' or '.mp4' in s for s in message.attachments):
            # See who posted their track.
            author_id = message.author.id
            counter = 0

            # Loop through last 100  messages
            async for m in message.channel.history(limit=200):
                # Check if user has given feedback before
                if m.author.id == author_id:
                    counter += 1

            # if they have submitted at least 2 messages, they're fine.
            if counter > 2:
                return
            else:
                # Give user a warning.
                await message.channel.send(
                    "Excuse me! You must submit feedback to a track above you to receive feedback!")


client.run(TOKEN)
