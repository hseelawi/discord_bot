"""
Discord Birthday Bot

A Discord bot that automatically sends birthday wishes to server members on their birthday.
The bot reads birthday data from a CSV file, generates personalized messages using Claude AI,
and sends birthday messages along with GIFs from Tenor to a specified channel.

The bot reads the following configuration from settings:
    - discord_token: Discord bot token for authentication
    - channel_id: Channel ID for sending birthday messages
    - heartbeat_channel_id: Channel ID for tracking script execution
    - claude_api_key: Anthropic API key for message generation
    - claude_model: Anthropic model for text message generation
    - claude_prompt: Birthday message prompt template
    - tenor_api_key: Tenor API key for GIF retrieval
    - tenor_query: Search query for birthday GIFs
    - data_path: Path to csv containing user birthday and username (can be local or s3path)
"""

import logging
import random
from datetime import datetime

import aiohttp
import discord
import pandas as pd
from anthropic import Anthropic
from discord.ext import commands

from settings import get_settings

logger = logging.getLogger("discord")
settings = get_settings()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
anthropic = Anthropic(api_key=settings.claude_api_key)


async def send_heartbeat(channel):
    """
    Send a heartbeat message to track script execution.

    Args:
        channel (discord.TextChannel): The Discord channel to send the heartbeat to

    Notes:
        Sends current date and time along with execution confirmation
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await channel.send(f"🤖 Script executed at {current_time}")
    except Exception as e:
        logger.error(f"Failed to send heartbeat message: {e}")


async def get_birthday_message(mention):
    """
    Generate a personalized birthday message using Claude AI.

    Args:
        mention (str): The Discord mention string for the birthday celebrant

    Returns:
        str: The formatted birthday message including the mention and AI-generated content

    Notes:
        Falls back to a simple default message if Claude API call fails
    """
    try:
        completion = anthropic.messages.create(
            model=settings.claude_model,
            max_tokens=150,
            temperature=0.9,
            messages=[{"role": "user", "content": settings.claude_prompt}],
        )
        message = completion.content[0].text.strip()
        return f"{mention} {message}"
    except Exception as e:
        logger.error(f"Failed to generate message using Claude: {e}")
        return f"{mention} 🎉 Happy Birthday! 🎂"


async def get_birthday_celebrants():
    """
    Retrieve list of users whose birthday is today.

    Returns:
        list[str]: List of usernames having birthdays on the current date

    Notes:
        - Reads from 'birthdays.csv' which must have 'username' and 'birthday' columns
        - Birthday column should be in a format parseable by pandas.to_datetime
    """
    today = datetime.now().strftime("%m-%d")
    df = pd.read_csv(settings.data_path)
    df["birthday"] = pd.to_datetime(df["birthday"])
    df["birthday_md"] = df["birthday"].dt.strftime("%m-%d")
    return df[df["birthday_md"] == today]["username"].tolist()


async def send_tenor_gif(channel):
    """
    Send a random birthday-themed GIF from Tenor to the specified Discord channel.
    Fetches top 5 results and randomly selects one.

    Args:
        channel (discord.TextChannel): The Discord channel to send the GIF to
    Notes:
        - Uses tenor_query from settings for GIF search
        - Requires valid Tenor API key in settings
        - Silently fails if GIF cannot be fetched or sent
    """
    try:
        api_key = settings.tenor_api_key
        query = settings.tenor_query
        # Set limit=5 to get top 5 results, remove random=true to get consistent top results
        search_url = (
            f"https://tenor.googleapis.com/v2/search?q={query}&key={api_key}&limit=10"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["results"]:
                        # Randomly select one GIF from the top 5
                        random_gif = random.choice(data["results"])
                        gif_url = random_gif["media_formats"]["gif"]["url"]
                        await channel.send(gif_url)
                    else:
                        logger.warning("No GIFs found")
    except Exception as e:
        logger.error(f"Failed to fetch GIF from Tenor: {e}")


@bot.event
async def on_ready():
    """
    Handle bot startup and birthday message distribution.

    This event handler:
    1. Sends a heartbeat message for execution tracking
    2. Checks for today's birthday celebrants
    3. Sends personalized messages and GIFs for each celebrant
    4. Closes the bot after completion

    Notes:
        Bot will automatically close after:
        - Processing all birthday messages
        - If no birthdays are found today
        - If required channels cannot be found
        - If an unhandled exception occurs
    """
    try:
        logger.info("Bot has connected to Discord!")

        # Send heartbeat message
        heartbeat_channel = bot.get_channel(settings.heartbeat_channel_id)
        if heartbeat_channel:
            await send_heartbeat(heartbeat_channel)
        else:
            logger.error(
                f"Could not find heartbeat channel with ID: {settings.heartbeat_channel_id}"
            )

        # Process birthdays
        channel = bot.get_channel(settings.channel_id)
        if channel is None:
            logger.error(f"Could not find channel with ID: {settings.channel_id}")
            await bot.close()
            return

        guild = channel.guild
        celebrants = await get_birthday_celebrants()
        if not celebrants:
            logger.info("No birthdays today")
            await bot.close()
            return

        for username in celebrants:
            member = discord.utils.get(guild.members, name=username)
            if member:
                await send_tenor_gif(channel)
                birthday_message = await get_birthday_message(member.mention)
                await channel.send(birthday_message)
            else:
                logger.warning(f"Could not find user {username} in the server")

        await bot.close()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await bot.close()


try:
    bot.run(settings.discord_token)
except Exception as e:
    logger.error(f"Failed to start the bot: {e}")