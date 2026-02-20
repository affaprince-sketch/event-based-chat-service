# app.py
import asyncio
from contextlib import asynccontextmanager
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
from typing import Dict, Set, Any
from models import MessageIn, EventEnvelope
from event_bus import publish_event, response_queue, start_background_task
from agent import MockAgent
from db import init_db, persist_message, last_messages
import time


# Used resources from Google AI response for how to use lifespan since on_event is deprecated from FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup (before 'yield')
    # FastAPI startup: init DB, start agent and consumer
    await init_db()
    loop = asyncio.get_running_loop()
    # start mock agent
    loop.create_task(AGENT.run())
    # start response consumer
    loop.create_task(response_consumer())

    yield
    # Code to run on shutdown (after 'yield' finishes)
    AGENT.stop()

app = FastAPI(title="MVP Event-Driven Chat Service", lifespan=lifespan)

# In-memory connected WS clients: room -> set of websocket objects
ROOMS: Dict[str, Set[WebSocket]] = {}

# Start background agent instance 
AGENT: MockAgent = MockAgent()

# Dummy Web UI for quick manual testing (optional)
@app.get("/")
async def index():
    html = """
    <!doctype html>
    <html>
    <body>
    <h1>MVP Chat</h1>
    <p>Open console & connect WebSocket to <code>ws://localhost:8000/ws?user=john</code></p>
    </body>
    </html>
    """
    return HTMLResponse(html)

# REST endpoint to post a message (client uses this to send)
@app.post("/messages")
async def post_message(msg: MessageIn):
    # validate body by pydantic
    event = {"type": "message", "data": {"user": msg.user, "room": msg.room, "text": msg.text}}
    # persist user message
    await persist_message(msg.user, msg.room, msg.text, role="user")
    # publish to event queue
    await publish_event(event)
    # respond with 202 accepted
    return {"status": "published"}

# WebSocket endpoint for clients to subscribe to events + send via ws
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # expect query param user and optional room
    await websocket.accept()
    params = dict(websocket.query_params)
    user = params.get("user", "john")
    room = params.get("room", "default")

    # register
    ROOMS.setdefault(room, set()).add(websocket)

    # send recent history to new client
    history = await last_messages(room, 20)
    for m in history:
        await websocket.send_json({"type": "history", "data": m})

    try:
        while True:
            payload = await websocket.receive_text()
            try:
                obj = json.loads(payload)
            except Exception:
                # treat as plain text message
                obj = {"text": payload}
            # allow client to send directly via WS
            text = obj.get("text")
            if text:
                # persist and publish
                await persist_message(user, room, text, role="user")
                await publish_event({"type":"message","data":{"user":user,"room":room,"text":text}})
            # else ignore other ws inputs in MVP
    except WebSocketDisconnect:
        # remove from rooms
        ROOMS.get(room, set()).discard(websocket)

# Background task: consume response_queue and broadcast to WS clients
async def response_consumer():
    while True:
        resp = await response_queue.get()
        try:
            # persist AI message if it has role info
            data = resp.get("data", {})
            role = data.get("role", "ai")
            await persist_message(data.get("user","ai"), data.get("room","default"), data.get("text",""), role=role)

            # broadcast to all websockets in the room
            room = data.get("room", "default")
            # prepare envelope
            envelope = {"type": resp.get("type", "message"), "data": data}
            conns = list(ROOMS.get(room, set()))
            for ws in conns:
                try:
                    await ws.send_json(envelope)
                except Exception:
                    # ignore send errors for now
                    pass
        except Exception:
            import traceback; traceback.print_exc()
        finally:
            try:
                response_queue.task_done()
            except Exception:
                pass


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
