from redbot.core import commands
import discord
import sqlite3
from sqlite3 import Error
import random
from random import seed
from random import randint
from datetime import datetime
client = discord.Client()
path = r"D:\Springfield\cogs\RaiQuotes\quotes.sqlite"
#testing path
path = r"C:\Users\olijo\Documents\discordRedbot\quotes.sqlite"


class Mycog(commands.Cog):
    """RaiQuotes Cog"""

    @commands.command()
    async def quoteid(self, ctx, word):
        """Finds a quote at the requested id"""
        # originally pulls down all quotes and searches them in code
        # now does a conditional select all on the db instead. In theory, should be slightly faster, but won't be noticable regardless.
        # this also just makes more sense to do.
        conn = None
        try:
            conn = sqlite3.connect(path)

            cur = conn.cursor()
            toEx = 'SELECT * FROM quotes where server_quote_id = ? and server_id = ?'
            
            cur.execute(toEx,(word,ctx.message.guild.id))
            row = cur.fetchone()
            found = 0
            if row is not None:
                name = '{}'.format(row[7])
                url = ''
                addedby = '?'
                img = ''
                for member in ctx.message.guild.members:
                    if row[6] == member.id:
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
    async def addquote(self, ctx, author):
        """Adds a quote to the database"""
        # Your code will go here
        quoted = ctx.message.content
        quoted = quoted.replace(author, "")
        quoted = quoted.replace(quoted[0],"")
        quoted = quoted.replace("addquote","")
        quoted = quoted.replace("  ","")
        linked = 0
        if(quoted.find("https") != -1):
            linked = 1
            if(quoted.find(" ", quoted.index("https"), len(quoted)) != -1):
                link = quoted[quoted.index("https"):quoted.index(" ", quoted.index("https"), len(quoted))]
                quoted = quoted.replace(link,"")
            else:
                link = quoted[quoted.index("https"):]
                quoted = quoted.replace(link,"")
        mention = 0
        if author[0] == "<":
            mention = 1
            author = author.replace("<", "")
            author = author.replace(">", "")
            author = author.replace("@", "")
            author = author.replace("!", "")
        conn = None
        try:
            conn = sqlite3.connect(path)
            if mention == 1:
                if len(ctx.message.attachments) > 0:
                    sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id, image_url) VALUES(?,?,?,?,?,?,?)'''
                    inputString = ('{}'.format(ctx.message.guild.id),'{}'.format(ctx.message.author.id), '{}'.format(author), '{}'.format(quoted), '{}'.format(ctx.message.channel.id), '{}'.format(ctx.message.id), '{}'.format(ctx.message.attachments[0].url))
                elif linked == 1:
                    sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id, image_url) VALUES(?,?,?,?,?,?,?)'''
                    inputString = ('{}'.format(ctx.message.guild.id),'{}'.format(ctx.message.author.id), '{}'.format(author), '{}'.format(quoted), '{}'.format(ctx.message.channel.id), '{}'.format(ctx.message.id), '{}'.format(link))
                else:
                    sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id) VALUES(?,?,?,?,?,?)'''
                    inputString = ('{}'.format(ctx.message.guild.id),'{}'.format(ctx.message.author.id), '{}'.format(author), '{}'.format(quoted), '{}'.format(ctx.message.channel.id), '{}'.format(ctx.message.id))
                
            if mention == 0:
                if len(ctx.message.attachments) > 0:
                    sql = '''INSERT INTO quotes(server_id,added_by,author_name,quote, channel_id, message_id, image_url) VALUES(?,?,?,?,?,?,?)'''
                    inputString = ('{}'.format(ctx.message.guild.id),'{}'.format(ctx.message.author.id), '{}'.format(author), '{}'.format(quoted), '{}'.format(ctx.message.channel.id), '{}'.format(ctx.message.id), '{}'.format(ctx.message.attachments[0].url))
                elif linked == 1:
                    sql = '''INSERT INTO quotes(server_id,added_by,author_name,quote, channel_id, message_id, image_url) VALUES(?,?,?,?,?,?,?)'''
                    inputString = ('{}'.format(ctx.message.guild.id),'{}'.format(ctx.message.author.id), '{}'.format(author), '{}'.format(quoted), '{}'.format(ctx.message.channel.id), '{}'.format(ctx.message.id), '{}'.format(link))
                else:
                    sql = '''INSERT INTO quotes(server_id,added_by,author_name,quote, channel_id, message_id) VALUES(?,?,?,?,?,?)'''
                    inputString = ('{}'.format(ctx.message.guild.id),'{}'.format(ctx.message.author.id), '{}'.format(author), '{}'.format(quoted), '{}'.format(ctx.message.channel.id), '{}'.format(ctx.message.id))
            cur = conn.cursor()
            cur.execute(sql,inputString)
            conn.commit()
            lastid = cur.lastrowid
            cur.execute("SELECT * FROM quotes")
            rows = cur.fetchall()
            quoteid = 0
            for row in rows:
                if '{}'.format(row[0]) == '{}'.format(lastid):
                    quoteid = row[2]
            await ctx.channel.send('Added that quote at id {} for ya! :)'.format(quoteid))
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def random(self, ctx):
        """Shows a random quote"""
        random.seed(datetime.now())
        quoted = ctx.message.content
        quoted = quoted.replace(quoted[0],"")
        quoted = quoted.replace("random","")
        author = 0
        if quoted != "":
            author = 1
            quoted = quoted.replace(" ", "")
            if quoted[0] == "<":
                quoted = quoted.replace("<", "")
                quoted = quoted.replace(">", "")
                quoted = quoted.replace("@", "")
                quoted = quoted.replace("!", "")
        if author == 1:
            conn = None
            try:
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                count = 0
                cur.execute("SELECT * FROM quotes")
                rows = cur.fetchall()
                for row in rows:
                    if row[1] == ctx.message.guild.id:
                        if '{}'.format(row[6]) == '{}'.format(quoted):
                            count = count + 1
                name = 'Error'
                url = ''
                addedby = '?'
                check = 1
                randval = 0
                if count != 0:
                    randval = randint(1, count)            
                name = '{}'.format(row[7])
                for row in rows:
                    if row[1] == ctx.message.guild.id:
                        if '{}'.format(row[6]) == '{}'.format(quoted):
                            if '{}'.format(check) == '{}'.format(randval):
                                for member in ctx.message.guild.members:
                                    if row[6] == member.id:
                                        name = '{}'.format(member.display_name)
                                        url = member.avatar_url
                                    if row[5] == member.id:
                                        addedby = '{}'.format(member.display_name)
                                emb = discord.Embed(title='{}'.format(name), description='{}'.format(row[8]), colour = 0x00ff00)
                                emb.set_footer(text = 'Added by: {} | Quote ID: {}'.format(addedby, row[2]))
                                if row[10] != None:
                                    emb.set_image(url='{}'.format(row[10]))
                                emb.set_thumbnail(url='{}'.format(url))
                                await ctx.channel.send(embed=emb)
                            check = check + 1
                if count == 0:
                    await ctx.channel.send("That author does not have any quotes saved. :(")
            except Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()
        if author == 0:
            conn = None
            try:
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                count = 0
                cur.execute("SELECT * FROM quotes")
                rows = cur.fetchall()
                for row in rows:
                    if row[1] == ctx.message.guild.id:
                        count = count + 1
                randval = 0
                if count != 0:
                    randval = randint(1, count)  
                name = 'Error'
                url = ''
                addedby = '?'
                check = 1
                for row in rows:
                    if row[1] == ctx.message.guild.id:
                        if '{}'.format(check) == '{}'.format(randval):
                            name = '{}'.format(row[7])
                            for member in ctx.message.guild.members:
                                if row[6] == member.id:
                                    name = '{}'.format(member.display_name)
                                    url = member.avatar_url
                                if row[5] == member.id:
                                    addedby = '{}'.format(member.display_name)
                            emb = discord.Embed(title='{}'.format(name), description='{}'.format(row[8]), colour = 0x00ff00)
                            emb.set_footer(text = 'Added by: {} | Quote ID: {}'.format(addedby, row[2]))
                            if row[10] != None:
                                emb.set_image(url='{}'.format(row[10]))
                            emb.set_thumbnail(url='{}'.format(url))
                            await ctx.channel.send(embed=emb)
                        check = check + 1
                if count == 0:
                    await ctx.channel.send("Eh? Somethings gone tits up. Go grab a coffee and let Rai know.")
            except Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()
                
    @commands.command()
    async def deleteid(self, ctx, word):
        """Deletes a quote at the requested id"""
        # Your code will go here
        
        conn = None
        try:
            conn = sqlite3.connect(path)
            sql = 'DELETE FROM quotes WHERE server_quote_id=?'
            cur = conn.cursor()
            cur.execute(sql,(word,))
            conn.commit()
            await ctx.channel.send('Quote {} should now be deleted! :)'.format(word))
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
        
    @commands.command()
    async def total(self, ctx, author):
        """Counts how many quotes the requested author has"""
        # Your code will go here
        author = author.replace("<", "")
        author = author.replace(">", "")
        author = author.replace("@", "")
        author = author.replace("!", "")

        conn = None
        try:
            conn = sqlite3.connect(path)

            cur = conn.cursor()
            count = 0
            cur.execute("SELECT * FROM quotes")
            rows = cur.fetchall()
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    if '{}'.format(row[6]) == '{}'.format(author):
                        count = count + 1
            await ctx.channel.send('<@!{}> has {} quotes saved in this server!'.format(author, count))
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def grandtotal(self, ctx):
        """Counts how many quotes are in the server"""
        # Your code will go here

        conn = None
        try:
            conn = sqlite3.connect(path)

            cur = conn.cursor()
            count = 0
            cur.execute("SELECT * FROM quotes")
            rows = cur.fetchall()
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    count = count + 1
            await ctx.channel.send('There are {} quotes saved in this server!'.format(count))
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

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
                            output = output  + name
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
                await ctx.channel.send("No matches for that boss!")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def searchQuotesStrict(self, ctx, word):
        """Search for all quotes containing a word. Print's a table, may not show entirerty of longer quotes"""
        # Your code will go here

        conn = None
        try:
            conn = sqlite3.connect(path)

            cur = conn.cursor()
            count = 0
            sql = "SELECT * FROM quotes where quote like ? or quote like ? or quote like ? or quote like ?"
            query = '% {} %'.format(word)
            left = '{} %'.format(word)
            right = '% {}'.format(word)
            cur.execute(sql, (query,left,right,word,))
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
                            output = output  + name
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
                await ctx.channel.send("No matches for that boss!")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def remix(self, ctx):
        """Remix baybeee"""
        random.seed(datetime.now())
        conn = None
        quote1 = ""
        quote2 = ""
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            count = 0
            cur.execute("SELECT * FROM quotes")
            rows = cur.fetchall()
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    count = count + 1
            randval1 = 0
            randval2 = 0
            if count != 0:
                randval1 = randint(1, count)
                randval2 = randint(1, count)
                matched = True
                while(matched):
                    if(randval1 == randval2):
                        matched = True
                        randval2 = randint(1, count)
                    else:
                        matched = False  
            name = 'Error'
            n1 = ''
            n2 = ''
            q1 = ''
            q2 = ''
            url = ''
            addedby = '?'
            check = 1
            id1 = 0
            id2 = 0
            for row in rows:
                if row[1] == ctx.message.guild.id:
                    if row[2] == randval1:
                        n1 = '{}'.format(row[7])
                        q1 = '{}'.format(row[8])
                        print(row[8])
                        for member in ctx.message.guild.members:
                            if row[6] == member.id:
                                n1 = '{}'.format(member.display_name)
                        if row[10] != None and row[8] != None:
                            url='{}'.format(row[10])
                            url='{}'.format(url)

                    if row[2] == randval2:
                        n2 = '{}'.format(row[7])
                        q2 = '{}'.format(row[8])
                        for member in ctx.message.guild.members:
                            if row[6] == member.id:
                                n2 = '{}'.format(member.display_name)
                        if row[10] != None:
                            url='{}'.format(row[10])
                            url='{}'.format(url)
                check = check + 1
            remixed = ''
            if(len(q1) != 0):
                chop = int(len(q1)/2)
                while(q1[chop] != ' ' and chop != len(q1) - 1):
                    chop = chop + 1
                
                remixed = q1[:chop]
            if(len(q2) != 0):
                chop = int(len(q2)/2)
                while(q2[chop] != ' ' and chop != 1):
                    chop = chop - 1
                
                if(chop == 0):
                    remixed = remixed + ' '
                remixed = remixed + q2[chop:]
            print(remixed)
            emb = discord.Embed(title='{}'.format(n1 + ' + ' + n2), description='{}'.format(remixed), colour = 0x00ff00)
            emb.set_image(url = '{}'.format(url))
            emb.set_thumbnail(url = '{}'.format(url))
            emb.set_footer(text = 'Quote IDs: {} + {}'.format(randval1, randval2))
            await ctx.channel.send(embed=emb)
                    
            if count == 0:
                await ctx.channel.send("Eh? Somethings gone tits up. Go grab a coffee and let Rai know.")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @commands.command()
    async def raihepl(self, ctx):
        """More detailed help command"""
        await ctx.channel.send('```Here are the commands for RaiQuotes cog!\nquoteid[id]               | Show the quote at [id]\naddquote [author] [quote] | Add a new quote to the database/ Accepts discord @user for [author] too!\ndeleteid [id]             | Deletes quote at [id]. It will be gone.... forever....\nrandom                    | Shows a random quote\ntotal [author]            | Shows how many quotes [author] has in this server\ngrandtotal                | Shows the total quotes in the server```')
