from redbot.core import commands, app_commands
from RaiQuotes import databaseUtility
import discord
import sqlite3
from sqlite3 import Error
import random
from random import randint
from datetime import datetime
import configparser
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
path = r"D:\Springfield\cogs\RaiQuotes\quotes.sqlite"
configPath = r"D:\Springfield\cogs\RaiQuotes\ApiConfig.ini"
config = configparser.ConfigParser()

# testing path
path = r"C:\Users\olijo\Documents\discordRedbot\quotes.sqlite"
# configPath = r"C:\Users\olijo\Documents\discordRedbot\ApiConfig.ini"
# config.read(configPath)
# apiUrl = config['DEFAULT']['Api']


class Mycog(commands.Cog):
    """RaiQuotes Cog"""
    def __init__(self, bot):
        self.bot = bot

    quotes = app_commands.Group(name="quotes", description="Rai quotes commands")

    @quotes.command(name="get_quote")
    async def quote_id(self, interaction: discord.Interaction, quote_id: int):
        """Finds a quote at the requested id"""
        # originally pulls down all quotes and searches them in code
        # now does a conditional select all on the db instead. In theory, should be slightly faster, but won't be noticable regardless.
        # this also just makes more sense to do.
        row = databaseUtility.get_quote(quote_id, interaction.guild_id)
        found = 0
        if row is not None:
            name = '{}'.format(row[7])
            url = ''
            added_by = '?'
            img = ''
            for member in interaction.guild.members:
                if row[6] == member.id:
                    name = '{}'.format(member.display_name)
                    url = member.display_avatar
                if row[5] == member.id:
                    added_by = '{}'.format(member.display_name)
            emb = discord.Embed(title='{}'.format(name), description='{}'.format(row[8]), colour=0x00ff00)
            emb.set_footer(text='Added by: {} | Quote ID: {}'.format(added_by, row[2]))
            if row[10] is not None:
                emb.set_image(url='{}'.format(row[10]))

            emb.set_thumbnail(url='{}'.format(url))
            found = 1
            await interaction.response.send_message(embed=emb)

        if found == 0:
            await interaction.response.send_message("I'm afraid I couldn't find that quote for you.")

    @quotes.command(name="add_quote")
    async def add_quote(self, interaction: discord.Interaction, quote_author: discord.Member, quote: str):
        """Adds a quote to the database"""
        server_id = interaction.guild_id
        added_by = interaction.user.id
        author_id = quote_author.id
        quote_text = quote
        channel_id = interaction.channel_id
        message_id = interaction.id
        quote_id = databaseUtility.insert_quote(server_id, added_by, author_id, quote_text, channel_id, message_id)
        if quote_id is not None:
            await interaction.response.send_message('I have saved that quote for you under ID {}, safe and sound ~'.format(quote_id))
        else:
            await interaction.response.send_message('I have encountered an error when adding that quote. insert_quote returned None.')

    @quotes.command(name="random")
    async def random(self, interaction: discord.Interaction, quote_author: discord.Member = None):
        """Shows a random quote"""
        random.seed(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

        # get all rows
        rows = databaseUtility.get_all_quotes(interaction.guild_id, quote_author)
        # choose a random result from rows
        rand_val = randint(0, len(rows) - 1)
        selected_row = rows[rand_val]
        name = ''
        added_by = ''
        url = ''
        print(selected_row)
        for member in interaction.guild.members:
            if selected_row[6] == member.id:
                name = '{}'.format(member.display_name)
                url = member.display_avatar
            if selected_row[5] == member.id:
                added_by = '{}'.format(member.display_name)
        emb = discord.Embed(title='{}'.format(name), description='{}'.format(selected_row[8]),
                            colour=0x00ff00)
        emb.set_footer(text='Added by: {} | Quote ID: {}'.format(added_by, selected_row[2]))
        if selected_row[10] is not None:
            emb.set_image(url='{}'.format(selected_row[10]))
        emb.set_thumbnail(url='{}'.format(url))
        await interaction.response.send_message(embed=emb)

    @quotes.command(name="delete_quote")
    async def deleteid(self, interaction: discord.Interaction, quote_id: int):
        """Deletes a quote at the requested id"""
        databaseUtility.delete_quote(interaction.guild_id, quote_id)
        await interaction.response.send_message('The quote at ID {} is now gone for good.'.format(quote_id))

    @quotes.command(name="total")
    async def total(self, interaction: discord.Interaction, member: discord.Member = None):
        """Counts how many quotes the requested author has"""
        if member is None:
            member = interaction.user
        rows = databaseUtility.get_all_quotes(interaction.guild_id, member)
        total = len(rows)
        await interaction.response.send_message('Oh my, <@!{}> has {} quotes saved for this server.'.format(member.id, total))

    @quotes.command(name="server_total")
    async def server_total(self, interaction: discord.Interaction):
        """Counts how many quotes are in the server"""
        rows = databaseUtility.get_all_quotes(interaction.guild_id)
        total = len(rows)
        await interaction.response.send_message('There are {} quotes saved in this server. Good work everyone ~'.format(total))

    @commands.command()
    async def searchQuotes(self, ctx, word):
        """Search for all quotes containing a word. Print's a table, may not show entirerty of longer quotes"""
        # Your code will go here
        conn = None
        try:
            conn = sqlite3.connect(path)

            cur = conn.cursor()
            count = 0
            sql = "SELECT * FROM quotes where quote like ?"
            query = '%{}%'.format(word)
            cur.execute(sql, (query,))
            rows = cur.fetchall()
            output = '```'
            if rows is not None:
                output = output + "ID    | Name                 | Quote\n"
                for row in rows:
                    if row[1] == 198685985234616320:
                        count = count + 1
                        output = output + '{}'.format(row[2])
                        for i in range(0, (5 - len('{}'.format(row[2])))):
                            output = output + ' '
                        output = output + ' | '
                        if row[6] is None:
                            name = row[7]
                            if len(name) > 20:
                                name = name[:20]
                            output = output + name
                            for i in range(0, (20 - len(name))):
                                output = output + ' '
                        else:
                            name = ""
                            for member in ctx.message.guild.members:
                                if row[6] == member.id:
                                    name = '{}'.format(member.display_name)
                            if len(name) > 20:
                                name = name[:20]
                            output = output + '{}'.format(name)
                            for i in range(0, (20 - len(name))):
                                output = output + ' '
                        output = output + ' | ' + row[8] + ' \n'
                output = output + '```'
                if len(output) > 2000:
                    output = output[:1970] + "\nresults too long```"
                await ctx.channel.send(output)
            else:
                await ctx.channel.send("I couldn't find any matches for that query.")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def searchQuotesStrict(self, ctx, word):
        """Search for all quotes containing a word. Print's a table, may not show entirerty of longer quotes"""

        conn = None
        try:
            conn = sqlite3.connect(path)

            cur = conn.cursor()
            count = 0
            sql = "SELECT * FROM quotes where quote like ? or quote like ? or quote like ? or quote like ?"
            query = '% {} %'.format(word)
            left = '{} %'.format(word)
            right = '% {}'.format(word)
            cur.execute(sql, (query, left, right, word,))
            rows = cur.fetchall()
            output = '```'
            if rows is not None:
                output = output + "ID    | Name                 | Quote\n"
                for row in rows:
                    if row[1] == ctx.message.guild.id:
                        count = count + 1
                        output = output + '{}'.format(row[2])
                        for i in range(0, (5 - len('{}'.format(row[2])))):
                            output = output + ' '
                        output = output + ' | '
                        if row[6] is None:
                            name = row[7]
                            if len(name) > 20:
                                name = name[:20]
                            output = output + name
                            for i in range(0, (20 - len(name))):
                                output = output + ' '
                        else:
                            name = ""
                            for member in ctx.message.guild.members:
                                if row[6] == member.id:
                                    name = '{}'.format(member.display_name)
                            if len(name) > 20:
                                name = name[:20]
                            output = output + '{}'.format(name)
                            for i in range(0, (20 - len(name))):
                                output = output + ' '
                        output = output + ' | ' + row[8] + ' \n'
                output = output + '```'
                if len(output) > 2000:
                    output = output[:1970] + "\nresults too long```"
                await ctx.channel.send(output)
            else:
                await ctx.channel.send("I couldn't find any matches for that query.")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @quotes.command(name="remix")
    async def remix(self, interaction: discord.Interaction, quote_author: discord.Member = None, remix_id: int = None):
        """Remixes quotes from the server."""
        random.seed(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        rows = databaseUtility.get_all_quotes(interaction.guild_id, quote_author)
        length = len(rows)
        if quote_author is not None and remix_id is not None:
            await interaction.response.send_message("I cannot remix within an author's quote and with a requested ID. Please chose one or the other.")
            return
        if length > 1:
            randval1 = randint(0, length - 1)
            randval2 = randint(0, length - 1)
            matched = True
            while matched:
                if randval1 == randval2:
                    matched = True
                    randval2 = randint(0, length - 1)
                else:
                    matched = False
            url = ''
            remixed = ''
            # quote 1 or requested id
            if remix_id is not None:
                row = databaseUtility.get_quote(remix_id, interaction.guild_id)
                n1 = '{}'.format(row[7])
                q1 = '{}'.format(row[8])
                id1 = row[2]
                for member in interaction.guild.members:
                    if row[6] == member.id:
                        n1 = '{}'.format(member.display_name)
                if row[10] is not None and row[8] is not None:
                    url = '{}'.format(rows[randval1][10])
                    url = '{}'.format(url)
            else:
                n1 = '{}'.format(rows[randval1][7])
                q1 = '{}'.format(rows[randval1][8])
                id1 = rows[randval1][2]
                for member in interaction.guild.members:
                    if rows[randval1][6] == member.id:
                        n1 = '{}'.format(member.display_name)
                if rows[randval1][10] is not None and rows[randval1][8] is not None:
                    url = '{}'.format(rows[randval1][10])
                    url = '{}'.format(url)
            # quote 2
            n2 = '{}'.format(rows[randval2][7])
            q2 = '{}'.format(rows[randval2][8])
            id2 = rows[randval2][2]
            for member in interaction.guild.members:
                if rows[randval2][6] == member.id:
                    n2 = '{}'.format(member.display_name)
            if rows[randval2][10] is not None and rows[randval2][8] is not None and url != '':
                url = '{}'.format(rows[randval1][10])
                url = '{}'.format(url)

            # check if it should swap quote order
            swap = randint(0, 1)
            if swap == 1:
                n_swap = n1
                q_swap = q1
                id_swap = id1
                n1 = n2
                q1 = q2
                id1 = id2
                n2 = n_swap
                q2 = q_swap
                id2 = id_swap

            if len(q1) != 0:
                chop = int(len(q1) / 2)
                while q1[chop] != ' ' and chop != len(q1) - 1:
                    chop = chop + 1
                if chop < len(q1):
                    remixed = q1[:chop]
                else:
                    remixed = q1
            if len(q2) != 0:
                chop = int(len(q2) / 2)
                while q2[chop] != ' ' and chop != 0:
                    chop = chop - 1

                if chop == 0:
                    remixed = remixed + ' '
                remixed = remixed + q2[chop:]
            emb = discord.Embed(title='{}'.format(n1 + ' + ' + n2), description='{}'.format(remixed), colour=0x00ff00)
            emb.set_image(url='{}'.format(url))
            emb.set_footer(text='Quote IDs: {} + {}'.format(id1, id2))
            await interaction.response.send_message(embed=emb)
        else:
            await interaction.response.send_message("I did not find enough quotes to remix for your request.")

    @quotes.command(name="total_added")
    async def total_added(self, interaction: discord.Interaction, author: discord.Member = None):
        """Counts how many quotes the requested author has added"""
        # Your code will go here
        if author is None:
            author = interaction.user
        rows = databaseUtility.get_all_quotes(interaction.guild_id, author)
        total = len(rows)
        await interaction.response.send_message(
                '<@!{}> has added {} quotes in this server. Keep it up ~'.format(author.id, total))


    @quotes.command()
    async def raihepl(self, interaction: discord.Interaction):
        """More detailed help command"""
        await interaction.response.send_message(
            '```Here are the commands for RaiQuotes cog!\nquoteid[id]               | Show the quote at [id]\naddquote [author] [quote] | Add a new quote to the database/ Accepts discord @user for [author] too!\ndeleteid [id]             | Deletes quote at [id]. It will be gone.... forever....\nrandom                    | Shows a random quote\ntotal [author]            | Shows how many quotes [author] has in this server\ngrandtotal                | Shows the total quotes in the server```', ephemeral=True)

    # @commands.command()
    # async def DevTest(self, ctx):
    #     session = requests.Session()
    #     print("Testing response....")
    #     response = session.get(url=apiUrl)
    #     print(response.text)
