import discord
import json

client = discord.Client()

# Will clean these up when ready to be deployed
set_list = ['ns02', 'ns02m02', 'ns02m03', 'ns02m04', 'ns03', 'ns04', 'ns05m01', 'ns05m02', 'ns05m03', 'ns05m04', 'ns10m01']
series_list = ["86", "a certain magical index", "accel world", "akame ga kill!", "akashic records of bastard magic instructor", 
"aldnoah.zero", "amagi brilliant park", "angel beats!", "angels of death", "anohana: the flower we saw that day", "another", 
"aria the scarlet ammo", "arknights", "attack on titan", "azur lane", "bang dream!", "bayonetta", "ben-to", "beyond the boundary", 
"black bullet", "black rock shooter", "bleach", "bofuri: i don't want to get hurt, so i'll max out my defense.", "bungo stray dogs", 
"cardcaptor sakura", "cells at work!", "chainsaw man", "charlotte", "chivalry of a failed knight", "chobits", "citrus", "clannad", 
"classroom of the elite", "code geass", "dagashi kashi", "danganronpa", "darker than black", "darling in the franxx", "date a live", 
"dead or alive", "death note", "demon slayer", "detective conan", "do you love your mom and her two-hit multi-target attacks?", 
"dropkick on my devil!", "eromanga sensei", "eva", "expelled from paradise", "fairy tail", "fate/apocrypha", "fate/extella", 
"fate/extra", "fate/grand order", "fate/grand order babylonia", "fate/grand order camelot", "fate/kaleid liner prisma☆illya", 
"fate/labyrinth", "fate/stay night", "fate/zero", "final fantasy", "fire force", "food wars! shokugeki no soma", "fox spirit matchmaker", 
"full metal panic!", "fullmetal alchemist", "future diary", "gabriel dropout", "gate", "genshin impact", "ghost in the shell", 
"gintama", "girls frontline", "girls und panzer", "goblin slayer", "god's blessing on this wonderful world!", "golden kamuy", 
"gosick", "granblue fantasy", "grimgar: ashes and illusions", "ground control to psychoelectric girl", "guilty crown", "gunbuster", 
"gundam build divers re:rise", "gurren lagann", "haganai: i don't have many friends", "hell girl", "high school of the dead", 
"himouto! umaru-chan", "honkai impact", "how to raise a boring girlfriend", "hyouka", "hyperdimension neptunia", "in/spectre", 
"interspecies reviewers", "inuyasha", "is it wrong to try to pick up girls in a dungeon?", "is the order a rabbit?", "is this a zombie?", 
"island", "jabami", "jojo's bizarre adventure", "jujutsu kaisen", "k", "k-on!", "kabaneri of the iron fortress", 
"kaguya-sama: love is war", "kakushigoto", "kantai collection", "kara no kyoukai", "katanagatari", "kill la kill", 
"lagrange: the flower of rin-ne", "laid-back camp", "land of the lustrous", "league of legends", "legend of zelda", "liar liar", 
"little witch academia", "love live!", "love, chunibyo & other delusions!", "lucky star", "macross", "magical girl lyrical nanoha", 
"mahou shoujo madoka magica", "masamune-kun's revenge", "miss kobayashi's dragon maid", "monogatari series", "monthly girl's nozaki-kun", 
"ms. vampire who lives in my neighborhood", "mushoku tensei: jobless reincarnation", "my hero academia", "my next life as a villainness", 
"my teen romantic comedy snafu", "my youth romantic comedy is wrong as i expected", "nagi-asu: a lull in the sea", "naruto", "new game!", 
"nier: automata", "nisekoi: fake love", "no game no life", "nyaruko: crawling with love!", "one piece", "one punch man", "oreimo", 
"our last crusade or the rise of a new world", "overlord", "overwatch", "panty & stocking with garterbelt", "plastic memories", 
"pokemon", "princess connect re:dive", "princess principal", "problem children are coming from another world, aren't they?", 
"psycho-pass", "puella magi madoka magica", "puella magi suzune magica", "punishing: gray raven", 
"rascal does not dream of bunny girl senpai", "re:creators", "re:zero", "red:pride of eden", "rent-a-girlfriend", "resident evil", 
"revue-starlight", "rozen maiden", "rurouni kenshin", "rwby", "sailor moon", "saki", "school days", "school-live-", "seint seiya", 
"senki zesshō symphogear", "seraph of the end", "shadows house", "shakugan no shana", "shin chuuka ichiban!", "sky of connection", 
"so i'm a spider, so what?", "sound! euphonium", "spice and wolf", "ssss. gridman", "ssss.dynazenon", "starcraft ii", "steins; gate", 
"street fighter", "super mario", "sword art online", "tada never falls in love", "tamako market", "teasing master takagi-san", 
"that time i got reincarnated as a slime", 'the "hentai" prince and the stony cat', "the ancient magus' bride", 
"the angel next door spoils me rotten", "the day i became a god", "the demon girl next door", "the detective is already dead", 
"the disastrous life of saiki k", "the familiar of zero", "the flower we saw that day", "the garden of sinners", 
"the hero is overpowered by overly cautious", "the idolm@ster", "the journey of elaina", "the king of fighters", 
"the legend of sword and fairy (chinese paladin)", "the melancholy of haruhi suzumiya", "the pet girl of sakurasou", 
"the quintessential quintuplets", "the rising of the shield hero", "the ryuo's work is never done", "the witcher", "to love-ru", 
"tokyo ghoul", "tokyo ravens", "tomb raider", "tonikawa: over the moon for you", "toradora", "touhou project", 
"uma musume: pretty derby", "unbreakable machine-doll", "urara meirochou", "violet evergarden", "vocaloid", "vsinger", 
"wandering witch: the journey of elaina", "wataten!: an angel flow down to me", "we never learn!: bokuben", "weathering with you", 
"welcome-to-demon-school-iruma-kun", "when they cry", "white album 2", "working !!", "world of warcraft", 
"worldend: what do you do at the end of the world? are you busy? will you save us?", "your lie in april", "your name", 
"yu-gi-oh!", "yuuki yuuna is a hero", "zombieland saga"]

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Search command
    if message.content.startswith('$search'):
        await create_search_url(message)
        
async def create_search_url(message):
    split_message = str.split(message.content)
    split_message.pop(0)

    count = len(split_message)
    print('Count: ' + str(count))
    if count > 3:
        await message.reply('Too many search options provided. Maximum of 3 allowed')
    elif count == 0:
        await message.reply('No search options provided. You can search by any combination of set, series and title')
    elif count <= 3 and count > 0:
        for option in split_message:
            if option in set_list:
                set_name = option
                split_message.remove(option)
                break
        else:
            set_name = ''
        for option in split_message:
            replace_option = option.replace('-', ' ')
            replace_option = replace_option.lower()
            if replace_option in series_list:
                series = option
                split_message.remove(option)
                break
            else:
                series = ''
        for option in split_message:
            title = option
        
        response = 'https://goddesstcg.com/search/?sort=set-number&set={}&series={}&title={}'.format(set_name, series, title)
        print(response)
        await message.reply(response)

# Put bot token here
client.run('bot token here')
