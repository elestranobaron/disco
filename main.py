import discord
import os
import requests
import json
import random
from replit import db
from keep_alive import keep_alive
import datetime
# importing the requests library 
import requests 
  
# api-endpoint 
URL = "https://api.discalbot.com/v2"
  
# location given here 
URL += "/events/create"
  
# defining a params dict for the parameters to be sent to the API 
PARAMS = {
				"guild_id": 375357265198317579,
				"calendar_number": 1,
				"event_id": "e7gqkup5l8",
				"epoch_start": 1521732600000,
				"epoch_end": 1521732600000,
				"summary": "Weekly study group",
				"description": "Time to study!",
				"location": "Building A, Room 205",
				"is_parent": False,
				"color": "NONE",
				"recur": False,#True,
				#"recurrence": {
				#	"frequency": "WEEKLY",
				#	"count": -1,
				#	"interval": 1
				#},
				"image": "https://imgur.com/totallyARealLink.png"
				}

client = discord.Client()

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing"]

starter_encouragements = [
  "Cheer up!",
  "Hang in there.",
  "You are a great person / bot!"
]

if "responding" not in db.keys():
  db["responding"] = True

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]["a"]
  return(quote)

def update_encouragements(encouraging_message):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]

def delete_encouragment(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
    db["encouragements"] = encouragements

@client.event
async def on_ready():
  print('We have logged in as {0.user}'
  .format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if message.content.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)
  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db.keys():
      options += db["encouragements"]

    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))

  if msg.startswith("$rendezvous"):
    rdv = msg.split("$rendezvous ", 1)[1]
    try:
      format = "%d/%m/%Y-%H:%M:%S"
      datetime.datetime.strptime(rdv, format)
      await message.channel.send("This is the correct date string format.")
      dateheure = rdv.split("-")
      jour = dateheure[0]
      heure = dateheure[1]
      jour = jour.split("/")
      jour = jour[2] + "/" + jour[1] + "/" + jour[0]
      ## appointment = jour + "-" + heure
      # sending get request and saving the response as response object 
      r = requests.post(URL, data = PARAMS) 
      # extracting data in json format 
      data = r.json()
      # extracting latitude, longitude and formatted address  
      # of the first matching location 
      ## response_id = data['id'] 
      response = data['message']
      # printing the output 
      await message.channel.send(response)
      #await message.channel.send("!cal edit")
      #await message.channel.send("!event create")
      #await message.channel.send("!event start " + appointment)
      #await message.channel.send("!event confirm")

      await message.channel.send("Rendez vous en place pour le " + rdv)
    except ValueError:
      await message.channel.send("This is the incorrect date string format. It should be YYYY-MM-DD")

  elif msg.startswith("$new"):
    encouraging_message = msg.split("$new ", 1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added.")

  elif msg.startswith("$del"):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(msg.split("$del",1)[1])
      delete_encouragment(index)
      encouragements = db ["encouragements"]
    await message.channel.send(encouragements)

  elif msg.startswith("$list"):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)

  elif msg.startswith("$responding"):
    value = msg.split("$responding ",1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on.")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off.")

keep_alive()
client.run(os.getenv('TOKEN'))
