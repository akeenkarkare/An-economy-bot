from discord.ext import commands
import discord 
import asyncio
import praw
from praw.models.listing.mixins import subreddit
from praw.reddit import Subreddit
import random 
from SimpleEconomy import Seco
import os 
from discord.ext.commands import cooldown, BucketType
from random import randint

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True)
client = commands.Bot(command_prefix="]", intents = intents)
seco = Seco(client,"simple economy api key","table name",def_bal=100,def_bank=400)

os.chdir("path name for the file")

@client.remove_command("help")

#printing that bot is online
@client.event
async def on_ready():
    print("Bot is online.")
    stream = discord.Streaming(
        name="whatever you want the status as",
        url="sample video url")
    await client.change_presence(activity=stream)

#auto role stuff here
@client.event
async def on_member_join(ctx):
    autorole = discord.utils.get(ctx.guild.roles, name = "Member")
    await ctx.add_roles(autorole)

#balance command
@client.command(aliases=["bal"])
async def balance(ctx):
    balance=await seco.get_balance(ctx.author.id)
    e=discord.Embed(
        title="Balance",
        description=f"Your balance is: {balance}₿"
    )
    await ctx.send(embed=e)

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

#beg cooldown
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
        text+=str(leaderboard.index(person)+1) +") "+client.get_user(int(person["userid"])).display_name+" - "+str(person["balance"])+"\n"

    e=discord.Embed(
        title="Leaderboard",
        description=text)
    await ctx.send(embed=e)

#shop command
@client.command()
async def shop(ctx):
    e=discord.Embed(
        title="Shop", color=0x66ff99,
        description=f"1) Bread - 50₿\n2) Cookie - 100₿\n\nDo ]buy <item> to buy!"
    )
    await ctx.send(embed=e)

#items command
@client.command(aliases=["inv"])
async def inventory(ctx):
    user=await seco.get("shop",userid=ctx.author.id)
    if user==None:
        await seco.insert("shop",userid=ctx.author.id,cookies=0,bread=0)
        user=await seco.get("shop",userid=ctx.author.id)
    
    
    cookies=user["cookies"]
    bread=user["bread"]
    await ctx.send(f"Cookies: {cookies}\nBread: {bread}")

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
                        colour=discord.Colour.green(),
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
                colour=discord.Colour.green(),
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
                colour=discord.Colour.green(),
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
    dice_embed = discord.Embed(title="Dice Roll",description=dice_random,color=0x66ff99)
    await ctx.send(embed=dice_embed)

#clear command
@client.command()
async def clear(ctx, amount = 1):
    await ctx.channel.purge(limit = amount + 1) 
    await ctx.send(f"Cleared {amount} messages.")

#ping command
@client.command()
async def ping(ctx):
    await ctx.send(f"Ping: {round(client.latency * 1000)}ms")

#ban command
@client.command()
async def ban(ctx, member: discord.Member, *, reason = 'They were annoying lmao'):
    if ctx.message.author.guild_permissions.administrator:
        await member.ban(reason = reason)
        await asyncio.sleep(1)
        await ctx.send(f"Banned {member}. Reason: {reason}")
    else:
        await ctx.send(f"{ctx.message.author} - You peasant, you lack the permission to do this.")
        await asyncio.sleep(3)

#When bot arrives
@client.event
async def on_guild_join(guild):
    live_serv_p = client.get_channel("channel id")
    await live_serv_p.send(f"Added to {guild.name} (Members - {str(guild.member_count)}). I'm in {str(len(client.guilds))} servers now. ")

#When bot leaves
@client.event
async def on_guild_leave(guild):
    live_serv_p = client.get_channel("channel id")
    await live_serv_p.send(f"Removed from {guild.name} (Members - {str(guild.member_count)}). I'm in {str(len(client.guilds))} servers now. ")

#Hi command
@client.command()
async def hi(ctx):
    hi_list = ["Go away I don't want to talk", "Hello lol", "Never gonna give you up never gonna let you down never gonna run around and desert you"]
    random_hi = random.choice(hi_list)
    hi_embed = discord.Embed(title=f'You greeted me?',description=random_hi, color=0x66ff99)
    await ctx.send(embed=hi_embed)    

#help command
@client.command()
async def help(ctx):
    helpembed=discord.Embed(title=f'HELP', color=0x66ff99, description="")
    helpembed.add_field(name="Categories", value="Economy\nReddit\nRandom Stuff + Moderation", inline=False)
    helpembed.add_field(name="Commands:", value="]help_economy\n]help_reddit\n]help_RSPM", inline=False)
    await ctx.send(embed=helpembed)

#help economy command
@client.command(aliases=["economy"])
async def help_economy(ctx):
    ecoembed=discord.Embed(title=f'HELP: ECONOMY', color=0x66ff99, description="Economy Commands.")
    ecoembed.add_field(name="]beg", value="Begs for batatas.", inline=False)
    ecoembed.add_field(name="]buy <item>", value="Buys an item.", inline=False)
    ecoembed.add_field(name="]bal", value="Shows balance.", inline=False)
    ecoembed.add_field(name="]leaderboard", value="Shows the leaderboard.", inline=False)
    ecoembed.add_field(name="]items", value="Shows your items.", inline=False)
    ecoembed.add_field(name="]shop", value="Shows the shop.", inline=False)
    ecoembed.add_field(name="]search", value="Searches in a car/house/boat.", inline=False)
    await ctx.send(embed=ecoembed)

#help reddit command
@client.command(aliases=["reddit"])
async def help_reddit(ctx):
    redembed=discord.Embed(title=f'HELP: REDDIT', color=0x66ff99, description="Reddit Commands.")
    redembed.add_field(name="]dog", value="Shows a dog.", inline=False)
    redembed.add_field(name="]cat", value="Shows a cat.", inline=False)
    redembed.add_field(name="]aww", value="Shows a pic to make you go aww.", inline=False)
    redembed.add_field(name="]meme", value="Shows a meme.", inline=False)
    await ctx.send(embed=redembed)

#help command
@client.command(aliases=["rspm"])
async def help_RSPM(ctx):
    rspmembed=discord.Embed(title=f"HELP: RSPM", color=0x66ff99, description="RSPM Commands.")
    rspmembed.add_field(name="]hi", value="Greets you back.", inline=False)
    rspmembed.add_field(name="]clear <value>", value="Clears messages.", inline=False)
    rspmembed.add_field(name="]say <type what you wanna say>", value="The bot says what you just said.", inline=False)
    rspmembed.add_field(name="]ban <user>", value="Bans people. (Unban Manually)", inline=False)
    rspmembed.add_field(name="]ping", value="Tells you the bot ping.", inline=False)
    rspmembed.add_field(name="]diceroll", value="Rolls between 1-6.", inline=False)
    await ctx.send(embed=rspmembed)

client.run("token")