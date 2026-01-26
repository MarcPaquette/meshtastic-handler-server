"""Tests for message router."""

import pytest

from meshtastic_handler.core.message_router import MenuRenderer, MessageRouter
from meshtastic_handler.core.plugin_registry import PluginRegistry
from meshtastic_handler.core.session import Session
from meshtastic_handler.interfaces.node_context import NodeContext

from tests.mocks import MockPlugin


class TestMenuRenderer:
    """Tests for MenuRenderer class."""

    def test_render_empty_registry(self) -> None:
        """Test rendering menu with no plugins."""
        registry = PluginRegistry()
        renderer = MenuRenderer(registry)

        result = renderer.render()
        assert "Available Services:" in result
        assert "Send number to select" in result

    def test_render_with_plugins(self) -> None:
        """Test rendering menu with plugins."""
        registry = PluginRegistry()
        registry.register(MockPlugin(name="Gopher Server", menu_number=1))
        registry.register(MockPlugin(name="LLM Assistant", menu_number=2))

        renderer = MenuRenderer(registry)
        result = renderer.render()

        assert "Available Services:" in result
        assert "1. Gopher Server" in result
        assert "2. LLM Assistant" in result
        assert "Send number to select" in result


class TestMessageRouter:
    """Tests for MessageRouter class."""

    @pytest.fixture
    def router_with_plugin(self) -> tuple[MessageRouter, MockPlugin, PluginRegistry]:
        """Create router with a mock plugin."""
        registry = PluginRegistry()
        plugin = MockPlugin(name="Test Plugin", menu_number=1, welcome="Welcome!")
        registry.register(plugin)
        router = MessageRouter(registry)
        return router, plugin, registry

    @pytest.mark.asyncio
    async def test_menu_selection_enters_plugin(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test that number selection enters a plugin."""
        router, plugin, _ = router_with_plugin
        session = Session(node_id="!test123")
        context = NodeContext(node_id="!test123")

        response = await router.route("1", session, context)

        assert "Welcome!" in response.message
        assert session.active_plugin == "Test Plugin"
        assert not session.is_at_menu

    @pytest.mark.asyncio
    async def test_invalid_menu_selection(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test invalid menu selection shows error."""
        router, _, _ = router_with_plugin
        session = Session(node_id="!test123")
        context = NodeContext(node_id="!test123")

        response = await router.route("99", session, context)

        assert "Invalid selection" in response.message
        assert session.is_at_menu

    @pytest.mark.asyncio
    async def test_non_number_at_menu(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test non-number input at menu shows error."""
        router, _, _ = router_with_plugin
        session = Session(node_id="!test123")
        context = NodeContext(node_id="!test123")

        response = await router.route("hello", session, context)

        assert "Invalid selection" in response.message
        assert "send a number" in response.message.lower()

    @pytest.mark.asyncio
    async def test_exit_command(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test !exit returns to menu."""
        router, _, _ = router_with_plugin
        session = Session(node_id="!test123")
        session.enter_plugin("Test Plugin")
        context = NodeContext(node_id="!test123")

        response = await router.route("!exit", session, context)

        assert "Returned to menu" in response.message
        assert session.is_at_menu

    @pytest.mark.asyncio
    async def test_exit_case_insensitive(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test !exit is case insensitive."""
        router, _, _ = router_with_plugin
        session = Session(node_id="!test123")
        session.enter_plugin("Test Plugin")
        context = NodeContext(node_id="!test123")

        response = await router.route("!EXIT", session, context)

        assert session.is_at_menu

    @pytest.mark.asyncio
    async def test_menu_command(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test !menu shows menu."""
        router, _, _ = router_with_plugin
        session = Session(node_id="!test123")
        session.enter_plugin("Test Plugin")
        context = NodeContext(node_id="!test123")

        response = await router.route("!menu", session, context)

        assert "Available Services:" in response.message
        # Should NOT exit plugin
        assert not session.is_at_menu

    @pytest.mark.asyncio
    async def test_help_in_plugin(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test !help shows plugin help."""
        router, plugin, _ = router_with_plugin
        session = Session(node_id="!test123")
        session.enter_plugin("Test Plugin")
        context = NodeContext(node_id="!test123")

        response = await router.route("!help", session, context)

        assert response.message == plugin.get_help_text()

    @pytest.mark.asyncio
    async def test_message_routed_to_plugin(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test messages are routed to active plugin."""
        router, plugin, _ = router_with_plugin
        session = Session(node_id="!test123")
        session.enter_plugin("Test Plugin")
        context = NodeContext(node_id="!test123")

        response = await router.route("test message", session, context)

        assert len(plugin.handle_calls) == 1
        assert plugin.handle_calls[0][0] == "test message"
        assert "Mock response" in response.message

    @pytest.mark.asyncio
    async def test_plugin_state_updated(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test plugin state is updated after handle."""
        router, _, _ = router_with_plugin
        session = Session(node_id="!test123")
        session.enter_plugin("Test Plugin")
        context = NodeContext(node_id="!test123")

        await router.route("hello", session, context)

        assert session.plugin_state.get("last_message") == "hello"

    @pytest.mark.asyncio
    async def test_whitespace_stripped(
        self, router_with_plugin: tuple[MessageRouter, MockPlugin, PluginRegistry]
    ) -> None:
        """Test that message whitespace is stripped."""
        router, _, _ = router_with_plugin
        session = Session(node_id="!test123")
        context = NodeContext(node_id="!test123")

        response = await router.route("  1  ", session, context)

        assert session.active_plugin == "Test Plugin"
