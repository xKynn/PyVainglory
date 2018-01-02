Welcome to PyVainglory's documentation!
===========================================

Basic Usage::

   import pyvainglory
   import requests

   vgc = pyvainglory.Client('your-api-key')

   # You can also provide a requests.Session to the Client constructor
   session = requests.Session()
   vgc_a = pyvainglory.Client('your-api-key', session)

   # Get 3 matches after specified time
   # after and before can also be datetime.datetime objects
   matches = vgc.get_matches(limit=3, after="2017-11-22T20:34:58Z", region='na')

   # Go to the next pages of matches
   matches.next()

   # Get telemetry data for one of the matches
   telemetry = matches.matches[0].get_telemetry()

   player = vgc.player_by_name('Demolasher36', region='sg')
   my_blitz_games = player.games_played.blitz
   
   my_recent_games = vgc.get_matches(limit=3, after="2018-01-1T20:34:58Z", playernames=['Demolasher36'], region='sg')

Async Usage::

   import aiohttp
   import asyncio
   import pyvainglory

   vgc = pyvainglory.AsyncClient('your-api-key')

   # You can also provide an aiohttp.ClientSession to the AsyncClient constructor
   session = aiohttp.ClientSession()
   vgc_a = pyvainglory.AsyncClient('your-api-key', session)

   # Get 3 matches after specified time
   # after and before can also be datetime.datetime objects
   matches = await vgc.get_matches(limit=3, after="2017-11-22T20:34:58Z", region='na')

   # Go to the next pages of matches
   await matches.next()

   # Get telemetry data for one of the matches
   telemetry = await matches.matches[0].get_telemetry()

   player = await vgc.player_by_name('Demolasher36', region='sg')
   my_blitz_games = player.games_played.blitz
   
   my_recent_games = await vgc.get_matches(limit=3, after="2018-01-1T20:34:58Z", playernames=['Demolasher36'], region='sg')

pyvainglory.Client
------------------------

.. automodule:: pyvainglory.client
    :members:
    :show-inheritance:

pyvainglory.AsyncClient
------------------------

.. automodule:: pyvainglory.asyncclient
    :members:
    :show-inheritance:

pyvainglory.models
----------------------

.. automodule:: pyvainglory.models
    :members:
    :show-inheritance:

pyvainglory.errors
----------------------

.. automodule:: pyvainglory.errors
    :members:
    :show-inheritance: