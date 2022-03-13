from discord import Message

from constants import MessageResponseContext, SupportedLinks, SupportedFormats
import log

logger = log.setup_logger('root')


def check_for_link(message: Message) -> MessageResponseContext or None:
    if not any(link.value in message.content for link in SupportedLinks):
        return None

    logger.info("found link previous feedback: {}".format(message.content))
    # Look for previous feedback
    return MessageResponseContext(author=message.author.name, content=message.content, jump_url=message.jump_url,
                                  author_id=message.author.id,
                                  message_id=message.id)


def check_for_attachment(message: Message) -> MessageResponseContext or None:
    """Checks if attachment is found in message"""
    if len(message.attachments) != 1 or not any(
            message.attachments[0].filename.endswith(fmt.value) for fmt in SupportedFormats):
        return None

    logger.info("found attachment previous feedback: {}".format(message.attachments[0].filename))
    # Look for previous feedback
    # Check for empty message attachment
    if len(message.content) > 1:
        return MessageResponseContext(author=message.author.name, content=message.content, jump_url=message.jump_url,
                                      author_id=message.author.id, message_id=message.id)
    return MessageResponseContext(author=message.author.name, content=message.attachments[0].filename,
                                  jump_url=message.jump_url,
                                  author_id=message.author.id, message_id=message.id)
