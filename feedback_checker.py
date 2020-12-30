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


async def previous_feedback(message) -> tuple:
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
    # Get the last feedback
    # Check to see if the person requesting has given feedback to last one
    # Check if person sending has @(user) the person w/ 100 characters or more.
    # If they have - allow the feedback submission. (true)
    # If they have not - deny their feedback. (false)

    # Okay let's get the username of requester and the last feedback submitter.
    curr_feedback_user = message.author.name
    curr_feedback_user_id = message.author.id

    print("New person submitted feedback: " + curr_feedback_user)
    print()

    resp = await previous_feedback(message)

    prev_feedback_user = resp[0]
    prev_feedback_user_id = resp[3]

    print("Previous feedback was: " + prev_feedback_user)
    print()

    # Check history, has the requester replied to the submitter?
    messages = await message.channel.history(limit=100).flatten()
    if len(messages) <= 1:
        # Exit early if there is nothing.
        return True

    for x in messages:
        for y in x.mentions:
            if y.id == prev_feedback_user_id:
                # Got the previous mention, but was it by the submitter?
                print("The previous feedback submitter is:", y.name)
                if x.author.id == curr_feedback_user_id:
                    print("The person who currently gave feedback is:", curr_feedback_user)
                    return True

    # for y in previous_message.mentions:
    #     print("---")
    #     print("Person mentioned: ", y)
    # if y.mentioned_in(x):
    #     if x.author.name == "FeedbackBot":
    #         # The bot did mentions, ignore his.
    #         continue
    #
    #     print("Original Author: ", x.author.name)
    #     print("Mentioned Author: ", y.name)
    #     print("Message: ", x.content)
    #     return True
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
