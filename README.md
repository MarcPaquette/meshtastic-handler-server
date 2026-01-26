# Meshtastic Handler Server

A Python-based Meshtastic server with a plugin architecture for handling different types of requests. Provides an interactive menu system for users to access various services over the Meshtastic mesh network.

## Features

- **Plugin Architecture**: Easily extensible with custom plugins
- **Per-Node Sessions**: Each Meshtastic node gets independent session state
- **Built-in Plugins**:
  - **Gopher Server**: Browse files and directories
  - **LLM Assistant**: AI-powered chat using Ollama
  - **Weather**: GPS-based weather from Open-Meteo
  - **Wikipedia**: Search and read Wikipedia articles
- **Message Chunking**: Automatic splitting of long responses for radio limits
- **Multiple Connection Types**: Serial, TCP, and BLE support

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/) package manager.

```bash
# Clone the repository
git clone <repository-url>
cd meshtastic-handler-server

# Install dependencies
uv sync

# Install with dev dependencies (for testing)
uv sync --extra dev
```

## Quick Start

```bash
# Run with auto-detect serial device
uv run python -m meshtastic_handler

# Run with specific serial device
uv run python -m meshtastic_handler --device /dev/ttyUSB0

# Run with TCP connection
uv run python -m meshtastic_handler --connection tcp --tcp-host 192.168.1.100

# Run with config file
uv run python -m meshtastic_handler --config config.yaml
```

## User Interaction Flow

When a user sends any message to the server:

```
User sends any message
        ↓
┌─────────────────────────────┐
│     MAIN MENU               │
│  "Available Services:"      │
│  1. Gopher Server           │
│  2. LLM Assistant           │
│  3. Weather                 │
│  4. Wikipedia               │
│                             │
│  Send number to select      │
└─────────────────────────────┘
        ↓
User sends "2"
        ↓
┌─────────────────────────────┐
│     LLM PLUGIN ACTIVE       │
│  "LLM Assistant"            │
│  Send your question or:     │
│  !help - show commands      │
│  !exit - return to menu     │
└─────────────────────────────┘
```

### Universal Commands

These commands work anywhere:
- `!exit` - Return to main menu
- `!menu` - Show main menu
- `!help` - Show plugin-specific help (when in a plugin)

## Configuration

Copy `config.example.yaml` to `config.yaml` and customize:

```yaml
server:
  max_message_size: 200
  session_timeout_minutes: 60

meshtastic:
  connection_type: serial  # serial, tcp, or ble
  device: null             # auto-detect

plugins:
  llm:
    ollama_url: "http://localhost:11434"
    model: "llama3.2"
  weather:
    timeout: 10.0
  wikipedia:
    language: "en"
```

## Built-in Plugins

### 1. Gopher Server (Menu #1)

Browse files and directories on the server.

Commands:
- `[number]` - Select item
- `!back` - Go to parent directory
- `!home` - Return to root directory

### 2. LLM Assistant (Menu #2)

Chat with an AI using Ollama.

Commands:
- `[message]` - Ask a question
- `!model <name>` - Switch model
- `!models` - List available models
- `!clear` - Clear conversation history

Requires [Ollama](https://ollama.ai/) running locally.

### 3. Weather (Menu #3)

Get weather for your GPS location.

Commands:
- `!refresh` - Get current weather
- `!forecast` - Get 3-day forecast

Requires GPS enabled on your Meshtastic device.

### 4. Wikipedia (Menu #4)

Search and read Wikipedia articles.

Commands:
- `[topic]` - Search for topic
- `!search <query>` - Search Wikipedia
- `!random` - Get random article

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Project Structure

```
meshtastic-handler-server/
├── src/meshtastic_handler/
│   ├── interfaces/          # Abstract base classes
│   ├── core/               # Plugin registry, routing, sessions
│   ├── transport/          # Meshtastic transport implementation
│   └── plugins/            # Built-in plugins
├── tests/                  # Test suite
└── config.example.yaml     # Example configuration
```

### Creating Custom Plugins

```python
from meshtastic_handler.interfaces.plugin import Plugin, PluginMetadata, PluginResponse
from meshtastic_handler.interfaces.node_context import NodeContext

class MyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Plugin",
            description="Does something cool",
            menu_number=5,
            commands=("!do", "!undo")
        )

    def get_welcome_message(self) -> str:
        return "Welcome to My Plugin!\nSend !help for commands."

    def get_help_text(self) -> str:
        return "Commands:\n!do - Do it\n!undo - Undo it\n!exit - Return to menu"

    async def handle(self, message: str, context: NodeContext, plugin_state: dict) -> PluginResponse:
        if message == "!do":
            return PluginResponse(message="Done!")
        return PluginResponse(message="Unknown command")
```

## License

MIT
