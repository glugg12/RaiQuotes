import sqlite3
from sqlite3 import Error

path = r"C:\Users\olijo\Documents\discordRedbot\quotes.sqlite"


def insert_quote(server_id, added_by, author_id, quote, channel_id, message_id, image_url=None):
    sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id, image_url) VALUES(?,?,?,?,?,?,?)'''
    inputString = (
        '{}'.format(server_id), '{}'.format(added_by), '{}'.format(author_id),
        '{}'.format(quote), '{}'.format(channel_id), '{}'.format(message_id),
        '{}'.format(image_url))
    conn = None
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute(sql, inputString)
        conn.commit()
        lastid = cur.lastrowid
        cur.execute("SELECT * FROM quotes")
        rows = cur.fetchall()
        quoteid = 0
        for row in rows:
            if '{}'.format(row[0]) == '{}'.format(lastid):
                quoteid = row[2]
        return quoteid
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

