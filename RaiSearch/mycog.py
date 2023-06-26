from redbot.core import commands
import discord
import sqlite3
from sqlite3 import Error
import random
from random import seed
from random import randint
from datetime import datetime
import requests
import configparser
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
config = configparser.ConfigParser()

RENPY_SEARCH_API_KEY = 'AIzaSyCZy_pdZOF5mPMoa7p3ydULxj5bMwEs-SM'
SEARCH_ENGINE_ID = '40078de84708240a1'
googleapi_link = 'https://www.googleapis.com/customsearch/v1/siterestrict'
last_query = None
illegal_characters = '/|:.?^*&%.#[]{}<>+="\'`„“_~'

def renpy_docs_query(query, index):

    if any(char in illegal_characters for string in query for char in string):
        return 'illegal_query'

    url = f"{googleapi_link}?key={RENPY_SEARCH_API_KEY}&cx={SEARCH_ENGINE_ID}&q={'+'.join(query)}"
    r = requests.get(url)
    results = r.json()
    
    if results['searchInformation']['totalResults'] == 0:
        return 'no_result'

    try:
        result = results['items'][index]
    except IndexError:
        result = None

    return result

class Searchcog(commands.Cog):
    """RaiSearch Cog"""

    @commands.command()
    async def docs(self, ctx, query, index=0):
        print("here")
        print(query)
        print (index)
        # Setting global variables for the next() command to use
        global last_query
        global last_index
        last_query = query
        last_index = index

        result = renpy_docs_query(query, index)

        if result == 'no_result':
            await ctx.channel.send("0 results found for this query.")
            return
        elif result == 'illegal_query':
            await ctx.channel.send("Query includes illegal character. Alphanumerical characters are recommended.")
            return
    
        # For the next() command - If there are no more results at this index position
        if not result:
            await ctx.channel.send(f"Reached end of results for last query! Issue a `docs <query>` command first.")
            return

        title = result['title']
        link = result['link']
        snippet = result['snippet']

        embed = discord.Embed(title=title, description=link)
        embed.add_field(name='', value=snippet)
        embed.set_footer(text=f'Result #{index+1}')

        await ctx.channel.send(embed=embed)

    @commands.command()
    async def next(self, ctx):

        if last_query:
            command = self.get_command('docs')
            await ctx.invoke(command, *last_query, index=last_index+1)

        else:
            await ctx.channel.send(f"Issue a `docs <query>` command first!")