"""Plugins module - Built-in plugin implementations."""

from meshtastic_handler.plugins.gopher_plugin import GopherPlugin
from meshtastic_handler.plugins.llm_plugin import LLMPlugin
from meshtastic_handler.plugins.weather_plugin import WeatherPlugin
from meshtastic_handler.plugins.wikipedia_plugin import WikipediaPlugin

__all__ = [
    "GopherPlugin",
    "LLMPlugin",
    "WeatherPlugin",
    "WikipediaPlugin",
]
