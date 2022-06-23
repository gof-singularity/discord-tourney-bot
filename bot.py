from email import header
from http.client import ResponseNotReady
from secrets import token_urlsafe
from urllib import response
from webbrowser import get
import discord
from discord.ext import commands
import requests
import json
import re

from server import get_matches, start_tournament, get_participants_names_ids, set_winner, create_tournament, add_participants, get_round_image, get_leaderboard, end_tournament

tourney_names_ids = []

def convertTuple(tup):
  str = ''
  for item in tup:
      if item.startswith('<') or item.startswith('@') or item.startswith('Round'):
        item = '\n' + item
      
      str = str + item + ' '
  return str
def gettourneyid(channelname):
  for item in tourney_names_ids:
    if item["channelname"] == channelname:
      return item["id"]
def getusername(id, obj):
  for item in obj:
    if item['id'] == id:
      return item['username']
def getidofusername(username, obj):
  for item in obj:
    if item['username'] == username:
      return item['id']




client = commands.Bot(command_prefix='!', help_command=None)

@client.event
async def on_ready():
  print('Bot is ready')


@client.command()
async def name(ctx):
  await ctx.send(f'{ctx.author}')

@client.command()
async def create(ctx, tourney):
    guild = ctx.message.guild
    if ctx.author.guild_permissions.manage_channels:
      await guild.create_text_channel(name=f'{tourney}')
    
      id = create_tournament(tourney)

      tourney_names_id = {} 
      tourney_names_id["id"] = id
      tourney_names_id["channelname"] = tourney

      tourney_names_ids.append(tourney_names_id)

      print(tourney_names_ids)
      
      if id > 0:
        await ctx.send(f'Tourney **{tourney}** created!')
      else:
        await ctx.send(f'error: Tourney could not be created')

      


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

  response = add_participants(tourney_id, username)
  
  await ctx.send(response)








@client.command()
async def result(ctx, *message):
    
  print(ctx.author)
  print(ctx.author.id)
  s = convertTuple(message)
  arr = s.split('\n')

  winner_user = arr[2].split(' ')[0]
  loser_user = arr[3].split(' ')[0]
  round = arr[1].split(' ')[1]
  fact = arr[4]
  study = arr[5]

  print(round)
  print(fact)
  print(study)

  loser_id=re.sub(r"@", "", str(loser_user))
  loser_id=re.sub(r"<", "", str(loser_id))
  loser_id=re.sub(r">", "", str(loser_id))

  winner_id=re.sub(r"@", "", str(winner_user))
  winner_id=re.sub(r"<", "", str(winner_id))
  winner_id=re.sub(r">", "", str(winner_id))
  
  
  winner = await client.fetch_user(winner_id)
  loser = await client.fetch_user(loser_id)

  winner_username = str(winner).split('#')[0]
  loser_username = str(loser).split('#')[0]

  channel = ctx.channel.name
  tourney_id = gettourneyid(channel)
  matches = get_matches(tourney_id)
  participant_names_ids = get_participants_names_ids(tourney_id)
  winner_api_id = getidofusername(winner_username, participant_names_ids)
  loser_api_id = getidofusername(loser_username, participant_names_ids)

  print(matches)
  print(winner_api_id)

  matchid = -1
  for match in matches:
    print(match["round"])
    if int(round) == int(match["round"]):
      print(match["player1_id"])
      print(match["player2_id"])
      if str(winner_api_id) == str(match["player1_id"]) and str(loser_api_id) == str(match["player2_id"]):
        matchid= match["id"] 
      elif str(winner_api_id) == str(match["player2_id"]) and str(loser_api_id) == str(match["player1_id"]):
        matchid= match["id"] 
  
  if matchid == -1:
    print('error: could not find match')
    return
 
  print(tourney_id)
  print(matchid)
  print(winner_api_id)

  set_winner(tourney_id, matchid, winner_api_id)

  await ctx.send(winner_user + ' won')
  








@client.command()
async def start(ctx):
  channel = ctx.channel.name
  tourney_id = gettourneyid(channel)
  print(tourney_id)
  response = start_tournament(tourney_id)
  if response == 200:
    await ctx.send(f'Tourney **{channel}** has started!!')

@client.command()
async def dmme(ctx):
  dm = await ctx.message.author.create_dm()
  await dm.send("You need to play the game until 18:00")
  #response = client.wait_for_message(author=ctx.message.author, timeout=30) 
  #await ctx.send(response) 

@client.command()
async def getmatches(ctx):
  channel = ctx.channel.name
  tourney_id = gettourneyid(channel)
  response = get_matches(tourney_id)
  tourney_names_ids = get_participants_names_ids(tourney_id)
  print(tourney_names_ids)
  s = ''
  for item in response:
    round = 'Round ' + str(item["round"])
    player1 = getusername(item["player1_id"], tourney_names_ids)
    player2 = getusername(item["player2_id"], tourney_names_ids)
    s = s + round + '\n' + str(player1) + ' vs ' + str(player2) + '\n'
    print(s)
  await ctx.send(s)




@client.command()
async def getmatchesround(ctx, round):
  channel = ctx.channel.name
  tourney_id = gettourneyid(channel)
  response = get_matches(tourney_id)
  tourney_names_ids = get_participants_names_ids(tourney_id)
  print(tourney_names_ids)
  s = ''
  for item in response:
    if round == str(item["round"]):
      round = 'Round ' + str(item["round"])
      player1 = getusername(item["player1_id"], tourney_names_ids)
      player2 = getusername(item["player2_id"], tourney_names_ids)
      s = s + round + '\n' + str(player1) + ' vs ' + str(player2) + '\n'
      print(s)
  await ctx.send(s)




@client.command()
async def round(ctx, round):
  channel = ctx.channel.name
  tourney_id = gettourneyid(channel)
  src=get_round_image(tourney_id, int(round))
  if not src:
    await ctx.send("**error**: There is no such tournament or round")

  
  with open(src, 'rb') as f:
    picture = discord.File(f)
    await ctx.send(file=picture)


@client.command()
async def board(ctx):
  channel = ctx.channel.name
  tourney_id = gettourneyid(channel)
  path=get_leaderboard(tourney_id)

  with open(path, 'rb') as f:
    picture = discord.File(f)
    await ctx.send(file=picture)

@client.command()
async def end(ctx):
  channel = ctx.channel.name
  tourney_id = gettourneyid(channel)

  response = end_tournament(tourney_id)
  await ctx.send(response)
client.run('OTg5MDQ0OTU3NTAxMzU4MTAw.GX--PX.e9JS1HKOshKahPcT7q5NKBnghO9SJagIi4XC4o')

