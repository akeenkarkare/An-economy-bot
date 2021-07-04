import discord 
from discord.ext import commands, tasks 
import asyncio
import praw
from praw.models.listing.mixins import subreddit
from praw.reddit import Subreddit
import random 
from SimpleEconomy import Seco
import os 
from discord.ext.commands import cooldown, BucketType
from random import randint
from discord.ext.commands import has_permissions, MissingPermissions
import youtube_dl
import tracemalloc

tracemalloc.start()

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True)
client = commands.Bot(command_prefix="]", intents = intents)
seco = Seco(client,"seco api","table name",def_bal=100,def_bank=400)

@client.remove_command("help")

#printing that bot is online
@client.event
async def on_ready():
    print("Bot is online.")
    activity = discord.Game(name="]help | v1.40 | Watching " + str(len(client.guilds)) + " servers.")
    await client.change_presence(status=discord.Status.idle, activity=activity)
    
#balance command
@client.command(aliases=["bal"])
async def balance(ctx):
    balance=await seco.get_balance(ctx.author.id)
    e=discord.Embed(
        title="Balance",
        description=f"Your balance is: {balance}₿"
    )
    await ctx.send(embed=e)

#daily command
@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    await seco.add_balance(ctx.author.id, 3000)
    embed = discord.Embed(title=f"Here are your daily coins, {ctx.message.author}!", description=f"+3000 added to your wallet.")
    await ctx.send(embed=embed)

#daily_cooldown
@daily.error 
async def daily_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"This, is a DAILY command. Not gonna work if 24 hours haven't passed.",description=f"Try again in {error.retry_after:.2f}s.", color=0x66ff99)
        await ctx.send(embed=em)

#beg command
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def beg(ctx):
    beg_list=["Somebody pitied and gave you ","You got lucky and got "]
    amount=random.randint(0,100)
    text=random.choice(beg_list) + str(amount) +"₿"
    await seco.add_balance(ctx.author.id,amount)
    e=discord.Embed(
        title="Beg",
        description=text
    )
    await ctx.send(embed=e)

#bank command
@client.command()
async def bank(ctx,member : discord.Member):
    bank=await seco.get_bank(member.id)
    await ctx.send(f"**{member.name}**'s bank balance is 🏛 **{bank}**₿")
@bank.error
async def bank_error(ctx, error):
    bank=await seco.get_bank(ctx.author.id)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Your bank balance is 🏛 **{bank}**₿")
    if isinstance(error, commands.BadArgument):
        await ctx.send("Member doesn't exist! Make sure the capitalisations are correct, use @ if that's the case.")

#deposit command
@client.command(aliases=['dep'])
async def deposit(ctx,amount = None):
    if amount == None:
        await ctx.send("Correct usage: `]deposit <amount>`")
        return
    balance=await seco.get_balance(ctx.author.id)
    amount = int(amount)
    if balance < amount:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be a positive integer!')
        return
    await seco.add_balance(ctx.author.id,-1*amount)
    await seco.add_bank(ctx.author.id,amount)
    await ctx.send(f'{ctx.author.mention} You deposited {amount} Batatas.')

#withdraw command
@client.command(aliases=['with'])
async def withdraw(ctx,amount = None):
    if amount == None:
        await ctx.send("Correct usage: `]withdraw <amount>`")
        return
    balance = await seco.get_balance(ctx.author.id)
    bank = await seco.get_bank(ctx.author.id)
    amount = int(amount)
    if bank < amount:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be a positive integer!')
        return
    await seco.add_balance(ctx.author.id,amount)
    await seco.remove_bank(ctx.author.id,amount)
    await ctx.send(f'{ctx.author.mention} You withdrew {amount} balance')


#beg_cooldown
@beg.error 
async def beg_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Slow it down bruh begging too much makes you look like a loser",description=f"Try again in {error.retry_after:.2f}s.", color=0x66ff99)
        await ctx.send(embed=em)

