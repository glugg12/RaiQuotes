import json

from redbot.core import commands
import discord
import pip

try:
    import requests
except ImportError:
    pip.main(['install', 'requests'])
import configparser

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
configPath = r"D:\Springfield\cogs\RaiQuotesV2\ApiConfig.ini"
config = configparser.ConfigParser()

config.read(configPath)
# need to run api alongside this
apiUrl = 'api:8080/'


class Mycog(commands.Cog):
    """RaiQuotes Cog"""

    @commands.command()
    async def quoteid(self, ctx, quote_id):
        """Finds a quote at the requested id"""
        server_id = ctx.message.guild.id
        if isinstance(quote_id, int):
            await ctx.channel.send("That is not a valid integer")
            return
        else:
            url = "localhost:8080/quotes/server/{}/{}".format(server_id, quote_id)
            response = requests.post(url)
            await ctx.channel.send(json.loads(response.content)["quote"])

    @commands.command()
    async def addquote(self, ctx, author):
        """Adds a quote to the database"""

    @commands.command()
    async def random(self, ctx):
        """Shows a random quote"""

    @commands.command()
    async def deleteid(self, ctx, word):
        """Deletes a quote at the requested id"""

    @commands.command()
    async def total(self, ctx, author):
        """Counts how many quotes the requested author has"""

    @commands.command()
    async def grandtotal(self, ctx):
        """Counts how many quotes are in the server"""

    @commands.command()
    async def searchQuotes(self, ctx, word):
        """Search for all quotes containing a word. Print's a table, may not show entirerty of longer quotes"""

    @commands.command()
    async def searchQuotesStrict(self, ctx, word):
        """Search for all quotes containing a word. Print's a table, may not show entirerty of longer quotes"""

    @commands.command()
    async def remix(self, ctx):
        """Remix baybeee"""

    @commands.command()
    async def remixid(self, ctx, id):
        """Remix baybeee"""

    @commands.command()
    async def totalAdded(self, ctx, author):
        """Counts how many quotes the requested author has added"""

    @commands.command()
    async def raihepl(self, ctx):
        """More detailed help command"""
        await ctx.channel.send(
            '```Here are the commands for RaiQuotes cog!\nquoteid[id]               | Show the quote at [id]\naddquote [author] [quote] | Add a new quote to the database/ Accepts discord @user for [author] too!\ndeleteid [id]             | Deletes quote at [id]. It will be gone.... forever....\nrandom                    | Shows a random quote\ntotal [author]            | Shows how many quotes [author] has in this server\ngrandtotal                | Shows the total quotes in the server```')
