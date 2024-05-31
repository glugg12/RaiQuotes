import sqlite3
from sqlite3 import Error

path = r"C:\Users\olijo\Documents\discordRedbot\quotes.sqlite"


def insert_quote(server_id, added_by, author_id, quote, channel_id, message_id, image_url=None):
    if image_url is not None:
        sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id, image_url) VALUES(?,?,?,?,?,?,?)'''
        inputString = (
            '{}'.format(server_id), '{}'.format(added_by), '{}'.format(author_id),
            '{}'.format(quote), '{}'.format(channel_id), '{}'.format(message_id),
            '{}'.format(image_url))
    else:
        sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id) VALUES(?,?,?,?,?,?)'''
        inputString = (
            '{}'.format(server_id), '{}'.format(added_by), '{}'.format(author_id),
            '{}'.format(quote), '{}'.format(channel_id), '{}'.format(message_id))
    conn = None
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute(sql, inputString)
        conn.commit()
        last_id = cur.lastrowid
        cur.execute("SELECT * FROM quotes")
        conn.commit()
        rows = cur.fetchall()
        quote_id = 0
        for row in rows:
            if '{}'.format(row[0]) == '{}'.format(last_id):
                quote_id = row[2]
        return quote_id
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def get_quote(quote_id, server_id):
    conn = None
    try:
        conn = sqlite3.connect(path)

        cur = conn.cursor()
        to_ex = '''SELECT * FROM quotes where server_quote_id = ? and server_id = ?'''

        cur.execute(to_ex, (quote_id, server_id))
        row = cur.fetchone()
        return row
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