#leaderboard command
@client.command(aliases=["lb"])
async def leaderboard(ctx):
    leaderboard=await seco.leaderboard()
    text=""
    for person in leaderboard:
        text+=str(leaderboard.index(person)+1) +") "+str(await client.fetch_user(int(person["userid"])))+" - "+str(person["balance"])+"\n"
    e=discord.Embed(
        title="Leaderboard (global)",
        description=text
    )
    await ctx.send(embed=e)

#shop command
@client.command()
async def shop(ctx):
    e=discord.Embed(
        title="Shop", color=0x66ff99,
        description=f"1) Bread - 50₿\n2) Cookie - 100₿\n\nDo ]buy <item> to buy!"
    )
    await ctx.send(embed=e)

#amount of servers command
@client.command()
async def servers(ctx):
    server_embed = discord.Embed(title=f"I'm in " + str(len(client.guilds)) + " servers. Let's get to 100!", colour=0x66ff99)
    await ctx.send(embed=server_embed)

#inventory command
@client.command(aliases=["inv"])
async def inventory(ctx):
    user=await seco.get("shop",userid=ctx.author.id)
    if user==None:
        await seco.insert("shop",userid=ctx.author.id,cookies=0,bread=0)
        user=await seco.get("shop",userid=ctx.author.id)
    
    
    cookies=user["cookies"]
    bread=user["bread"]
    embed45 = discord.Embed(title=f"Cookies: {cookies}\nBread: {bread}")
    await ctx.send(embed=embed45)

#buy command
@client.command()
async def buy(ctx,item:str):
    prices={"bread":50,"cookies":100}

    #checking if item is in the dict
    if not item.lower() in prices.keys():
        await ctx.send("Are you dumb there is nothing of that sort in the shop.")
        return
    price=prices[item.lower()]
    balance=await seco.get_balance(ctx.author.id)


    if balance >= price:
        await seco.remove_balance(ctx.author.id,price)

        user=await seco.get("shop",userid=ctx.author.id)
        if user==None:

            user_items={"cookies":0,"bread":0}
            user_items[item.lower()]=1

            await seco.insert("shop",userid=ctx.author.id,**user_items)
            await ctx.send("Purchase was successful!")
        else:
            await seco.update("shop",{item.lower():user[item.lower()]+1})
            await ctx.send("Purchase was successful!")

    else:
        await ctx.send("You don't have enough money!")

