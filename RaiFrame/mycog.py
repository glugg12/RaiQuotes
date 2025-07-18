from redbot.core import commands, app_commands
from RaiQuotes import databaseUtility
import discord
import sqlite3
from sqlite3 import Error
import random
from random import randint
from datetime import datetime
from datetime import timezone
import configparser
from discord.ext import tasks
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# testing path
# path = r"C:\Users\olijo\Documents\discordRedbot\quotes.sqlite"

# utc = timezone.utc
# time = datetime.time(hour=20, minute=00, tzinfo=utc)
category_mod = discord.SelectOption(label="Mod")
category_primes = discord.SelectOption(label="Prime Parts")

class AddItemModal(discord.ui.Modal, title="Add wishlist item"):
    # category_dropdown = discord.ui.select(placeholder="Category", min_values = 1, max_values = 2, options = [category_mod, category_primes])
    name = discord.ui.TextInput(label='Name')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("A")

    async def on_submit(self, interaction: discord.Interaction, error):
        await interaction.response.send_message("B")

class FrameCog(commands.Cog):
    """RaiQuotes Cog"""
    
    def __init__(self, bot):
        self.bot = bot
        
    
    quotes = app_commands.Group(name="warf", description="Warframe Wishlist Utilities")

    @quotes.command(name="add_item")
    async def add_item(self, interaction: discord.Interaction):
        add_item_modal = AddItemModal()
        await interaction.response.send_modal(add_item_modal)
