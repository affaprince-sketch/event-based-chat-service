# simple_client.py
import asyncio
import json
import aiohttp
import websockets

REST_URL = "http://localhost:8000"
#WS_URL = "ws://localhost:8000/ws?user={user}&room={room}"
WS_URL = "ws://event-based-chat-service-h4eue8fbcyf8bjam.canadacentral-01.azurewebsites.net:8000/ws?user={user}&room={room}"

async def ws_listener(user="john", room="default"):
    uri = WS_URL.format(user=user, room=room)
    async with websockets.connect(uri) as ws:
        print("Connected to WS. Waiting for messages (ctrl-c to quit)...")
        print("Chatting History in room: ", room)
        async for msg in ws:
            try:
                data = json.loads(msg)
            except Exception:
                data = {"raw": msg}
            print("WS RECEIVED:", data)

async def post_message(user="john", room="default", text="hi"):
    async with aiohttp.ClientSession() as session:
        resp = await session.post(f"{REST_URL}/messages", json={"user":user,"room":room,"text":text})
        print(await resp.json())

async def interactive(user="john", room="default"):
    # spawn WS listener
    listener = asyncio.create_task(ws_listener(user,room))
    await asyncio.sleep(0.5)
    print("Type messages to send. Empty line to quit.")
    try:
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            if not line:
                break
            await post_message(user,room,line)
    finally:
        listener.cancel()

if __name__ == "__main__":
    import sys
    user = sys.argv[1] if len(sys.argv) > 1 else "john"
    room = sys.argv[2] if len(sys.argv) > 2 else "default"
    asyncio.run(interactive(user, room))