#search command
@client.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def search(ctx):
    user = ctx.message.author.id
    balance=await seco.get_balance(user)
    rnum1 = randint(0, 200)
    rnum2 = randint(0, 300)
    rnum3 = randint(0, 70)
    die = randint(0, 5)
    options = {
        "car": rnum1,
        "house": rnum2,
        "boat": rnum3
    }
    e = discord.Embed(
        colour=discord.Colour.green(),
        title="Where do you want to search?",
        description="`car` , `house` , `boat`"
    )
    await ctx.send(embed=e)
    msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    if msg.content.lower() == "car":
        if die == 3:
            letters = "hfkjdsfjahg543t3i598382742uidjksadn"
            fthingy = ""
            for nn in range(0, 10):
                fthingy += random.choice(letters)
            i = True
            await ctx.send(f"Police are chasing you type `{fthingy}`")
            while i:
                msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
                msgco = msg.content.lower()
                if msgco == fthingy:
                    coinremove = round(balance / 1)
                    await ctx.send(f"You escaped! But lost `{coinremove}` batatas from your wallet! :(")
                    await seco.remove_balance(user,coinremove)
                else:
                    e = discord.Embed(
                        color=0x66ff99,
                        title=f"You escaped! But you left your wallet behind so now your balance is gone :("
                    )
                    await ctx.send(embed=e)
                    await seco.remove_balance(user,balance)
                    i = False
        else:
            coinremove = options["car"]
            await ctx.send(f"You found `{coinremove}` batatas from someones car!")
            await seco.add_balance(user,coinremove)
    if msg.content.lower() == "house":
        if die == 3:
            letters = "hfkjdsfjahg543t3i598382742uidjksadn"
            fthingy = ""
            for nn in range(0, 10):
                fthingy += random.choice(letters)
            i = True
            await ctx.send(f"Police are chasing you type `{fthingy}`")
            while i:
                msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
                msgco = msg.content.lower()
                if msgco == fthingy:
                    coinremove = round(balance / 1)
                    await ctx.send(f"You escaped! But lost `{coinremove}` batatas from your wallet! :(")
                    await seco.remove_balance(user,coinremove)
                else:
                    await ctx.send(f"You escaped! But you left your wallet behind so now your balance is gone :(")
                    await seco.remove_balance(user,balance)
                    i = False
        else:
            coinremove = options["house"]
            e = discord.Embed(
                color=0x66ff99,
                title=f"You found `{coinremove}` batatas from someones house! It was a close one!"
            )
            await ctx.send(embed=e)
            await seco.add_balance(user,coinremove)
    if msg.content.lower() == "boat":
        if die == 3:
            letters = "hfkjdsfjahg543t3i598382742uidjksadn"
            fthingy = ""
            for nn in range(0, 10):
                fthingy += random.choice(letters)
            i = True
            await ctx.send(f"Police are chasing you type `{fthingy}`")
            while i:
                msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
                msgco = msg.content.lower()
                if msgco == fthingy:
                    coinremove = round(balance / 1)
                    await ctx.send(f"You escaped! But lost `{coinremove}` batatas from your wallet! :(")
                    await seco.remove_balance(user,coinremove)
                else:

                    await ctx.send(f"You escaped! But you left your wallet behind so now your balance is gone :(")
                    await seco.remove_balance(user,balance)
                    i = False
        else:
            coinremove = options["boat"]
            e = discord.Embed(
                color=0x66ff99,
                title=f"You found `{coinremove}` batatas from a boat!"
            )
            await ctx.send(embed=e)
            await seco.add_balance(user,coinremove)
@search.error
async def search_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = discord.Embed(
            colour=discord.Colour.red(),
            title="Searching too much is gonna get you arrested dummy. Try again in {:.2f}s".format(
                error.retry_after)
        )
        await ctx.send(embed=msg)
    else:
        raise error

#slots command
@client.command(aliases=["Slots"])
@commands.cooldown(1, 7, commands.BucketType.user)
async def slots(ctx, amount:int):                                                                                     
    balance=await seco.get_balance(ctx.author.id)                                                                     
    double = amount * 2                                                                                               
    quadwin = amount *3                                                                                              
    quad = amount * 4                                                                                                 
    if amount <= 0:   
        embed=discord.Embed(title="You can't gamble with less than **1** batata.")                                                                                                
        return await ctx.send(embed=embed)
    if balance == 0:   
        embed=discord.Embed(title="You can't gamble with less than **1** batata.")                                                                                            
        return await ctx.send(embed=embed)
    if balance < amount:     
        embed=discord.Embed(title="Oops, looks like you don't have enough batatas to gamble this amount.")                                                                                        
        await ctx.send(embed=embed) 
    else:
        choice=random.randint(1,100)                                                                                  
        if choice == 100:                                                                                             
            await seco.add_balance(ctx.author.id,100000)                                                              
            embed=discord.Embed(title="You won!",                                                                     
                                description="Congratulations! You hit the jackpot of __**100,000**__ batatas.", 
                                color=0x66ff99)
            embed.add_field(name="** **", value="🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉", inline=False)
            await ctx.send(embed=embed)                                                                               
            return
        if choice <= 95 and choice > 79:                                                                              
            await seco.add_balance(ctx.author.id,amount)                                                              
            embed=discord.Embed(title="You won!",                                                                     
                                description=f"Congratulations! You won __**{double}**__ batatas.", 
                                color=0x66ff99)
            embed.add_field(name="** **", value="🎉🎉🎉🎉🎉🎉", inline=False)
            await ctx.send(embed=embed)
            return
        if choice < 100 and choice > 95:                                                                              
            await seco.add_balance(ctx.author.id,quadwin)                                                           
            embed=discord.Embed(title="You won!",                                                                     
                                description=f"Congratulations! You won __**{quad}**__ batatas.", 
                                color=0x66ff99)
            embed.add_field(name="** **", value="🎉🎉🎉🎉🎉🎉", inline=False)
            await ctx.send(embed=embed)
            return
        if choice <= 79:                                                                                              
            await seco.remove_balance(ctx.author.id,amount)                                                          
            embed=discord.Embed(title="You lost!",                                                                    
                                description=f"Better luck next time, scrub. You lost your __**{amount}**__ batatas.", 
                                color=discord.Color.red())
            await ctx.send(embed=embed)
            return

