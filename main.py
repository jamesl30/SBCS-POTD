import os
import discord
import requests
from discord.ext import commands
from discord import Embed
import asyncio
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("token")

channel = 1072138841969938482
home = 1072138841969938482

#intents setup
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

client = discord.Client(intents=intents)
# URL for the Express server where the daily problem is exposed
EXPRESS_SERVER_URL = 'http://localhost:8000'

current_date = ""

@bot.command()
async def daily(ctx):
    with open("day.txt", 'r') as source_file:
        if source_file.readline() == str(datetime.now(timezone.utc).strftime('%m-%d')):
            return
        else:
            with open("day.txt", 'w') as destination_file:
                destination_file.write(datetime.now(timezone.utc).strftime('%m-%d'))
    try:
        # Fetch the daily problem from the Express server
        response = requests.get(EXPRESS_SERVER_URL)
        
        # Check if the request was successful
        if response.status_code == 200:
            daily_problem = response.json()

            # Prepare the problem message
            #message = str(datetime.today().strftime('%m-%d')) + f": **{daily_problem['question']['title']}**.\n\nQuestion Difficulty: **{daily_problem['question']['difficulty']}**\n\nLink: https://www.leetcode.com{daily_problem['link']}\n\nStatement: {daily_problem['question']['content']}"
            message = f"Statement: {daily_problem['question']['content']}"
            message = message.replace('<strong>', '**')
            message = message.replace('</strong>', '**')
            message = message.replace('<code>', '`')
            message = message.replace('</code>', '`')
            message = message.replace('<code>', '`')
            message = message.replace('</code>', '`')
            message = message[:message.rfind('<strong class="example">Example 1:')]
            message.replace(r'\n', '\n')
            soup = BeautifulSoup(message, "html.parser")
            for data in soup(['script']):
                data.decompose()
            message = ""
            for string in soup.stripped_strings:
                if (string=='.'):
                    message+=(string + '\n\n')
                else:
                    message+=(string+ " ")
            message.strip()
            message = message.replace(' ,', ',')
            message = message.replace(' .', '.')
            message = message.replace(' :', ':')
            message = message.replace(' ]', ']')
            message = message.replace(' [', '[')
            print(message)
            #message = "Good Morning <@&1172561226576965683>\n\nThis is your coding interview problem for " + message + "\n\nHave a great day! Reminder: You can get the Daily Programming role in the <#884991300296925214>\n\nNote: You can discuss about the Question in the following thread: <#1169709010958688376>"
            msg = await bot.get_channel(channel).send("Good Morning <@&1172561226576965683>\n\nThis is your coding interview problem for "
                + str(datetime.now(timezone.utc).strftime('%m-%d'))
                + f": **{daily_problem['question']['title']}**.\n\nQuestion Difficulty: **{daily_problem['question']['difficulty']}**\n\nLink: https://www.leetcode.com{daily_problem['link']}",
                embed=Embed(title=f"{daily_problem['question']['title']}", description = message))
            msg.publish()
            return
        else:
            message = "Sorry, I couldn't fetch the daily problem at the moment."        

    except Exception as e:
        # In case of any error, we provide a fallback message
        message = f"An error occurred while fetching the daily problem: {str(e)}"
        print(message)
    msg = await bot.get_channel(channel).send(message)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await daily(await bot.get_channel(home).send(f'{bot.user} has connected to Discord!'))

bot.run(TOKEN)
