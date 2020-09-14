from .mycog import Mycog
import sqlite3
from sqlite3 import Error

def setup(bot):
    
    bot.add_cog(Mycog())