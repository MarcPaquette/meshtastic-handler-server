"""Interfaces module - Abstract base classes and dataclasses."""

from meshtastic_handler.interfaces.message_transport import (
    IncomingMessage,
    MessageHandler,
    MessageTransport,
)
from meshtastic_handler.interfaces.node_context import GPSLocation, NodeContext
from meshtastic_handler.interfaces.plugin import Plugin, PluginMetadata, PluginResponse

__all__ = [
    "GPSLocation",
    "IncomingMessage",
    "MessageHandler",
    "MessageTransport",
    "NodeContext",
    "Plugin",
    "PluginMetadata",
    "PluginResponse",
]
