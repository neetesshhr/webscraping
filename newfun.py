import asyncio
import requests
import websockets
from index import urlmaker
import os

os.system("node -e buttonclicker.js")

async def handle_message(websocket, message):
    if message == "fetch_url":
        response = requests.get(url=urlmaker(), stream=True)

async def handle_connection(websocket, path):
  async for message in websocket:
    await handle_message(websocket, message)

server = websockets.serve(handle_connection, "localhost", 4321)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
