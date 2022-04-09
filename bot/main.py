# Author: Andrew Magana
# main.py
"""
Problem: When someone wants feedback we should make sure they have given feedback to the previous feedback track.
Solution:
    When someone submits a new feedback (link or appropriate format), check to see the previous user's feedback.
    See if current user (submitter) has given feedback to previous person.
    IF they have
        Good! We can allow track to post.
    ELSE they have not
        Then we decline the feedback, and tell them to give feedback to previous user.
"""

import log
import os

import discord
from discord import Message
from dotenv import load_dotenv

from bot_responses import previous_feedback_submission_message, info_message, deny_feedback_submission_message
from constants import SupportedLinks, SupportedFormats, MessageResponseContext
from helper import check_for_link, check_for_attachment

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

# Setup logger
logger = log.setup_logger(name='root')


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    logger.info(f'{client.user} is connected to the following GUILD: {guild.name} (ID: {guild.id})')


@client.event
async def on_message(message: Message):
    # The bot called, ignore.
    if message.author == client.user:
        return

    # Should be in feedback channel
    if message.channel.name != 'feedback':
        return

    general_log = {
        "author": message.author.name,
        "content": message.content,
        "attachments": message.attachments
    }

    logger.info(general_log)

    await validate_link(message)
    await validate_attachment(message)

    # Someone wants to know what the last feedback is.
    if '.last' in message.content:
        last_feedback_info = await last_feedback(message)
        logger.info('last feedback message length: {}'.format(len(last_feedback_info.content)))
        await message.channel.send(embed=previous_feedback_submission_message(last_feedback_info))

    # Some general info about this bot and the commands available.
    if '.info' in message.content:
        await message.channel.send(embed=info_message())


async def validate_link(message: Message) -> None:
    # Validate links
    if any(link.value in message.content for link in SupportedLinks):
        logger.info("link found: {}".format(message.content))
        if not await validate_feedback_submission(message):
            await deny_feedback_submission(message)


async def validate_attachment(message: Message) -> None:
    # Validate attachments
    if len(message.attachments) == 1 and any(
            message.attachments[0].filename.endswith(fmt.value) for fmt in SupportedFormats):
        logger.info("attachment found: {}".format(message.attachments[0].filename))
        if not await validate_feedback_submission(message):
            await deny_feedback_submission(message)
    elif len(message.attachments) > 1:
        logger.info("more than one attachment is not allowed")
        await message.channel.send(
            message.author.mention + ", :x:** Feedback Denied! **:x: \n Only 1 attachment is allowed!!! ")


# This exists to give the last feedback overall (even if you're the final submission)
async def last_feedback(message: Message) -> MessageResponseContext:
    previous_messages = await message.channel.history(limit=100).flatten()
    for msg in previous_messages:
        link_exists = check_for_link(msg)
        if link_exists:
            return link_exists

        attach_exists = check_for_attachment(msg)
        if attach_exists:
            return attach_exists


# This is to get the previous feedback that DOES NOT INCLUDE the denied one (since we gotta submit to trigger this)
async def previous_feedback(message: Message) -> MessageResponseContext:
    previous_messages = await message.channel.history(limit=100).flatten()
    for m in previous_messages:
        if message.author.id == m.author.id:
            continue

        # This stops from showing the person who just submitted.
        link_exists = check_for_link(m)
        if link_exists:
            return link_exists

        attach_exists = check_for_attachment(m)
        if attach_exists:
            return attach_exists


''' --- pseudocode --- 
    validate_feedback_submission()
    Objective: Look for the last feedback submission.
    Approach:
    - Grab all messages from the time the person submitted the newest feedback till the last.
    - Check if the new submitter has mentioned the previous feedback (within those messages)
    - If they have, good to go. Gave feedback.
    - If they have not, then we need to deny their request.
'''


async def validate_feedback_submission(message: Message) -> bool:
    """ Checks to make sure the one submitting a track has given feedback. """

    # Grab current submitter info
    current_user = message.author.name
    current_user_id = message.author.id
    logger.info("new feedback submitted by: {}".format(current_user))

    # Grab previous feedback submission info
    prev_fb_submission = await previous_feedback(message)
    if prev_fb_submission is None:
        logger.info("no previous feedback track exists")
        return True

    logger.info("found previous feedback: {}".format(prev_fb_submission))

    prev_fb_user = prev_fb_submission.author
    prev_fb_user_id = prev_fb_submission.author_id
    prev_fb_message_id = prev_fb_submission.message_id
    logger.info("previous feedback ID: {}".format(prev_fb_message_id))
    logger.info("previous feedback author: {}".format(prev_fb_user))

    # Check history, has the requester replied to the submitter?
    previous_messages = await message.channel.history(limit=100).flatten()

    count = 0
    # Grab all messages until the previous feedback
    for msg in previous_messages:
        count += 1
        if prev_fb_message_id != msg.id:
            continue
        # Got all messages till previous, check if the messages have mentions from original author
        messages_till_prev_fb = await message.channel.history(limit=count).flatten()
        for sub_msg in messages_till_prev_fb:
            # Now we check the messages the submitter has posted (since prev feedback)
            if sub_msg.author.id != current_user_id:
                continue
            # If they have given mentions, have they been to the prev feedback?
            for mention in sub_msg.mentions:
                if mention.id != prev_fb_user_id:
                    continue
                # We know the new feedback submitter has given feedback to prev. submission
                logger.info(
                    "feedback message: {} \n"
                    "length: {}".format(sub_msg.content, len(sub_msg.content)))
                # Must be 100 chars of feedback.
                if len(sub_msg.content) >= 100:
                    return True
                else:
                    await message.channel.send(
                        "Please make sure your submission is over 100 characters! "
                        "That should be about a couple sentences on average. :)")
                    return False
    return False


# Right now it checks if feedback is valid and if it isn't, denys it.
async def deny_feedback_submission(message: Message) -> None:
    await message.delete()
    logger.info("feedback submission denied for: {}".format(message.author.name))
    last_feedback_info = await previous_feedback(message)
    await message.channel.send(
        message.author.mention +
        ", :x:** Feedback Request Denied! **:x: \n "
        "Please direct reply or mention @" + last_feedback_info.author + " the previous feedback submission: ",
        embed=deny_feedback_submission_message(last_feedback_info))


client.run(TOKEN)
