from datetime import datetime
import discord
import sqlite3
from sqlite3 import Error
from prettytable import PrettyTable

incorrect_format = 'Unable to add score, incorrect format provided.'

sql_create_squirdles_table = """ CREATE TABLE IF NOT EXISTS squirdles (
                                        message_id text PRIMARY KEY,
                                        user_id text NOT NULL,
                                        daily_number text NOT NULL,
                                        score text NOT NULL,
                                        created_date text
                                    ); """

sql_check_squirdle_message = """ SELECT * FROM squirdles
                                 WHERE message_id = ?
                                 ; """

sql_check_daily_message = """ SELECT * FROM squirdles
                              WHERE user_id = ? AND daily_number = ?
                              ; """

sql_insert_daily_message = """ INSERT INTO squirdles (message_id, user_id, daily_number, score, created_date)
                               VALUES (?,?,?,?,?)
                               ; """

sql_update_daily_score = """ UPDATE squirdles
                             SET score = ?
                             WHERE user_id = ? AND daily_number = ?
                             ; """

sql_squirdle_leaderboard = """ SELECT user_id, avg(score) FROM squirdles
                               GROUP BY user_id
                               ORDER BY avg(score)
                              ; """

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print('Connected to database.')
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print('Create table command executed.')
    except Error as e:
        print(e)

def check_message_id(conn, message_id):
    cur = conn.cursor()
    cur.execute(sql_check_squirdle_message, (message_id,))
    rows = cur.fetchall()
    if len(rows) < 1:
        return False
    return True

def check_daily_message(conn, user_id, daily_number):
    cur = conn.cursor()
    cur.execute(sql_check_daily_message, (user_id, daily_number,))
    rows = cur.fetchall()
    if len(rows) > 0:
        return True
    return False

def insert_daily_message(conn, message_id, user_id, daily_number, score):
    cur = conn.cursor()
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    cur.execute(sql_insert_daily_message, (message_id, user_id, daily_number, score, date_time,))
    conn.commit()
    return check_daily_message(conn, user_id, daily_number)

async def update_daily_score(conn, message, user_id):
    split_update_message = message.content.split(' ')
    if len(split_update_message) != 3:
        print('Wrong amount of parameters provided.')
        return
    
    daily_number = split_update_message[1]
    score = split_update_message[2]
    if not check_for_int(message, daily_number, score):
        return
    cur = conn.cursor()
    cur.execute(sql_update_daily_score, (score, user_id, daily_number,))
    conn.commit()
    await message.reply('Daily #{0} set to score of {1}'.format(daily_number, score))

def show_leaderboard(conn, client):
    cur = conn.cursor()
    cur.execute(sql_squirdle_leaderboard)
    rows = cur.fetchall()
    t = PrettyTable(['User ID', 'Average Score'])
    for row in rows:
        user = client.get_user(int(row[0]))
        new_row = (user.display_name, row[1])
        t.add_row(new_row)
    return t

async def check_for_int(message, daily_number, score):
    try:
        int(daily_number)
        int(score)
        return True
    except ValueError:
       print('Daily Number: {0}, Score: {1}'.format(daily_number, score))
       await message.reply(incorrect_format)
       return False

conn = create_connection('squirdle_messages.db')
if conn is not None:
    # create squirdles table
    create_table(conn, sql_create_squirdles_table)
else:
    print("Unable to create database connection.")

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    user_id = message.author.id
    # Do some message checks
    if message.author == client.user:
        return

    if message.content.startswith('?leaderboard'):
        table = show_leaderboard(conn, client)
        await message.reply(table)
        return

    if message.content.startswith('?update'):
        await update_daily_score(conn, message, user_id)
        print('Score updated.')
        return

    if not message.content.startswith('Squirdle'):
        return

    if check_message_id(conn, message.id):
        return
    
    split_message = message.content.split('-')
    if len(split_message) != 2:
        print('Incorrect message.')
        await message.reply(incorrect_format)
        return
    counter = 0
    for m in split_message:
        split_message[counter] = m.strip(' ')
        counter += 1
    # First character in 2nd half of message contains score
    score = (split_message[1])[0]

    daily_number_split = split_message[0].split(' ')
    if len(daily_number_split) !=3:
        print('Incorrect message.')
        await message.reply(incorrect_format)
        return
    # 3rd part of 1st half of message contains daily number
    daily_number = daily_number_split[2]

    if not await check_for_int(message, daily_number, score):
        return

    if check_daily_message(conn, user_id, daily_number):
        print('Daily score already exists for {}.'.format(message.author.name))
        await message.reply('Daily score already exists for {}.'.format(message.author.name))
        return

    if insert_daily_message(conn, message.id, user_id, daily_number, score):
        print('New Result Added. Daily: {}, Score: {}.'.format(daily_number, score))
    else:
        print('Unable to add new result.')


client.run('bot token here')
