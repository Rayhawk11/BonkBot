"""
Bonk Bot main source file.
"""

import os
import sys
import logging
from typing import Union, List

import discord

# Configuration
EMOJI = 'custom_emoji_name'
ROLE = 'Role1'
TARGET = 'jail'
MESSAGE = "Your message has been moved!"


# Configure Logging
logging.basicConfig()
logger = logging.getLogger('bonkbot')
logger.setLevel(logging.DEBUG)


def get_emoji_name(emoji: Union[discord.Emoji, discord.PartialEmoji, str]):
    """
    Built in emoji's are represented by a unicode character. Custom emoji's are an object
    Normalize emoji's to something easy to use

    :param emoji: The object returned from `discord.Reaction.emoji`
    :return: A human readable string. May be unicode
    """

    if isinstance(emoji, str):
        return emoji
    else:
        return emoji.name

def get_role_names(roles: List[discord.Role]):
    """
    Returns the names as strings of a list of roles.
    """
    return [role.name for role in roles]


def build_formatted_text(mention_string, text):
    """
    Construct a formatted text block to send in the target channel
    :param mention_string: Name of the user who sent the message
    :param text: The text of the original message
    :return: A formatted block string to send.
    """
    res = f"{mention_string}\n{MESSAGE}\n"
    for line in text.split("\n"):
        res += "> " + line
    return res

class BonkBot(discord.Client):

    def __init__(self, **options):
        super().__init__(**options)
        self.target_channel: discord.TextChannel = None

    async def on_connect(self):
        logger.info(f"Connected with '{self.user}'")

    async def on_ready(self):
        logger.info("Client ready")
        self.target_channel = discord.utils.get(self.get_all_channels(), name=TARGET)
        logger.info(f"Set target channel to {self.target_channel.name}")

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        emoji_name = get_emoji_name(reaction.emoji)
        logger.info(f"User '{user.display_name}' sent '{emoji_name}'")

        # Test that this is a bonk
        if emoji_name == EMOJI and ROLE in get_role_names(user.roles):
            logger.info(f"{reaction.message.id} bonked by {user.display_name}")
            message_text = reaction.message.content
            await reaction.message.delete()
            new_message = await self.target_channel.send(build_formatted_text(reaction.message.author.mention, message_text))
            logger.info(f"Successfully moved {reaction.message.id} to {new_message.id}")


if __name__ == '__main__':
    token = os.environ.get('DISCORD_TOKEN')
    if token is None:
        logger.error("DISCORD_TOKEN not set. Exiting.")
        sys.exit(1)

    logger.info("Running Client")
    client = BonkBot()
    client.run(token)
    logger.warning("Client exited")
