import discord
import requests
import json

set_list, series_list = [], []

def get_values(site):
    response_API = requests.get(site)
    response_code = response_API.status_code

    if response_code == 200:
        data = response_API.text
        slug_list = json.loads(data)

        value_list = []
        for slug_dct in slug_list:
            for k, v in slug_dct.items():
                value_list.append(v)
        return value_list
    else:
        print('Unable to reach endpoint {} - Response code: {}').__format__(response_API.url, response_code)

def update_values():
    global set_list
    set_list = get_values('https://goddesstcg.com/wp-json/wp/v2/set?per_page=20&_fields=slug')
    global series_list 
    series_list = get_values('https://goddesstcg.com/wp-json/wp/v2/series?per_page=300&_fields=slug')

update_values()

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global set_list
    global series_list 

    if message.author == client.user:
        return

    # Search command
    if message.content.startswith('?search'):
        print('search requested by {}'.format(message.author))
        await create_search_url(message)

    elif message.content.startswith('?help'):
        print('help requested by {}'.format(message.author))
        await message.reply(f'Use the **"?search set series title"** command to search for cards. Each search option should be seperated by a space. \n Set should be **without** hyphens e.g. ns02m02 \n Series should be **with** hyphens e.g. sword-art-online \n' + 
        'Title should be the character name e.g. asuna')

    elif message.content.startswith('?list'):
        print('list requested by {}'.format(message.author))
        await message.reply('Set list: \n {}'.format(set_list))

        split_list = list()
        split_num = int((len(series_list)/4)+1)
        for i in range(0, len(series_list), split_num):
            split_list.append(series_list[i:i+split_num])
        for count, split_series_list in enumerate(split_list):
            await message.reply('Series List Part {}: \n {}'.format(count+1, split_series_list))

    elif message.content.startswith('?update'):
        print('update requested by {}'.format(message.author))
        await message.reply('Updating Lists')
        update_values()
 
async def create_search_url(message):
    global set_list
    global series_list 

    print(set_list)
    print(series_list)
    split_message = str.split(message.content)
    split_message.pop(0)

    count = len(split_message)
    print('Count: ' + str(count))
    if count > 3:
        await message.reply('Too many search options provided. Maximum of 3 allowed')
    elif count == 0:
        await message.reply('No search options provided. You can search by any combination of set, series and title')
    elif count <= 3 and count > 0:
        set_name = ''
        series = ''
        title = ''
        for option in split_message:
            lower_option = option.lower()
            if lower_option in set_list:
                set_name = lower_option
                split_message.remove(option)
                break
        
        for option in split_message:
            lower_option = option.lower()
            if lower_option in series_list:
                series = lower_option
                split_message.remove(option)
                break
        
        for option in split_message:
            option = option.lower()
            title = option
        
        response = 'https://goddesstcg.com/search/?sort=set-number&set={}&series={}&title={}'.format(set_name, series, title)
        print(response)
        await message.reply(response)

# Put bot token here
client.run('bot token here')
