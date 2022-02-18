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

sql_check_user_scores = """ SELECT daily_number, score FROM squirdles
                            WHERE user_id = ?
                            ORDER BY daily_number + 0
                            ; """

sql_check_daily_score = """ SELECT daily_number, score FROM squirdles
                              WHERE user_id = ? AND daily_number = ?
                              ; """

sql_insert_daily_message = """ INSERT INTO squirdles (message_id, user_id, daily_number, score, created_date)
                               VALUES (?,?,?,?,?)
                               ; """

sql_remove_daily_score = """ DELETE FROM squirdles
                             WHERE user_id = ? AND daily_number = ?
                             ; """

sql_update_daily_score = """ UPDATE squirdles
                             SET score = ?
                             WHERE user_id = ? AND daily_number = ?
                             ; """

sql_squirdle_leaderboard = """ SELECT user_id, avg(score), count(user_id) FROM squirdles
                               GROUP BY user_id
                               ORDER BY avg(score), count(user_id) DESC
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

def check_daily_score(conn, user_id, daily_number):
    cur = conn.cursor()
    cur.execute(sql_check_daily_score, (user_id, daily_number,))
    rows = cur.fetchall()
    return rows

def insert_daily_message(conn, message_id, user_id, daily_number, score):
    cur = conn.cursor()
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    cur.execute(sql_insert_daily_message, (message_id, user_id, daily_number, score, date_time,))
    conn.commit()
    return check_daily_score(conn, user_id, daily_number)

async def update_daily_score(conn, message, user_id):
    split_update_message = message.content.split(' ')
    if len(split_update_message) != 3:
        print('Wrong amount of parameters provided.')
        return
    
    daily_number = split_update_message[1]
    score = split_update_message[2]
    daily_score = check_daily_score(conn, user_id, daily_number)
    if len(daily_score) < 1:
        await message.reply('Daily #{0} does not exist for {1}.'.format(daily_number, message.author.name))
        return
    if not await check_for_int(message, daily_number, score):
        return
    cur = conn.cursor()
    cur.execute(sql_update_daily_score, (score, user_id, daily_number,))
    conn.commit()
    await message.reply('Daily #{0} set to score of {1}'.format(daily_number, score))

async def remove_daily_score(conn, message, user_id):
    split_update_message = message.content.split(' ')
    if len(split_update_message) != 2:
        print('Wrong amount of parameters provided.')
        return
    
    daily_number = split_update_message[1]
    if not await check_for_int(message, daily_number, 0):
        return
    daily_score = check_daily_score(conn, user_id, daily_number)
    if len(daily_score) < 1:
        await message.reply('Daily #{0} does not exist for {1}.'.format(daily_number, message.author.name))
        return
    cur = conn.cursor()
    cur.execute(sql_remove_daily_score, (user_id, daily_number,))
    conn.commit()
    await message.reply('Daily #{0} removed for user {1}'.format(daily_number, message.author.name))

def show_user_score(conn, user_id):
    cur = conn.cursor()
    cur.execute(sql_check_user_scores, (user_id,))
    rows = cur.fetchall()
    t = PrettyTable(['Daily #', 'Score'])
    for row in rows:
        t.add_row(row)
    return t

def get_leaderboard(conn):
    cur = conn.cursor()
    cur.execute(sql_squirdle_leaderboard)
    rows = cur.fetchall()
    return rows

async def send_leaderboard(message, rows):
    embed = discord.Embed(title='Squirdle Leaderboard')
    users = ''
    scores = ''
    days = ''
    for row in rows:
        user = client.get_user(int(row[0]))
        username = user.name
        users += username + '\n'
        scores += str(float("{0:.2f}".format(row[1]))) + '\n'
        days += str(row[2]) + '\n'

    embed.add_field(name='User ID', value=users, inline=True)
    embed.add_field(name='Average Score', value=scores, inline=True)
    embed.add_field(name='Total Days', value=days, inline=True)
    await message.reply(embed=embed)

async def send_score(message, row):
    daily_number = row[0]
    score = row[1]
    embed = discord.Embed(title='Daily Score')
    embed.add_field(name='Daily #', value=daily_number, inline=True)
    embed.add_field(name='Score', value=score, inline=True)
    await message.reply(embed=embed)

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
        rows = get_leaderboard(conn)
        await send_leaderboard(message, rows)
        return

    if message.content.startswith('?update'):
        await update_daily_score(conn, message, user_id)
        print('Score updated.')
        return
    
    if message.content.startswith('?remove'):
        await remove_daily_score(conn, message, user_id)
        print('Score removed.')
        return

    if message.content.startswith('?scores'):
        table = show_user_score(conn, user_id)
        await message.reply(table)
        return

    if message.content.startswith('?score'):
        score_message_split = message.content.split(' ')
        try:
            daily_number = score_message_split[1]
        except:
            print(incorrect_format)
            await message.reply(incorrect_format) 
            return

        if not await check_for_int(message, daily_number, 0):
            return
        
        daily_score_rows = check_daily_score(conn, user_id, daily_number)
        if len(daily_score_rows) < 1:
            await message.reply('Daily #{0} does not exist for {1}.'.format(daily_number, message.author.name))
            return
        daily_score_row = daily_score_rows[0]
        await send_score(message, daily_score_row)
        #daily_score = daily_score_rows[0]
        #await message.reply('Daily #{0} has a score of {1}'.format(daily_score[0], daily_score[1]))
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

    check_score = check_daily_score(conn, user_id, daily_number)
    if len(check_score) > 0:
        print('Daily score already exists for {}.'.format(message.author.name))
        await message.reply('Daily score already exists for {}.'.format(message.author.name))
        return

    new_insert = insert_daily_message(conn, message.id, user_id, daily_number, score)
    if len(new_insert) > 0:
        print('New Result Added. Daily: {}, Score: {}.'.format(daily_number, score))
    else:
        print('Unable to add new result.')


client.run('bot token here')