#slots cooldown
@slots.error 
async def slots_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em1 = discord.Embed(title=f"Playing too much slots will make you go broke",description=f"Try again in {error.retry_after:.2f}s.", color=0x66ff99)
        await ctx.send(embed=em1)


#meme command
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def meme(ctx):
    reddit = praw.Reddit(client_id = "reddit client id",
    client_secret = 'reddit client secret',
    user_agent = 'agent name')
    memes_submission = reddit.subreddit('dankmemes').hot()
    post_to_pick = random.randint(1, 100)
    for i in range(0, post_to_pick):
        submission = next(x for x in memes_submission if not x.stickied)
    await ctx.send(submission.url)

#meme cooldown
@meme.error 
async def meme_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        meme_embed = discord.Embed(title=f"Too many memes will make you question your life",description=f"Try again in {error.retry_after:.2f}s.", color=0x66ff99)
        await ctx.send(embed=meme_embed)

#cat command
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def cat(ctx):
    reddit = praw.Reddit(client_id = "reddit client id",
    client_secret = 'reddit client secret',
    user_agent = 'agent name')
    memes_submission = reddit.subreddit('catpictures').hot()
    post_to_pick = random.randint(1, 100)
    for i in range(0, post_to_pick):
        submission = next(x for x in memes_submission if not x.stickied)
    await ctx.send(submission.url)

#cat cooldown
@cat.error 
async def cat_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        cat_embed = discord.Embed(title=f"Too much cuteness will kill you.",description=f"Try again in {error.retry_after:.2f}s.", color=0x66ff99)
        await ctx.send(embed=cat_embed)

#dog command
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def dog(ctx):
    reddit = praw.Reddit(client_id = "rT_aYy4lKTEAMA",
    client_secret = 'reddit client secret',
    user_agent = 'agent name')
    memes_submission = reddit.subreddit('dogpictures').hot()
    post_to_pick = random.randint(1, 100)
    for i in range(0, post_to_pick):
        submission = next(x for x in memes_submission if not x.stickied)
    await ctx.send(submission.url)

#dog cooldown
@dog.error 
async def dog_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        dog_embed = discord.Embed(title=f"Too much cuteness will kill you.",description=f"Try again in {error.retry_after:.2f}s.", color=0x66ff99)
        await ctx.send(embed=dog_embed)

#aww command
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def aww(ctx):
    reddit = praw.Reddit(client_id = "reddit client id",
    client_secret = 'reddit client secret',
    user_agent = 'agent name')
    memes_submission = reddit.subreddit('aww').hot()
    post_to_pick = random.randint(1, 100)
    for i in range(0, post_to_pick):
        submission = next(x for x in memes_submission if not x.stickied)
    await ctx.send(submission.url)

#aww cooldown
@aww.error 
async def aww_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        aww_embed = discord.Embed(title=f"Too much cuteness will kill you.",description=f"Try again in {error.retry_after:.2f}s.", color=0x66ff99)
        await ctx.send(embed=aww_embed)
    
#say_embed command
@client.command()
@commands.cooldown(1,5, commands.BucketType.user)
async def say_embed(ctx, *, respond):
    respond = respond.replace("(", "")
    respond = respond.replace(")", "")
    respond_embed = discord.Embed(title=respond, color=0x66ff99)
    await ctx.send(embed=respond_embed)

