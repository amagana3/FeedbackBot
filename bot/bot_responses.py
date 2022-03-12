import discord
from discord import Embed, Color

from constants import MessageResponseContext


def last_feedback_message(prev_feedback_metadata: MessageResponseContext) -> Embed:
    """ Embedded response for .last"""
    embed = discord.Embed(title="Last Feedback Request", description="By: " + prev_feedback_metadata.author,
                          color=Color.green())
    embed.add_field(name="Original Message", value=prev_feedback_metadata.content, inline=False)
    embed.add_field(name="Link to Message", value=prev_feedback_metadata.jump_url, inline=False)
    return embed


def info_message() -> Embed:
    """ Embedded response for .info"""
    embed = discord.Embed(title="FeedbackBot", description="Author: KingMagana69", color=Color.blue())
    embed.add_field(name="How does the bot work?",
                    value="The bot checks to see if the last person who submitted feedback gave feedback "
                          "to the previous submitter. Feedback can be given in the form of a "
                          "tag (@), or a direct reply. Note: Anyone who games the system will be kicked.",
                    inline=False)
    embed.add_field(name="Command Option: `.last`", value="Shows the previous feedback submission",
                    inline=False)
    embed.add_field(name="Command Option: `.info`", value="Display how the bot works",
                    inline=False)
    embed.add_field(name="Supported Links", value="soundcloud, dropbox",
                    inline=False)
    embed.add_field(name="Supported attachments", value=" `.mp3`, `.mp4a`, `.flac`, `.wav`",
                    inline=False)
    return embed


def deny_feedback_message(prev_feedback_metadata: MessageResponseContext) -> Embed:
    """ Embedded response for denied feedback"""
    embed = discord.Embed(title="Last Feedback Request", description="By: " + prev_feedback_metadata.author,
                          color=Color.red())
    embed.add_field(name="Original Message", value=prev_feedback_metadata.content, inline=False)
    embed.add_field(name="Link to Message", value=prev_feedback_metadata.jump_url, inline=False)
    return embed
