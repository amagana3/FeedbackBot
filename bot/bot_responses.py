import discord
import re
from discord import Embed, Color

from constants import MessageResponseContext, SupportedLinks, SupportedFormats

regex = r'([A-Za-z.]+)'
replace = r'`\1`'

supported_links_list = [link.value for link in SupportedLinks]
supported_links_str = ", ".join(supported_links_list)
supported_links = re.sub(regex, replace, supported_links_str)

supported_formats_list = [formats.value for formats in SupportedFormats]
supported_formats_str = ", ".join(supported_formats_list)
supported_formats = re.sub(regex, replace, supported_formats_str)


# TODO: Introduce a design pattern for building these messages, generically.
def previous_feedback_submission_message(prev_feedback_metadata: MessageResponseContext) -> Embed:
    """ Embedded response for .last"""
    embed = discord.Embed(title="Previous Feedback Submission", description="By: " + prev_feedback_metadata.author,
                          color=Color.green())
    embed.add_field(name="Original Message", value=prev_feedback_metadata.content[0:997] + "...", inline=False)
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
    embed.add_field(name="Supported Links", value=supported_links,
                    inline=False)
    embed.add_field(name="Supported attachments", value=supported_formats,
                    inline=False)
    return embed


def deny_feedback_submission_message(prev_feedback_metadata: MessageResponseContext) -> Embed:
    """ Embedded response for denied feedback"""
    embed = discord.Embed(title="Previous Feedback Submission", description="By: " + prev_feedback_metadata.author,
                          color=Color.red())
    embed.add_field(name="Original Message", value=prev_feedback_metadata.content, inline=False)
    embed.add_field(name="Link to Message", value=prev_feedback_metadata.jump_url, inline=False)
    return embed