#say command
@client.command()
@commands.cooldown(1,5, commands.BucketType.user)
async def say(ctx, *, respond):
    respond = respond.replace("(", "")
    respond = respond.replace(")", "")
    await ctx.send(respond)

#diceroll command
@client.command(aliases=["dr"])
async def diceroll(ctx):
    dice_list = ["1", "2", "3", "4", "5", "6"]
    dice_random = random.choice(dice_list)
    dice_embed = discord.Embed(title=f"Dice Roll",description=dice_random,color=0x66ff99)
    await ctx.send(embed=dice_embed)

#yes or no command
@client.command(aliases=["Yn", "YesOrNo", "yesorno"])
async def yn(ctx):
    yn_list = ["Yes", "No"]
    yn_random = random.choice(yn_list)
    yn_embed = discord.Embed(title=f"Yes Or No", description=yn_random, color=0x66ff99)
    await ctx.send(embed=yn_embed)

#clear command
@client.command()
async def clear(ctx, amount = 1):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.channel.purge(limit = amount + 1) 
        await asyncio.sleep(1)
        await ctx.send(f"Cleared {amount} messages.")
    else:
        await ctx.send(f"{ctx.message.author} - You peasant, you lack the permission to do this.")
        await asyncio.sleep(3)

#ping command
@client.command()
async def ping(ctx):
    await ctx.send(f"Ping: {round(client.latency * 1000)}ms")

#emojify command
@client.command()
async def emojify(ctx,*,text):
    emojis = []
    for s in text.lower():
        if s.isdecimal():
            num2emo = {'0':'zero', '1':'one', '2':'two', '3':'three', '4':'four', '5':'five', '6':'six', '7':'seven', '8':'eight', '9':'nine'}
            emojis.append(f':{num2emo.get(s)}:')
        elif s.isalpha():
            emojis.append(f':regional_indicator_{s}:')
        else:
            emojis.append(s)
    await ctx.send(' '.join(emojis))

#ban command
@client.command()
async def ban(ctx, member: discord.Member, *, reason = f'They were annoying lmao'):
    if ctx.message.author.guild_permissions.administrator:
        await member.ban(reason = reason)
        await asyncio.sleep(1)
        await ctx.send(f"Banned {member}. Reason: {reason}")
    else:
        await ctx.send(f"{ctx.message.author} - You peasant, you lack the permission to do this.")
        await asyncio.sleep(3)

#Hi command
@client.command()
async def hi(ctx):
    hi_list = ["Whatchu know about rolling down in the deep", "Go away I don't want to talk", "Hello lol", "Never gonna give you up never gonna let you down never gonna run around and desert you"]
    text1 = random.choice(hi_list)
    embed101 = discord.Embed(title=f'You greeted me?',description=text1, color=0x66ff99)
    await ctx.send(embed=embed101)    

#Roast command
@client.command()
async def roast(ctx):
    roast_list = ["Your grades say ‘Marry rich’ but your looks say ‘Try harder’.", "Your mom told you that you could become anything. Yet you still chose to become a disappointment.", "Never gonna give you up never gonna let you down never gonna run around and desert you", "Whatchu know about rolling down in the deep when your brain goes numb you can call that mental freeze"]
    text2 = random.choice(roast_list)
    roast_embed = discord.Embed(title=f'Wanted me to roast you?', description=text2, color=0x66ff99)
    await ctx.send(embed=roast_embed) 

#Vote command
@client.command(aliases=["Vote"])
async def vote(ctx):
    vote_embed = discord.Embed(title="VOTING", description="Vote here: https://discordbotlist.com/bots/asteroid-0398. Rewards to be added.", color=0x66ff99)   
    await ctx.send(embed=vote_embed)
"""
#play command
@client.command()
async def play(ctx, url : str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    voice.play(discord.FFmpegPCMAudio("song.mp3"))

#leave vc command
@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

#pause command
@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")

#resume command
@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")

#stop command
@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
"""
#help command
@client.command(aliases=["help"])
async def Help(ctx):
    embed=discord.Embed(title=f'HELP', color=0x66ff99, description="(Add me in your server! Link here: https://asteroidbot-04.webselfsite.net/)")
    embed.add_field(name=f"Categories", value=f"Economy\nReddit\nRandom Stuff + Moderation", inline=False)
    embed.add_field(name=f"Commands:", value=f"]economy\n]reddit\n]rspm", inline=False)
    await ctx.send(embed=embed)

