from .mycog import Searchcog
import sqlite3
from sqlite3 import Error

async def setup(bot):
    
    await bot.add_cog(Searchcog())
