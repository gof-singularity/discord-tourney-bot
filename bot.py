from secrets import token_urlsafe
import discord
from discord.ext import commands
import requests
import json

tourney_names_ids = []

def convertTuple(tup):
  str = ''
  for item in tup:
      if item.startswith('@') or item.startswith('Round'):
        item = '\n' + item
      
      str = str + item + ' '
  return str


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

        tourney_names_id = {} 
        tourney_names_id["id"] = tourney_id
        tourney_names_id["channelname"] = tourney

        tourney_names_ids.append(tourney_names_id)

        print(tourney_names_ids)

        await ctx.send(response.text)


@client.command()
async def addme(ctx):
  username = str(ctx.author).split('#')[0]
  channel = ctx.channel.name
  tourney_id = -1
  for item in tourney_names_ids:
    if item["channelname"] == channel:
      tourney_id = item["id"]
      print(tourney_id)
      
  if tourney_id == -1:
    print('invalid tourney_id')
    return


  response = requests.post('http://localhost:8080/tournament/add-players', json = {"id": f'{tourney_id}', "playerList": [f'{username}']})
  await ctx.send(response.text)

@client.command()
async def tourneyresult(ctx, *message):
  print(message)
  s = convertTuple(message)

  await ctx.send(s.split('\n'))
  
client.run('OTg5MDQ0OTU3NTAxMzU4MTAw.GX--PX.e9JS1HKOshKahPcT7q5NKBnghO9SJagIi4XC4o')
