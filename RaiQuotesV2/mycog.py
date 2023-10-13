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
intents.members = True
client = discord.Client(intents=intents)
configPath = r"D:\Springfield\cogs\RaiQuotesV2\ApiConfig.ini"
config = configparser.ConfigParser()

config.read(configPath)
# need to run api alongside this
apiUrl = 'http://api:8080/'


class Mycog(commands.Cog):
    """RaiQuotes Cog"""

    @commands.command()
    async def quoteid(self, ctx, quote_id):
        """Finds a quote at the requested id"""
        server_id = ctx.message.guild.id
        print('begin')
        try:
            int(quote_id)
            print('int')
            url = apiUrl + "quotes/server/{}/{}".format(server_id, quote_id)
            response = requests.get(url)
            if response.status_code == 200:
                content = json.loads(response.content)
                user = ctx.guild.get_member(int(content["authorId"]))
                added_by = ctx.guild.get_member(int(content["addedBy"]))
                if user is not None:
                    emb = discord.Embed(title='{}'.format(user.display_name), description='{}'.format(content["quote"]),
                                        colour=0x00ff00)
                else:
                    emb = discord.Embed(title='{}'.format(content["authorName"]),
                                        description='{}'.format(content["quote"]), colour=0x00ff00)
                emb.set_footer(text='Added by: {}'.format(added_by.display_name))
                await ctx.channel.send(embed=emb)
            elif response.status_code == 404:
                await ctx.channel.send("I'm afraid I couldn't find that quote for you.")
        except ValueError:
            print('not int')
            await ctx.channel.send("That is not a valid integer")
            return

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
