import json
import os

regions = {
    "na": "North America",
    "eu": "Europe",
    "sa": "South America",
    "ea": "East Asia",
    "sg": "Southeast Asia"
}

game_modes = {
    'blitz_pvp_ranked': 'Blitz' ,
    'blitz_rounds_pvp_casual': 'Onslaught',
    'ranked': 'Ranked',
    'casual': 'Casual',
    'private_party_blitz_match': 'Private Blitz',
    'casual_aral': 'Battle Royale',
    'private': 'Private',
    'private_party_draft_match': 'Private Draft',
    'private_party_aral_match': 'Private Battle Royale'
}

skindir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'skins.json')
with open(skindir) as skinjson:
    skins = json.load(skinjson)

itemdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'items.json')
with open(itemdir) as itemjson:
    items = json.load(itemjson)