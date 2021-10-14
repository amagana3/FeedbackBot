# Author: Andrew Magana
# main.py

import os
import logging
import discord
from dotenv import load_dotenv
from bot_responses import last_feedback_message, info_message
from enums import SupportedLinks, SupportedFormats

# pseudocode:
# Problem: When someone wants feedback we should make sure they have given feedback to the previous feedback track.
# Solution:
#   When someone submits a new feedback (Soundcloud link), check to see the previous user's feedback
#   See if current user (submitter) has given feedback to previous person
#   if they have, then we're good!
#   if they haven't, then we decline the feedback and tell them to give feedback to previous user.
#       Send them the message in context to give feedback.

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(funcName)s:%(lineno)d - %(message)s')


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    logging.info(f'{client.user} is connected to the following GUILD: {guild.name} (ID: {guild.id}')


@client.event
async def on_message(message):
    # The bot called, ignore.
    if message.author == client.user:
        return

    # Should be in feedback channel
    if message.channel.name == 'feedback':
        general_log = {
            "author": message.author.name,
            "content": message.content,
            "attachments": message.attachments
        }

        logging.info(general_log)

        # Verify links
        if any(link.value in message.content for link in SupportedLinks):
            logging.info("link found: {}".format(message.content))
            if not await validate_feedback(message):
                await message.delete()
                await deny_feedback(message)

        # Verify attachments
        if len(message.attachments) == 1 and any(
                message.attachments[0].filename.endswith(fmt.value) for fmt in SupportedFormats):
            logging.info("attachment found: {}".format(message.attachments[0].filename))
            if not await validate_feedback(message):
                await message.delete()
                await deny_feedback(message)

        # Someone wants to know what the last feedback is.
        if '.last' in message.content:
            last_feedback_info = await last_feedback(message)
            await message.channel.send(embed=last_feedback_message(last_feedback_info))

        # Some general info about this bot and the commands available.
        if '.info' in message.content:
            await message.channel.send(embed=info_message())


# This exists to give the last feedback overall (even if you're the final submission)
async def last_feedback(message) -> tuple:
    count = 0
    messages = await message.channel.history(limit=100).flatten()
    for m in messages:
        if any(link.value in m.content for link in SupportedLinks) and count < 1:
            logging.info("found link previous feedback: {}".format(m.content))
            # Look for previous feedback
            count += 1
            return m.author.name, m.content, m.jump_url, m.author.id

        check_for_attachment(m, count)


# This is to get the previous feedback that DOES NOT INCLUDE the denied one (since we gotta submit to trigger this)
async def previous_feedback(message) -> tuple:
    count = 0
    messages = await message.channel.history(limit=100).flatten()
    for m in messages:
        # This stops from showing the person who just submitted.
        if message.author.id == m.author.id:
            continue
        if any(link.value in m.content for link in SupportedLinks) and count < 1:
            logging.info("found link previous feedback: {}".format(m.content))
            # Look for previous feedback
            count += 1
            return m.author.name, m.content, m.jump_url, m.author.id, m

        check_for_attachment(m, count)


# pseudocode
# Look for the last feedback submission.
# Grab all messages from the time the person submitted the newest feedback till the last.
# Check if the new submitter has mentioned the previous feedback (within those messages)
# If they have, good to go. Gave feedback.
# If they have not, then we need to deny their request.
# This method checks if the user who submitted feedback has given feedback to previous poster
# Returns a boolean.
async def validate_feedback(message):
    """ Checks to make sure the one submitting a track has given feedback. """

    # Okay let's get the username of requester and the last feedback submitter.
    curr_feedback_user = message.author.name
    curr_feedback_user_id = message.author.id

    logging.info("new feedback submitted by: {}".format(curr_feedback_user))

    resp = await previous_feedback(message)
    logging.info("found previous feedback: {}".format(resp))

    prev_feedback_user = resp[0]
    prev_feedback_user_id = resp[3]
    previous_feedback_message = resp[4]
    logging.info("previous feedback ID: {}".format(previous_feedback_message.id))
    logging.info("previous feedback author: {}".format(prev_feedback_user))

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
                            logging.info("Feedback message: {}".format(y.content))
                            logging.info("Length of feedback: {}".format(len(y.content)))
                            if len(y.content) >= 100:
                                return True
                            else:
                                await message.channel.send(
                                    "Please make sure your submission is over 100 characters! That should be about a "
                                    "couple sentences on average. :)")
                                return False
    return False


def check_for_attachment(m, count):
    """Checks if attachment is found in message"""
    if len(m.attachments) != 1 or not any(
            m.attachments[0].filename.endswith(fmt.value) for fmt in SupportedFormats) or count >= 1:
        return

    logging.info("found attachment previous feedback: {}".format(m.attachments[0].filename))
    # Look for previous feedback
    count += 1
    # Check for empty message attachment
    if len(m.content) > 1:
        return m.author.name, m.content, m.jump_url, m.author.id, m
    return m.author.name, m.attachments[0].filename, m.jump_url, m.author.id, m


async def deny_feedback(message):
    logging.info("Feedback denied for: {}".format(message.author.name))

    last_feedback_info = await previous_feedback(message)
    embed_var = discord.Embed(title="Last Feedback Request", description="By: " + last_feedback_info[0],
                              color=0xFF0000)
    embed_var.add_field(name="Original Message", value=last_feedback_info[1], inline=False)
    embed_var.add_field(name="Link to Message", value=last_feedback_info[2], inline=False)
    await message.channel.send(
        message.author.mention + ", :x:** Feedback Denied! **:x: \n Please give feedback to the following: ",
        embed=embed_var)


client.run(TOKEN)
