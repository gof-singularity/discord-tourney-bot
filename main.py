import discord
import random
from replit import db


sad_words = ['sad', 'depressed', 'shit', 'hungry', 'gae']


def update_encouragement(encouraging_message):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]

def delete_encouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
    db["encouragements"] = encouragements

def show_encouragements():
  encouragements = []
  encouragements = db["encouragements"]
  return encouragements




def add_player_mk(player):
  if "players_mk" in db.keys():
    players = db["players_mk"]
    players.append(player)
    db["players_mk"] = players
  else:
    db["players_mk"] = [player]

def show_players_mk():
  return db["players_mk"]

def delete_player_mk(player):
  players = db["players_mk"]
  index = players.index(player)
  if len(players) > index:
    del players[index]
    db["players"] = players


def add_player_fifa(player):
  if "players_fifa" in db.keys():
    players = db["players_fifa"]
    players.append(player)
    db["players_fifa"] = players
  else:
    db["players_fifa"] = [player]

def show_players_fifa():
  return db["players_fifa"]


def add_player_tennis(player):
  if "players_tennis" in db.keys():
    players = db["players_tennis"]
    players.append(player)
    db["players_tennis"] = players
  else:
    db["players_tennis"] = [player]

def show_players_tennis():
  return db["players_tennis"]

client = discord.Client()
api_key = 'OTg5MDQ0OTU3NTAxMzU4MTAw.GX--PX.e9JS1HKOshKahPcT7q5NKBnghO9SJagIi4XC4o'

@client.event
async def on_ready():
  print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
  if message.author == client.user:
    return
    
  msg = message.content
  
  
  options = db["encouragements"]
  
  if msg.startswith('$newenc'):
    encouraging_message = msg.split('$new ', 1)[1]
    update_encouragement(encouraging_message)
    await message.channel.send('New encouragement added.')

  if msg.startswith('$showenc'):
    await message.channel.send(show_encouragements())

  if msg.startswith('$delenc'):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(msg.split('$del ', 1)[1])
      delete_encouragement(index)
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)


  
  if any(word in msg for word in sad_words):
    await message.channel.send(random.choice(options))
    
  if msg.startswith('$print_my_name'):
    await message.channel.send(f'Your name is {message.author}')

  if msg.startswith('$addme'):
    player = str(message.author).split('#')[0]
    channel = message.channel.name
    print(message.channel.id)
    if channel == 'mk-tourney':
      add_player_mk(player)
      await message.channel.send(f'Player {player} added to {channel}')

    if channel == 'fifa-tourney':
      add_player_fifa(player)
      await message.channel.send(f'Player {player} added to {channel}')

    if channel == 'tennis-tourney':
      add_player_tennis(player)
      await message.channel.send(f'Player {player} added to {channel}')

  if msg.startswith('$show'):
    channel = message.channel.name
    if channel == 'mk-tourney':
      await message.channel.send(show_players_mk())

    if channel == 'fifa-tourney':
      await message.channel.send(show_players_fifa())

    if channel == 'tennis-tourney':
      await message.channel.send(show_players_tennis())

  if msg.startswith('$deleteme'):
    player = str(message.author).split('#')[0]
    delete_player_mk(player)
    await message.channel.send(f'Player {player} deleted')      

  if msg.startswith('/help'):
    await message.channel.send('''
                         Commands:
                         $addmetogame to add user to the game tourney
                         $deletemefromgame to delete user from the game tourney
                         $showplayers to show players in the game tourney
                               ''')


client.run(api_key)