import json

from redbot.core import commands
import discord
import pip
import json
from datetime import date
import random
from datetime import datetime
from random import randint

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
        if quote_id is not None:
            try:
                int(quote_id)
                url = apiUrl + "quotes/server/{}/{}".format(server_id, quote_id)
                response = requests.get(url)
                if response.status_code == 200:
                    content = json.loads(response.content)
                    user = None
                    if content["authorId"] is not None:
                        user = ctx.guild.get_member(int(content["authorId"]))
                    added_by = ctx.guild.get_member(int(content["addedBy"]))
                    if user is not None:
                        emb = discord.Embed(title='{}'.format(user.display_name),
                                            description='{}'.format(content["quote"]),
                                            colour=0x00ff00)
                        emb.set_thumbnail(url='{}'.format(user.display_avatar))
                    else:
                        emb = discord.Embed(title='{}'.format(content["authorName"]),
                                            description='{}'.format(content["quote"]), colour=0x00ff00)
                    emb.set_footer(text='Added by: {} | {}'.format(added_by.display_name, content["dateAdded"].split('T')[0]))

                    if content["imageUrl"] is not None:
                        emb.set_image(url='{}'.format(content["imageUrl"]))
                    await ctx.channel.send(embed=emb)
                elif response.status_code == 404:
                    await ctx.channel.send("I'm afraid I couldn't find that quote for you.")
            except ValueError:
                await ctx.channel.send("I'm sorry, but {} is not a value I can use for a quote ID".format(quote_id))
                return
        else:
            await ctx.channel.send("Would you please provide a quote ID for me to use with the command?")

    @commands.command()
    async def addquote(self, ctx, *args):
        """Adds a quote to the database"""
        #   command should be issued with <@author/author name> <quote>, so we can grab the first arg, see if it's an @ or
        #   not, then collect the message afterward
        #   Is there a nicer to convert <@id> to a member?
        mentioned = ""
        if args[0][0] == "<":
            mentioned = args[0]
            replace_list = ["<", ">", "@", "!"]
            for char in replace_list:
                mentioned = mentioned.replace(char, "")
        try:
            author = ctx.guild.get_member(int(mentioned))
            author = author.id
        except ValueError:
            author = None
        author_name = None
        link = None
        quoted_words = list(args[1:])
        if author is None:
            author_name = args[0]
        for location, partial in enumerate(args[1:]):
            if partial.find("https") != -1:
                link = partial
                quoted_words.remove(partial)
        quote = " ".join(quoted_words)
        request = {
            "quote": quote,
            "serverId": ctx.guild.id,
            "addedBy": ctx.message.author.id,
            "authorId": author,
            "authorName": author_name,
            "imageUrl": link,
            "date": date.today().strftime("%Y-%m-%d"),
        }
        url = apiUrl + "quotes"
        response = requests.post(url, json=request)
        if response.status_code == 200:
            content = json.loads(response.content)
            await ctx.channel.send(
                'I have saved that quote for you under ID {}, safe and sound ~'.format(content["serverQuoteId"]))
        elif response.status_code == 404:
            await ctx.channel.send("I'm afraid I couldn't find that quote for you.")
        else:
            await ctx.channel.send('I have encountered a problem: Response code: {}'.format(response.status_code))

    @commands.command()
    async def random(self, ctx, *args):
        """Shows a random quote"""
        author_id = None
        author_name = None
        if not args:
            #     no author passed
            url = apiUrl + "quotes/server/{}/random".format(ctx.guild.id)
        else:
            try:
                if args[0][0] == "<":
                    author = args[0]
                    replace_list = ["<", ">", "@", "!"]
                    for char in replace_list:
                        author = author.replace(char, "")
                    member = ctx.guild.get_member(int(author))
                    if member is not None:
                        author_id = member.id
                    else:
                        author_name = " ".join(args)
                else:
                    author_name = " ".join(args)
            except ValueError:
                #         search for string literal
                author_name = " ".join(args)
            #     should have final_author here now
            if author_id is not None:
                url = apiUrl + "quotes/server/{}/random?authorId={}".format(ctx.guild.id, author_id)
            elif author_name is not None:
                url = apiUrl + "quotes/server/{}/random?authorName={}".format(ctx.guild.id, author_name)
            else:
                #   should never occur, but just in case
                url = apiUrl + "quotes/server/{}/random".format(ctx.guild.id)

        response = requests.get(url)
        if response.status_code == 200:
            content = json.loads(response.content)
            await ctx.channel.send(content)
        elif response.status_code == 412:
            await ctx.channel.send(
                "I'm sorry, there appears to not be any quotes I can use for your request right now.")
        else:
            await ctx.channel.send('I have encountered a problem: Response code: {}'.format(response.status_code))

    @commands.command()
    async def delete(self, ctx, quote_id):
        """Deletes a quote at the requested id"""
        if quote_id is not None:
            try:
                int(quote_id)
            except ValueError:
                await ctx.channel.send("I'm sorry, but {} is not a value I can use for a quote ID".format(quote_id))
                return
            url = apiUrl + "quotes/server/{}/{}".format(ctx.guild.id, quote_id)
            response = requests.delete(url)
            content = json.loads(response.content)
            if response.status_code == 200:
                await ctx.channel.send('The quote at ID {} is now gone for good.'.format(quote_id))
            elif response.status_code == 404:
                await ctx.channel.send("I'm afraid I couldn't find that quote for you.")
            else:
                await ctx.channel.send('I have encountered a problem: Response code: {}'.format(response.status_code))
        else:
            await ctx.channel.send("Would you please provide a quote ID for me to use with the command?")

    @commands.command()
    async def stats(self, ctx, author=None):
        """Get various stats"""
        if author is not None:
            try:
                replace_list = ["<", ">", "@", "!"]
                for char in replace_list:
                    author = author.replace(char, "")
                int(author)
            except ValueError:
                await ctx.channel.send(
                    "I'm sorry, but {} is not a value I can use for a user ID. At this time, I can only use mentioned users for this command.".format(
                        author))
                return
            member = ctx.guild.get_member(int(author))
            if member is not None:
                url = apiUrl + "quotes/server/{}/stats/{}".format(ctx.guild.id, member.id)
                response = requests.get(url)
                content = json.loads(response.content)
                if response.status_code == 200:
                    random.seed(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                    emb = discord.Embed(title='{}'.format(member.display_name),
                                        description='{}'.format(
                                            "Quotes added: {}\nTimes quoted: {}\n Total swag: {}".format(
                                                content["totalTimesQuoted"], content["totalQuotesAdded"],
                                                randint(1, 1000)
                                            )),
                                        colour=0x00ff00)
                    emb.set_footer(
                        text="Remember, nothing's ever a competition! Your quotes and contributions are loved regardless of these statistics. <3")
                    emb.set_thumbnail(url='{}'.format(member.display_avatar))
                    await ctx.channel.send(embed=emb)
                else:
                    await ctx.channel.send(
                        'I have encountered a problem: Response code: {}'.format(response.status_code))
            else:
                await ctx.channel.send(
                    "I'm sorry, but {} is not a value I can use for a user ID. At this time, I can only use mentioned users for this command.".format(
                        author))
        else:
            url = apiUrl + "quotes/server/{}/stats".format(ctx.guild.id)
            response = requests.get(url)
            content = json.loads(response.content)
            if response.status_code == 200:
                random.seed(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                emb = discord.Embed(title='{}'.format(ctx.guild.name),
                                    description='{}'.format("Total Quotes: {}".format(content["totalQuotes"])),
                                    colour=0x00ff00)
                emb.set_footer(text="You're making so many memories together!")
                emb.set_thumbnail(url='{}'.format(ctx.guild.icon))
                await ctx.channel.send(embed=emb)
            else:
                await ctx.channel.send('I have encountered a problem: Response code: {}'.format(response.status_code))

    # todo: reimplement when a better search solution is developed in the api
    # @commands.command()
    # async def searchQuotes(self, ctx, word):
    #     """Search for all quotes containing a word. Print's a table, may not show entirerty of longer quotes"""
    #
    # @commands.command()
    # async def searchQuotesStrict(self, ctx, word):
    #     """Search for all quotes containing a word. Print's a table, may not show entirerty of longer quotes"""

    @commands.command()
    async def remix(self, ctx, remix_request=None):
        """Remix baybeee"""
        if remix_request is not None:
            if remix_request[0] == "<":
                try:
                    temp = remix_request
                    replace_list = ["<", ">", "@", "!"]
                    for char in replace_list:
                        temp = temp.replace(char, "")
                    int(temp)
                    member = ctx.guild.get_member(int(temp))
                    url = apiUrl + "quotes/server/{}/remix?authorId={}".format(ctx.guild.id, member.id)
                except ValueError:
                    await ctx.channel.send(
                        "I'm sorry, but {} is not a value I can use for a user or a quote ID. At this time, I can only use mentioned users and quote IDs (or nothing) for this command.".format(
                            remix_request))
                    return
            else:
                #             we do not tend to use plain string for authors anymore - if we wanted to here is where we would do it. Though we need to check if whole string is int
                try:
                    int(remix_request)
                    url = apiUrl + "quotes/server/{}/remix?quoteId={}".format(ctx.guild.id, remix_request)
                except ValueError:
                    await ctx.channel.send(
                        "I'm sorry, but {} is not a value I can use for a user or a quote ID. At this time, I can only use mentioned users and quote IDs (or nothing) for this command.".format(
                            remix_request))
                    return
        else:
            url = apiUrl + "quotes/server/{}/remix".format(ctx.guild.id)
        response = requests.get(url)
        content = json.loads(response.content)
        if response.status_code == 200:
            try:
                int(content["author1"])
                name1 = ctx.guild.get_member(int(content["author1"])).display_name
            except ValueError:
                name1 = content["author1"]
            try:
                int(content["author2"])
                name2 = ctx.guild.get_member(int(content["author2"])).display_name
            except ValueError:
                name2 = content["author2"]
            emb = discord.Embed(title='{} + {}'.format(name1, name2),
                                description='{}'.format("{}".format(content["quote"])),
                                colour=0x00ff00)
            emb.set_footer(text="Quote IDs {} + {}".format(content["quoteId1"], content["quoteId2"]))
            await ctx.channel.send(embed=emb)
        else:
            await ctx.channel.send('I have encountered a problem: Response code: {}'.format(response.status_code))

    @commands.command()
    async def getSplits(self, ctx, quote_id):
        """Get the splits for the quote"""
        try:
            int(quote_id)
        except ValueError:
            await ctx.channel.send("I'm sorry, but {} is not a value I can use for a quote ID".format(quote_id))
            return
        url = apiUrl + "quotes/server/{}/{}/split".format(ctx.guild.id, quote_id)
        response = requests.get(url)
        content = json.loads(response.content)
        if response.status_code == 200:
            emb = discord.Embed(title='Split Data',
                                description='{}'.format("{}\n Left split ends at: {}\n Right split starts at: {}".format(content["fullQuote"], content["splitLeftPosition"], content["splitRightPosition"])),
                                colour=0x00ff00)
            emb.set_footer(text="Please remember that these values are INCLUDING the formatting characters. Setting your own splits, you should ignore the formatting characters when counting")
            await ctx.channel.send(embed=emb)
        else:
            await ctx.channel.send('I have encountered a problem: Response code: {}'.format(response.status_code))

    @commands.command()
    async def setSplits(self, ctx, quote_id, **kwargs):
        """Set the splits for the quote"""
        try:
            int(quote_id)
            left = None
            right = None
            if 'left' in kwargs:
                left = kwargs.get('left')
            if 'right' in kwargs:
                right = kwargs.get('right')
            if left is not None:
                left = int(left)
            if right is not None:
                right = int(right)
        except ValueError:
            await ctx.channel.send("I'm sorry, but one of your input values is not an integer")
            return
        url = apiUrl + "quotes/server/{}/{}/split".format(ctx.guild.id, quote_id)
        quote_url = apiUrl + "quotes/server/{}/{}".format(ctx.guild.id, quote_id)
        response = requests.get(quote_url)
        if response.status_code == 200:
            content = json.loads(response.content)
            formatters = ["***", "**", "*", "__", "_", "~~"]
            skip_ast = False
            skip_und = False
            if left is not None:
                left_split = content["quote"][:left]
                for formatter in formatters:
                    if left_split.count(formatter) > 0:
                        if formatter.find("*") != -1:
                            if not skip_ast:
                                left = left + (left_split.count(formatter) * len(formatter))
                                print("adding {}".format((left_split.count(formatter) * len(formatter))))
                                skip_ast = True
                        elif formatter.find("_") != -1:
                            if not skip_und:
                                left = left + (left_split.count(formatter) * len(formatter))
                                skip_und = True
                        else:
                            left = left + (left_split.count(formatter) * len(formatter))
            if right is not None:
                right_split = content["quote"][right:]
                skip_ast = False
                skip_und = False
                for formatter in formatters:
                    if right_split.count(formatter) > 0:
                        if formatter.find("*") != -1:
                            if not skip_ast:
                                right = right + (right_split.count(formatter) * len(formatter))
                                skip_ast = True
                        elif formatter.find("_") != -1:
                            if not skip_und:
                                right = right + (right_split.count(formatter) * len(formatter))
                                skip_und = True
                        else:
                            right = right + (right_split.count(formatter) * len(formatter))
        else:
            await ctx.channel.send('I have encountered a problem: Response code: {}'.format(response.status_code))
            return
        request = {
            "splitLeftPosition": left,
            "splitRightPosition": right,
        }
        response = requests.post(url, json=request)
        content = json.loads(response.content)
        if response.status_code == 200:
            emb = discord.Embed(title='Split Data',
                                description='{}'.format("{}\n Left split ends at: {}\n Right split starts at: {}".format(content["fullQuote"], content["splitLeftPosition"], content["splitRightPosition"])),
                                colour=0x00ff00)
            emb.set_footer(text="Please remember that these values are INCLUDING the formatting characters. Setting your own splits, you should ignore the formatting characters when counting")
            await ctx.channel.send(embed=emb)
        else:
            await ctx.channel.send('I have encountered a problem: Response code: {}'.format(response.status_code))