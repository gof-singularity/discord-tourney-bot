import discord
from discord.ext import commands
import re
import psycopg2

from server import get_matches, start_tournament, get_participants_names_ids, set_winner, create_tournament, add_participants, get_round_image, get_leaderboard, end_tournament

tourney_names_ids = []
players_usernames_d_ids = []


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

def get_discord_idofusername(username, obj):
  for item in obj:
    if item['username'] == username:
      return item['discord_id']


client = commands.Bot(command_prefix='!', help_command=None)

@client.event
async def on_ready():
  print('Bot is ready')

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

  players_usernames_d_id = {'discord_id': ctx.author.id, 'username': username }
  players_usernames_d_ids.append(players_usernames_d_id)

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
  postgres_username = str(ctx.author).split('#')[0]
  print(ctx.author)
  print(ctx.author.id)
  s = convertTuple(message)
  arr = s.split('\n')
  try: 
    winner_user = arr[2].split(' ')[0]
    loser_user = arr[3].split(' ')[0]
    round = arr[1].split(' ')[1]
    fact = arr[4]
    study = arr[5]
  except IndexError:
    await ctx.send('**error**: something is missing')
    return

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

  if winner != ctx.author:
    await ctx.send('**error**: authentication error')
    return

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
  try:
    connection = psycopg2.connect(user="wwanpexp",
                                  password="lW9ahJNBZ0mGQUI9VtWCi2R44KWNvjUc",
                                  host="batyr.db.elephantsql.com",
                                  port="5432",
                                  database="wwanpexp")
    cursor = connection.cursor()

    postgres_insert_query = """ INSERT INTO customuser (ID, NAME, FACT, STUDY) VALUES (%s,%s, %s, %s)"""
    record_to_insert = (str(loser_id), str(loser_username), str(fact), str(study))
    cursor.execute(postgres_insert_query, record_to_insert)
    
    connection.commit()
    count = cursor.rowcount
    print(count, "Record inserted successfully into mobile table")

  except (Exception, psycopg2.Error) as error:
      print("Failed to insert record into mobile table", error)

  finally:
      # closing database connection.
      if connection:
          cursor.close()
          connection.close()
          print("PostgreSQL connection is closed")
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
  
  for match in matches:
    if matchid == match["id"]:
      if match["winner_id"] != None:
        await ctx.send('**error**: you have already played the match')
        return

  if matchid == -1:
    print('error: could not find match')
    return
 
  print(tourney_id)
  print(matchid)
  print(winner_api_id)

  set_winner(tourney_id, matchid, winner_api_id)
  matches = get_matches(tourney_id)
  print(matches)
  

  await ctx.send(winner_user + ' won')
  








@client.command()
async def start(ctx):
  if ctx.author.guild_permissions.manage_channels:
    channel = ctx.channel.name
    tourney_id = gettourneyid(channel)
    print(tourney_id)
    response = start_tournament(tourney_id)
    if response == 200:
      await ctx.send(f'Tourney **{channel}** has started!!')


    matches = get_matches(tourney_id)
    tourney_names_ids = get_participants_names_ids(tourney_id)
    print(tourney_names_ids)
    s = ''
    for match in matches:
      if int(match["round"]) == 1:

        player1 = getusername(match["player1_id"], tourney_names_ids)
        player2 = getusername(match["player2_id"], tourney_names_ids)
        
        player1_discord_id = get_discord_idofusername(player1, players_usernames_d_ids)
        player2_discord_id = get_discord_idofusername(player2, players_usernames_d_ids)

        player1_user = await client.fetch_user(player1_discord_id)
        player2_user = await client.fetch_user(player2_discord_id)

        player1_discord_id = '<@' + str(player1_discord_id) + '>'
        player2_discord_id = '<@' + str(player2_discord_id) + '>'


        dm = await player1_user.create_dm()
        await dm.send(f"You need to play {channel} with {player2_discord_id} until 18:00")
        
        dm = await player2_user.create_dm()
        await dm.send(f"You need to play {channel} with {player1_discord_id} until 18:00")
        

        #s = s + round + '\n' + str(player1) + ' vs ' + str(player2) + '\n'
        #print(s)
  else:
    await ctx.send('You do not have permission to start a tourney')

@client.command()
async def dmme(ctx):
  dm = await ctx.message.author.create_dm()
  await dm.send("You need to play the game until 18:00")



################# NOT USED #################
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



################# NOT USED #################
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
  if ctx.author.guild_permissions.manage_channels:
    channel = ctx.channel.name
    tourney_id = gettourneyid(channel)
    src=get_round_image(tourney_id, int(round))
    if len(src)>35:
      await ctx.send(src)
      return

    
    with open(src, 'rb') as f:
      picture = discord.File(f)
      await ctx.send(file=picture)
  else:
    await ctx.send('You lack the permission to retrieve rounds.')


@client.command()
async def board(ctx):
  if ctx.author.guild_permissions.manage_channels:
    channel = ctx.channel.name
    tourney_id = gettourneyid(channel)
    path=get_leaderboard(tourney_id)

    with open(path, 'rb') as f:
      picture = discord.File(f)
      await ctx.send(file=picture)
  else:
    await ctx.send('You lack the permission to retrieve rounds.')

@client.command()
async def end(ctx):
  if ctx.author.guild_permissions.manage_channels:
    channel = ctx.channel.name
    tourney_id = gettourneyid(channel)

    response = end_tournament(tourney_id)
    await ctx.send(response)
  else:
    await ctx.send('You lack the permission to retrieve rounds.')



@client.command()
async def profile(ctx):
  try:
    connection = psycopg2.connect(user="wwanpexp",
                                  password="lW9ahJNBZ0mGQUI9VtWCi2R44KWNvjUc",
                                  host="batyr.db.elephantsql.com",
                                  port="5432",
                                  database="wwanpexp")
    cursor = connection.cursor()

    name = str(ctx.author).split('#')[0]
    postgres_select_query = f"select * from customuser where name = '{name}'"
    cursor.execute(postgres_select_query)
    mobile_records = cursor.fetchall()
    print(mobile_records)

    connection.commit()
    count = cursor.rowcount
    print(count, "Record select successfully into mobile table")
    await ctx.send(mobile_records)
  except (Exception, psycopg2.Error) as error:
      print("Failed to select record into mobile table", error)

  finally:
      # closing database connection.
      if connection:
          cursor.close()
          connection.close()
          print("PostgreSQL connection is closed")











    
client.run('OTg5MDQ0OTU3NTAxMzU4MTAw.Gk4J9U.5OFujjFtXl1NqZTItLLGr5L4TL01AELdJBKjxk')

