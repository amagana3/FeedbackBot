# Author: Andrew Magana
# feedback_checker.py
import os

import discord
from dotenv import load_dotenv
from typing import Optional, Any

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(f'{client.user} is connected to the following GUILD: {guild.name} (ID: {guild.id}')
    print()


@client.event
async def on_message(message):
    # The bot called, ignore.
    if message.author == client.user:
        return

    print("Content:", message.content)
    print("Channel:", message.channel)
    print("Attachments: ", message.attachments)
    print()

    # NEW pseudocode:
    # Problem: When someone wants feedback we should make sure they have given feedback to the previous feedback track.
    # Solution:
    # When someone submits a new feedback (Soundcloud link), check to see the previous user's feedback
    # See if current user (submitter) has given feedback to previous person
    # if they have, then we're good!
    # if they haven't, then we decline the feedback and tell them to give feedback to previous user.
    # Send them the message in context to give feedback.

    # Should be in feedback channel
    if message.channel.name == 'feedback':
        # Someone submitted feedback, check to see if they gave feedback to previous poster.
        if 'soundcloud.com' in message.content:
            if not await validate_feedback(message):
                await message.delete()
                await deny_feedback(message)

        # Someone wants to know what the last feedback is.
        if '.last' in message.content:
            last_feedback_info = await last_feedback(message)
            embed_var = discord.Embed(title="Last Feedback Request", description="By: " + last_feedback_info[0],
                                      color=0x00ff00)
            embed_var.add_field(name="Original Message", value=last_feedback_info[1], inline=False)
            embed_var.add_field(name="Link to Message", value=last_feedback_info[2], inline=False)
            await message.channel.send(embed=embed_var)


async def last_feedback(message) -> tuple:
    count = 0
    messages = await message.channel.history(limit=100).flatten()
    for m in messages:
        if "soundcloud.com" in m.content and count < 1:
            # Look for previous feedback
            count += 1
            return m.author.name, m.content, m.jump_url, m.author.id


async def previous_feedback(message) -> Optional[tuple[Any, Any, Any, Any, Any]]:
    count = 0
    messages = await message.channel.history(limit=100).flatten()
    for m in messages:
        if message.author.id == m.author.id:
            continue
        if "soundcloud.com" in m.content and count < 1:
            # Look for previous feedback
            count += 1
            return m.author.name, m.content, m.jump_url, m.author.id, m


# This method checks if the user who submitted feedback has given feedback to previous poster
# Returns a boolean.
async def validate_feedback(message):
    # pseudocode
    # Look for the last feedback submission.
    # Grab all messages from the time the person submitted the newest feedback till the last.
    # Check if the new submitter has mentioned the previous feedback (within those messages)
    # If they have, good to go. Gave feedback.
    # If they have not, then we need to deny their request.

    # Okay let's get the username of requester and the last feedback submitter.
    curr_feedback_user = message.author.name
    curr_feedback_user_id = message.author.id

    print("New person submitted feedback: " + curr_feedback_user)
    print()

    resp = await previous_feedback(message)

    prev_feedback_user = resp[0]
    prev_feedback_user_id = resp[3]
    previous_feedback_message = resp[4]
    print("Previous Feedback ID: ", previous_feedback_message.id)
    print("Previous Feedback author: " + prev_feedback_user)
    print()

    # Check history, has the requester replied to the submitter?
    messages = await message.channel.history(limit=100).flatten()

    count = 0
    # Grab all messages until the previous feedback
    for x in messages:
        count += 1
        if previous_feedback_message.id == x.id:
            # Got all messages till previous, check if the messages have mentions from original author
            messages_till_prev = await message.channel.history(limit=count).flatten()
            for y in messages_till_prev:
                # Now we check the messages the submitter has posted (since prev feedback)
                if y.author.id == curr_feedback_user_id:
                    # If they have given mentions, have they been to the prev feedback?
                    for mention in y.mentions:
                        if mention.id == prev_feedback_user_id:
                            # We know the new feedback submitter has replied to the previous feedback author.
                            print("Feedback message:", y.content)
                            print("Length of feedback:", len(y.content))
                            if len(y.content) > 100:
                                return True
                            else:
                                await message.channel.send(
                                    "Please make sure your submission is over 100 characters! That should be about a "
                                    "couple sentences on average. :)")
                                return False
    return False


async def deny_feedback(message):
    print("Feedback denied for:", message.author.name)

    last_feedback_info = await previous_feedback(message)
    embed_var = discord.Embed(title="Last Feedback Request", description="By: " + last_feedback_info[0],
                              color=0xFF0000)
    embed_var.add_field(name="Original Message", value=last_feedback_info[1], inline=False)
    embed_var.add_field(name="Link to Message", value=last_feedback_info[2], inline=False)
    await message.channel.send(
        message.author.mention + ", :x:** Feedback Denied! **:x: \n Please give feedback to the following: ",
        embed=embed_var)


client.run(TOKEN)
