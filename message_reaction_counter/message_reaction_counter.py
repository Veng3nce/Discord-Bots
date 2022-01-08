import discord
import json

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Only start command if selected user runs it
    if message.content == '$run' and message.author.id == 243901055501467649:
        data = {}
        guild = message.guild

        print('Discord name: ' + guild.name)
        print('--------------------------------------------------')

        # Loop through each channel in discord
        for channel in guild.text_channels:
            print('reading channel: ' + channel.name)
            
            data[channel.name] = []
            message_counter = 0
            reacted_counter = 0

            # Loop through each message in channel
            async for message in channel.history(limit=None):
                message_counter +=1 
                reaction_counter = 0

                # Count the total number of reactions on the message
                for reaction in message.reactions:
                    reaction_counter += reaction.count
                # Write the message to file if it has enough reactions
                if reaction_counter > 0:
                    reacted_counter += 1

                    # Format data and append
                    count = str(reaction_counter)
                    id = str(message.id)
                    date = str(message.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                    data[channel.name].append({
                        'id': id,
                        'channel': channel.name,
                        'author': message.author.name,
                        'date': date,
                        'reactions': count,
                        'content': message.content
                    })
                    
                        
            print(channel.name + ' message count: ' + str(message_counter))
            print(channel.name + ' reacted message count: ' + str(reacted_counter))
            print('--------------------------------------------------')
            
    # Output to formatted json file 
    with open('top_reactions.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    print('counting complete')

# Put bot token here
client.run('bot token here')
