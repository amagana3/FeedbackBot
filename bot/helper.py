from discord import Message

from constants import MessageResponseContext, SupportedLinks, SupportedFormats
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(funcName)s:%(lineno)d - %(message)s')


def check_for_link(message: Message, count: int) -> MessageResponseContext or None:
    if not any(link.value in message.content for link in SupportedLinks) or count >= 1:
        return None

    logging.info("found link previous feedback: {}".format(message.content))
    # Look for previous feedback
    count += 1
    return MessageResponseContext(author=message.author.name, content=message.content, jump_url=message.jump_url,
                                  author_id=message.author.id,
                                  message_id=message.id)


def check_for_attachment(message: Message, count: int) -> MessageResponseContext or None:
    """Checks if attachment is found in message"""
    if len(message.attachments) != 1 or not any(
            message.attachments[0].filename.endswith(fmt.value) for fmt in SupportedFormats) or count >= 1:
        return None

    logging.info("found attachment previous feedback: {}".format(message.attachments[0].filename))
    # Look for previous feedback
    count += 1
    # Check for empty message attachment
    if len(message.content) > 1:
        return MessageResponseContext(author=message.author.name, content=message.content, jump_url=message.jump_url,
                                      author_id=message.author.id, message_id=message.id)
    return MessageResponseContext(author=message.author.name, content=message.attachments[0].filename,
                                  jump_url=message.jump_url,
                                  author_id=message.author.id, message_id=message.id)