#help economy command
@client.command(aliases=["economy"])
async def Economy(ctx):
    embed1=discord.Embed(title=f'HELP: ECONOMY', color=0x66ff99, description=f"Economy Commands.\n(Add me in your server! Link here: https://asteroidbot-04.webselfsite.net/)")
    embed1.add_field(name=f"]beg", value=f"Begs for batatas.", inline=False)
    embed1.add_field(name=f"]buy <item>", value=f"Buys an item.", inline=False)
    embed1.add_field(name=f"]bal", value=f"Shows balance.", inline=False)
    embed1.add_field(name=f"]leaderboard", value=f"Shows the leaderboard.", inline=False)
    embed1.add_field(name=f"]inventory", value=f"Shows your items.", inline=False)
    embed1.add_field(name=f"]shop", value=f"Shows the shop.", inline=False)
    embed1.add_field(name=f"]search", value=f"Searches in a car/house/boat.", inline=False)
    embed1.add_field(name=f"]slots", value=f"Play slots.", inline=False)
    embed1.add_field(name=f"]bank <optional user @>", value=f"Check bank balance.", inline=False)
    embed1.add_field(name=f"]with", value=f"Withdraw money from the bank.", inline=False)
    embed1.add_field(name=f"]dep", value=f"Deposit money in the bank.", inline=False)
    embed1.add_field(name=f"]daily", value=f"Gives you 3000 coins, after a 24 hour time gap.", inline=False)
    await ctx.send(embed=embed1)

#help reddit command
@client.command(aliases=["reddit"])
async def Reddit(ctx):
    embed2=discord.Embed(title=f'HELP: REDDIT', color=0x66ff99, description=f"Reddit Commands.\n(Add me in your server! Link here: https://asteroidbot-04.webselfsite.net/)")
    embed2.add_field(name=f"]dog", value=f"Shows a dog.", inline=False)
    embed2.add_field(name=f"]cat", value=f"Shows a cat.", inline=False)
    embed2.add_field(name=f"]aww", value=f"Shows a pic to make you go aww.", inline=False)
    embed2.add_field(name=f"]meme", value=f"Shows a meme.", inline=False)
    await ctx.send(embed=embed2)

#help command
@client.command(aliases=["rspm"])
async def Rspm(ctx):
    embed3=discord.Embed(title=f"HELP: RSPM", color=0x66ff99, description=f"RSPM Commands.\n(Add me in your server! Link here: https://asteroidbot-04.webselfsite.net/)")
    embed3.add_field(name=f"]hi", value=f"Greets you back.", inline=False)
    embed3.add_field(name=f"]clear <value>", value=f"Clears messages.", inline=False)
    embed3.add_field(name=f"]say <type what you wanna say>", value=f"The bot says what you just said.", inline=False)
    embed3.add_field(name=f"]say_embed <type what you wanna say>", value=f"The bot says what you just said, but in an embed.", inline=False)
    embed3.add_field(name=f"]ban <user>", value=f"Bans people. (Unban Manually)", inline=False)
    embed3.add_field(name=f"]ping", value=f"Tells you the bot ping.", inline=False)
    embed3.add_field(name=f"]diceroll", value=f"Rolls between 1-6.", inline=False)
    embed3.add_field(name=f"]servers", value=f"Shows how many servers I am in.", inline=False)
    embed3.add_field(name=f"]vote", value=f"Gives you a link for voting the bot.", inline=False)
    embed3.add_field(name=f"]emojify <type what you wanna emojify>", value=f"Emojifies your texts.", inline=False)
    embed3.add_field(name=f"]yesorno", value=f"Says either Yes or No to settle a bet with your friend.")
    await ctx.send(embed=embed3)

client.run("bot token")
