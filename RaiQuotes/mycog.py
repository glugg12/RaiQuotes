from redbot.core import commands
import discord
import sqlite3
from sqlite3 import Error
import random
from random import seed
from random import randint
from datetime import datetime
client = discord.Client()
print('init')

class Mycog(commands.Cog):
    """My custom cog"""

    @commands.command()
    async def quoteid(self, ctx, word):
        """This does stuff!"""
        # Your code will go here
        
        conn = None
        try:
            conn = sqlite3.connect(r"quotes.sqlite")
            print(sqlite3.version)

            cur = conn.cursor()
            cur.execute("SELECT * FROM quotes")
            rows = cur.fetchall()
            found = 0
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    numb = row[2]
                    if '{}'.format(numb) == '{}'.format(word):
                        name = '{}'.format(row[7])
                        url = ''
                        addedby = '?'
                        img = ''
                        for member in ctx.message.guild.members:
                            if row[6] == member.id:
                                print(member.display_name)
                                name = '{}'.format(member.display_name)
                                url = member.avatar_url
                            if row[5] ==member.id:
                                addedby = '{}'.format(member.display_name)
                        emb = discord.Embed(title='{}'.format(name), description='{}'.format(row[8]), colour = 0x00ff00)
                        emb.set_footer(text = 'Added by: {}'.format(addedby))
                        if row[10] != None:
                            emb.set_image(url='{}'.format(row[10]))
                
                        emb.set_thumbnail(url='{}'.format(url))
                        found = 1
                        await ctx.channel.send(embed=emb)
            if found == 0:
                await ctx.channel.send("Couldn't find that quote!")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
    
    @commands.command()
    async def randomquote(self, ctx):
        """This does stuff!"""
        # Your code will go here
        random.seed(datetime.now())

        conn = None
        try:
            conn = sqlite3.connect(r"Z:\_DBS\quotes.sqlite")
            print(sqlite3.version)

            cur = conn.cursor()
            count = 0
            cur.execute("SELECT * FROM quotes")
            rows = cur.fetchall()
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    count = count + 1
            randval = randint(0,count)
            name = 'Error'
            url = ''
            addedby = '?'
            check = 0
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    if '{}'.format(check) == '{}'.format(randval):
                        for member in ctx.message.guild.members:
                            name = '{}'.format(row[7])
                            if row[6] == member.id:
                                name = '{}'.format(member.display_name)
                                url = member.avatar_url
                            if row[5] == member.id:
                                addedby = '{}'.format(member.display_name)
                        emb = discord.Embed(title='{}'.format(name), description='{}'.format(row[8]), colour = 0x00ff00)
                        emb.set_footer(text = 'Added by: {}'.format(addedby))
                        if row[10] != None:
                            emb.set_image(url='{}'.format(row[10]))
                        emb.set_thumbnail(url='{}'.format(url))
                        await ctx.channel.send(embed=emb)
                    check = check + 1
            
            
            
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def addquote(self, ctx, author, quoted):
        """This does stuff!"""
        # Your code will go here
        author = author.replace("<", "")
        author = author.replace(">", "")
        author = author.replace("@", "")
        author = author.replace("!", "")
        print(author)
        conn = None
        try:
            conn = sqlite3.connect(r"Z:\_DBS\quotes.sqlite")
            print(sqlite3.version)
            sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id) VALUES(?,?,?,?,?,?)'''
            cur = conn.cursor()
            inputString = ('{}'.format(ctx.message.guild.id),'{}'.format(ctx.message.author.id), '{}'.format(author), '{}'.format(quoted), '{}'.format(ctx.message.channel.id), '{}'.format(ctx.message.id))
            cur.execute(sql,inputString)
            conn.commit()
            await ctx.channel.send("Added that quote for ya! :)")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def random(self, ctx, author):
        """This does stuff!"""
        # Your code will go here
        random.seed(datetime.now())
        author = author.replace("<", "")
        author = author.replace(">", "")
        author = author.replace("@", "")
        author = author.replace("!", "")

        conn = None
        try:
            conn = sqlite3.connect(r"Z:\_DBS\quotes.sqlite")
            print(sqlite3.version)

            cur = conn.cursor()
            count = 0
            cur.execute("SELECT * FROM quotes")
            rows = cur.fetchall()
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    if '{}'.format(row[6]) == '{}'.format(author):
                        count = count + 1
            randval = randint(1,count)
            name = 'Error'
            url = ''
            addedby = '?'
            check = 1
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    if '{}'.format(row[6]) == '{}'.format(author):
                        if '{}'.format(check) == '{}'.format(randval):
                            
                            name = '{}'.format(row[7])
                            for member in ctx.message.guild.members:
                                if row[6] == member.id:
                                    print("here")
                                    name = '{}'.format(member.display_name)
                                    url = member.avatar_url
                                if row[5] == member.id:
                                    addedby = '{}'.format(member.display_name)
                            emb = discord.Embed(title='{}'.format(name), description='{}'.format(row[8]), colour = 0x00ff00)
                            emb.set_footer(text = 'Added by: {}'.format(addedby))
                            if row[10] != None:
                                emb.set_image(url='{}'.format(row[10]))
                            emb.set_thumbnail(url='{}'.format(url))
                            await ctx.channel.send(embed=emb)
                        check = check + 1
            
            
            
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()