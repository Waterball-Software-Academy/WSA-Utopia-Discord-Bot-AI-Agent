from abc import ABC, abstractmethod
from typing import Dict, List


class EventListener(ABC):
    @abstractmethod
    async def handle_event(self, event_type: str, *args, **kwargs):
        """Handle an event. Must be implemented by subclasses."""
        pass


class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[EventListener]] = {}

    def subscribe(self, event_type: str, listener: EventListener):
        """Subscribe a listener to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        print(f"Listener subscribed to event '{event_type}'")

    def unsubscribe(self, event_type: str, listener: EventListener):
        """Unsubscribe a listener from an event type."""
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)
            print(f"Listener unsubscribed from event '{event_type}'")
            if not self._listeners[event_type]:  # Clean up if no listeners left
                del self._listeners[event_type]

    async def publish(self, event_type: str, *args, **kwargs):
        """Publish an event to all its subscribers."""
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                await listener.handle_event(event_type, *args, **kwargs)
            print(f"Event '{event_type}' published to {len(self._listeners[event_type])} listeners")
        else:
            print(f"No listeners for event '{event_type}'")
