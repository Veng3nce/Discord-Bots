import discord
import requests
import json
import re

set_list, series_list, rarity_list = [], [], []

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
    try:
        global set_list
        global series_list 
        global rarity_list
        set_list = get_values('https://goddesstcg.com/wp-json/wp/v2/set?per_page=50&_fields=slug')
        series_list = get_values('https://goddesstcg.com/wp-json/wp/v2/series?per_page=300&_fields=slug')
        rarity_list = get_values('https://goddesstcg.com/wp-json/wp/v2/rarity?per_page=50&_fields=slug')

    except:
        print('Unable to access API')


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
        print(message.content)
        await create_search_url(message)

    elif message.content.startswith('?help'):
        print('help requested by {}'.format(message.author))
        await message.reply(f'Use the **"?search set series rarity title"** command to search for cards. e.g. ?search ns10m01 sword-art-online ntr asuna \n' + 
        'Each search option should be seperated by a space. \n' + 
        'Set should be **without** hyphens e.g. ns10m01 \n' + 
        'Series should be **with** hyphens e.g. sword-art-online \n' + 
        'Rarity should be the card rarity e.g. ntr \n' + 
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

        await message.reply('Rarity list: \n {}'.format(rarity_list))

    elif message.content.startswith('?update'):
        print('update requested by {}'.format(message.author))
        await message.reply('Updating lists')
        update_values()
 
async def create_search_url(message):
    global set_list
    global series_list
    global rarity_list

    min_value = 0
    max_value = 4
    split_message = str.split(message.content)
    split_message.pop(0)

    count = len(split_message)
    if count > max_value:
        await message.reply('Too many search options provided. Maximum of {} allowed'.format(max_value))
    elif count == min_value:
        await message.reply('No search options provided. You can search by any combination of set, series, rarity and title')
    elif count <= max_value and count > min_value:
        set_name = ''
        series = ''
        rarity = ''
        title = ''
        # SET CHECK
        for option in split_message:
            lower_option = option.lower()
            # Find all instances of numbers in string
            if lower_option.startswith('ns'):
                numbers = re.findall('[0-9]?[0-9]', lower_option)

                # Remove duplicate values
                numbers = list(dict.fromkeys(numbers))

                # Fill with 0 if less than 2 digits
                for count, number in enumerate(numbers):
                    if(int(number) < 10):
                        lower_option = lower_option.replace(numbers[count], number.zfill(2))
                        lower_option = lower_option.replace('00', '0')

                        #Remove the 0 from numbers the front if larger than 2 and starts with 0
                        too_big = re.findall('[0][0-9][0-9]', lower_option)
                        for num in too_big:
                            split_num = [char for char in num]
                            lower_option = lower_option.replace(num, '{}{}'.format(split_num[1],split_num[2]))
                
            if lower_option in set_list:
                # Assign value and remove from 
                set_name = lower_option
                split_message.remove(option)
                break
        
        # SERIES CHECK
        for option in split_message:
            lower_option = option.lower()
            if lower_option in series_list:
                series = lower_option
                split_message.remove(option)
                break
        
        # RARITY CHECK
        for option in split_message:
            lower_option = option.lower()
            if lower_option in rarity_list:
                rarity = lower_option
                split_message.remove(option)

        # Take whatever is left and assign the final value to title
        for option in split_message:
            option = option.lower()
            title = option
        
        response = 'https://goddesstcg.com/search/?sort=set-number&set={}&series={}&title={}&rarity={}'.format(set_name, series, title, rarity)
        print(response)
        await message.reply(response)

# Put bot token here
client.run('bot token here')
