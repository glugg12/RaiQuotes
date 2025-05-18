import sqlite3
from sqlite3 import Error
import os
from RaiQuotes.exceptions import QuoteNotFoundException, NoSplitValuesException
path = os.environ['QUOTES_DB_PATH']
# path = f'"{path_input}"'
# path = r"C:\Users\olijo\Documents\discordRedbot\quotes.sqlite"


def insert_quote(server_id, added_by, author_id, quote, channel_id, message_id, image_url=None):
    if image_url is not None:
        sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id, image_url) VALUES(?,?,?,?,?,?,?)'''
        input_string = (
            '{}'.format(server_id), '{}'.format(added_by), '{}'.format(author_id),
            '{}'.format(quote), '{}'.format(channel_id), '{}'.format(message_id),
            '{}'.format(image_url))
    else:
        sql = '''INSERT INTO quotes(server_id,added_by,author_id,quote, channel_id, message_id) VALUES(?,?,?,?,?,?)'''
        input_string = (
            '{}'.format(server_id), '{}'.format(added_by), '{}'.format(author_id),
            '{}'.format(quote), '{}'.format(channel_id), '{}'.format(message_id))
    conn = None
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute(sql, input_string)
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


def get_all_quotes(server_id, member=None):
    conn = None
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        to_ex = ''
        if member is not None:
            to_ex = '''SELECT * FROM quotes where server_id = ? and author_id = ?'''
            cur.execute(to_ex, (server_id, member.id))
        else:
            to_ex = '''SELECT * FROM quotes where server_id = ?'''
            cur.execute(to_ex, (server_id,))
        rows = cur.fetchall()
        return rows
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def get_quotes_added_by(server_id, member):
    conn = None
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        to_ex = '''SELECT * FROM quotes where server_id = ? and added_by = ?'''
        cur.execute(to_ex, (server_id, member.id))
        rows = cur.fetchall()
        return rows
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def delete_quote(server_id, quote_id):
    conn = None
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        sql = 'DELETE FROM quotes WHERE server_quote_id=? and server_id = ?'
        cur.execute(sql, (quote_id, server_id))
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def add_quote_splits(quote_id, server_id, left_split_end, right_split_start):
    quote = get_quote(quote_id, server_id)
    if quote is not None:
        #   check if quote has remix entry
        new_record = False
        updated_record = False
        conn = None
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            to_ex = '''SELECT * FROM remix_split where quote_id=?'''
            cur.execute(to_ex, (quote[0],))

            if cur.fetchone() is None:
                # need to make new record
                if left_split_end is not None:
                    if left_split_end > len(quote[8]) - 1:
                        left_split_end = len(quote[8]) - 1

                if right_split_start is not None:
                    if right_split_start > len(quote[8]):
                        right_split_start = int(len(quote[8])/2)

                split_ex = '''INSERT INTO remix_split (left_split_end, right_split_start, quote_id) VALUES (?,?,?)'''
                cur.execute(split_ex, (left_split_end, right_split_start, quote[0],))
                new_record = True
            else:
                # record exists, update
                if left_split_end is not None and right_split_start is not None:
                    if left_split_end > len(quote[8]) - 1:
                        left_split_end = len(quote[8]) - 1
                    if right_split_start > len(quote[8]) - 1:
                        right_split_start = len(quote[8]) - 1

                    if left_split_end < 0:
                        left_split_end = 0
                    if right_split_start < 0:
                        right_split_start = 0

                    split_ex = '''UPDATE remix_split SET left_split_end = ?, right_split_start = ? WHERE quote_id = ?'''
                    cur.execute(split_ex, (left_split_end, right_split_start, quote[0],))
                    updated_record = True
                elif left_split_end is not None:
                    if left_split_end > len(quote[8]) - 1:
                        left_split_end = len(quote[8]) - 1
                    if left_split_end < 0:
                        left_split_end = 0
                    split_ex = '''UPDATE remix_split SET left_split_end = ? WHERE quote_id = ?'''
                    cur.execute(split_ex, (left_split_end, quote[0],))
                    updated_record = True
                elif right_split_start is not None:
                    if right_split_start > len(quote[8]) - 1:
                        right_split_start = len(quote[8]) - 1
                    if right_split_start < 0:
                        right_split_start = 0
                    split_ex = '''UPDATE remix_split SET right_split_start = ? WHERE quote_id = ?'''
                    cur.execute(split_ex, (right_split_start, quote[0],))
                    updated_record = True
                else:
                    raise NoSplitValuesException

            conn.commit()
            return [new_record, updated_record]
        finally:
            conn.close()
    else:
        raise QuoteNotFoundException


def get_quote_splits(quote_id, server_id):
    quote = get_quote(quote_id, server_id)
    if quote is not None:
        #   check if quote has remix entry
        conn = None
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            to_ex = '''SELECT * FROM remix_split where quote_id=?'''
            cur.execute(to_ex, (quote[0],))
            split_data = cur.fetchone()
            if split_data is not None:
                return [split_data[1], split_data[2]]
            else:
                return None
        finally:
            conn.close()
    else:
        raise QuoteNotFoundException


def remove_quote_splits(quote_id, server_id, keep_left, keep_right):
    quote = get_quote(quote_id, server_id)
    conn = None
    records_change = False
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        if not keep_left and not keep_right:
            to_ex = '''DELETE FROM remix_split where quote_id = ?'''
            cur.execute(to_ex, (quote[0],))
            records_change = True
        elif keep_right:
            to_ex = '''UPDATE remix_split SET left_split_end = ? where quote_id = ?'''
            cur.execute(to_ex, (None, quote[0],))
            records_change = True
        elif keep_left:
            to_ex = '''UPDATE remix_split SET right_split_start = ? where quote_id = ?'''
            cur.execute(to_ex, (None, quote[0],))
            records_change = True
        conn.commit()
        return records_change
    finally:
        conn.close()

