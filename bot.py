from secrets import token_urlsafe
import discord
from discord.ext import commands
import requests
import json

client = commands.Bot(command_prefix='!')
@client.event
async def on_ready():
  print('Bot is ready')

@client.command()
async def ping(ctx):
  await ctx.send('Pong')


@client.command()
async def name(ctx):
  await ctx.send(f'{ctx.author}')

@client.command()
async def createtourney(ctx, tourney):
    guild = ctx.message.guild
    if ctx.author.guild_permissions.manage_channels:
        await guild.create_text_channel(name=f'{tourney}')
        response = requests.post('http://localhost:8080/tournament/create', json={ "name": f'{tourney}', "type": "round robin", "rankedBy": "points scored", "startAt": "2022-06-22T03:00:00"})
        obj = json.loads(response.text)
        tourney_id = obj["id"]

        f=open('id.txt', 'w')
        f.write(str(tourney_id))
        f.close()
        await ctx.send(response.text)


@client.command()
async def addme(ctx):
  username = str(ctx.author).split('#')[0]
  f= open("id.txt","r")
  tourney_id = f.read()
  f.close()
  response = requests.post('http://localhost:8080/tournament/add-players', json = {"id": f'{tourney_id}', "playerList": [f'{username}']})
  await ctx.send(response.text)


client.run('OTg5MDQ0OTU3NTAxMzU4MTAw.GX--PX.e9JS1HKOshKahPcT7q5NKBnghO9SJagIi4XC4o')
