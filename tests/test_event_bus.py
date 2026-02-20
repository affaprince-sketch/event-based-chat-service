# tests/test_event_bus.py
import asyncio
import pytest
from event_bus import event_queue, response_queue, publish_event, publish_response

@pytest.mark.asyncio
async def test_publish_event_and_response():
    # clear queues
    while not event_queue.empty():
        event_queue.get_nowait()
    while not response_queue.empty():
        response_queue.get_nowait()

    await publish_event({"type":"message","data":{"user":"t","text":"hello"}})
    ev = await asyncio.wait_for(event_queue.get(), timeout=1.0)
    assert ev["type"] == "message"
    event_queue.task_done()

    await publish_response({"type":"message","data":{"user":"ai","text":"hi"}})
    rv = await asyncio.wait_for(response_queue.get(), timeout=1.0)
    assert rv["data"]["user"] == "ai"
    response_queue.task_done()
