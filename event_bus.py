# event_bus.py
import asyncio
from typing import Any, Dict, Callable, Coroutine, Optional

# Single queue for inbound events
event_queue: "asyncio.Queue[dict]" = asyncio.Queue()

# Also have a responses queue where agents publish back
response_queue: "asyncio.Queue[dict]" = asyncio.Queue()

# Used resources from StackOverflow posts
# Simple publisher helper
async def publish_event(event: dict):
    """Publish an event into the main event queue."""
    await event_queue.put(event)

async def publish_response(event: dict):
    """Publish a response (from agents) to the response queue."""
    await response_queue.put(event)

# Used resources from StackOverflow posts
# Utility: start background tasks for consumer loops (called from app)
def start_background_task(loop: asyncio.AbstractEventLoop, coro: Callable[..., Coroutine]):
    """Start a background coroutine in the given event loop."""
    task = loop.create_task(coro())
    return task
