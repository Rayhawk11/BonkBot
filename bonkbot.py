"""
Bonk Bot main source file.
"""

import os
import sys
import logging
from typing import Union, List

import discord

# Configuration
EMOJI = 'Thonk_Bonk'
ROLE = 'janitor'
TARGET = 'bonk'
MESSAGE = 'Please keep NSFW conversations limited to abyss channels.'
BLACKLISTED_STRINGS = {'https://media.discordapp.net/attachments/650552561019125780/788593749600632892/1607974944336.gif', 'https://tenor.com/view/among-us-twerk-yellow-ass-thang-gif-18983570', ':BonkCircumventer:'}

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


def build_formatted_text(mention_string, bonker, text):
    """
    Construct a formatted text block to send in the target channel
    :param mention_string: Name of the user who sent the message
    :param text: The text of the original message
    :return: A formatted block string to send.
    """
    res = f"{mention_string} has been bonked by {bonker}\n{MESSAGE}\n"
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
        if self.target_channel is None:
            logger.warning(f"Target channel {TARGET} does not exist")
            return
        logger.info(f"Set target channel to {self.target_channel.name}")

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        emoji_name = get_emoji_name(reaction.emoji)
        logger.info(f"User '{user.display_name}' sent '{emoji_name}'")

        # Test that this is a bonk
        if emoji_name == EMOJI and ROLE in get_role_names(user.roles):
            logger.info(f"{reaction.message.id} bonked by {user.display_name}")
            message_text = reaction.message.content
            await reaction.message.delete()
            new_message = await self.target_channel.send(
                build_formatted_text(reaction.message.author.mention, user.mention, message_text))
            logger.info(f"Successfully moved {reaction.message.id} to {new_message.id}")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if any(substring in message.content for substring in BLACKLISTED_STRINGS):
            logger.info(f"{message.id} bonked for containing blacklisted string")
            message_text = message.content
            await message.delete()
            new_message = await self.target_channel.send(build_formatted_text(message.author.mention, 'BonkBot', message_text))
            logger.info(f"Successfully moved {message.id} to {new_message.id}")


if __name__ == '__main__':
    token = os.environ.get('DISCORD_TOKEN')
    if token is None:
        logger.error("DISCORD_TOKEN not set. Exiting.")
        sys.exit(1)

    logger.info("Running Client")
    client = BonkBot()
    client.run(token)
    logger.warning("Client exited")
