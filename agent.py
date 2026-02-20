# agent.py
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any
from event_bus import event_queue, response_queue, publish_response
import time

class Agent(ABC):
    """Abstract Agent: listens to events and may publish responses."""
    @abstractmethod
    async def run(self):
        ...

class MockAgent(Agent):
    """
    A simple rule-based agent.
    Listens to event_queue and responds to messages containing keywords.
    """
    def __init__(self, name: str = "mock-ai", poll_interval: float = 0.1):
        self.name = name
        self.poll_interval = poll_interval
        self._running = False

    async def _process_message(self, event: Dict[str, Any]):
        typ = event.get("type")
        data = event.get("data", {})
        # Only respond to 'message' events
        if typ != "message":
            return

        text = (data.get("text") or "").lower()
        room = data.get("room", "default")
        user = data.get("user", "anonymous")

        # Rule: greeting
        if any(w in text for w in ["hello", "hi", "hey"]):
            resp = {
                "type": "message",
                "data": {
                    "user": self.name,
                    "room": room,
                    "text": f"Hello {user}! I'm a mock AI agent. You said: {data.get('text')}",
                    "role": "ai",
                }
            }
            await publish_response(resp)
            return

        # Rule: echo when user asks "repeat:"
        if text.startswith("repeat:"):
            payload = data.get("text")[7:].strip()
            resp = {
                "type": "message",
                "data": {
                    "user": self.name,
                    "room": room,
                    "text": f"Repeating: {payload}",
                    "role": "ai",
                }
            }
            await publish_response(resp)
            return

        # Rule: get time
        if "time" in text:
            resp = {
                "type": "message",
                "data": {
                    "user": self.name,
                    "room": room,
                    "text": f"The time is {time.strftime('%H:%M:%S')}",
                    "role": "ai",
                }
            }
            await publish_response(resp)
            return

        # Default: sometimes ignore, sometimes send a dummy response
        if "?" in text:
            resp = {
                "type": "message",
                "data": {
                    "user": self.name,
                    "room": room,
                    "text": "That's an interesting question! (I am a mock AI agent.)",
                    "role": "ai",
                }
            }
            await publish_response(resp)
            return
        
        # Rule: bye
        if "bye" in text:
            resp = {
                "type": "message",
                "data": {
                    "user": self.name,
                    "room": room,
                    "text": "Goodbye! Happy to talk with you! (I am a mock AI agent.)",
                    "role": "ai",
                }
            }
            await publish_response(resp)
            return

    async def run(self):
        # simple consumer of event_queue
        self._running = True
        while self._running:
            try:
                event = await event_queue.get()
                # Process each and don't re-put
                await self._process_message(event)
            except Exception:
                # keep agent alive even if one message errors
                import traceback; traceback.print_exc()
            finally:
                try:
                    event_queue.task_done()
                except Exception:
                    pass
            await asyncio.sleep(self.poll_interval)

    def stop(self):
        self._running = False
