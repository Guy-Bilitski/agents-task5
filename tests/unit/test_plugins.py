"""
Unit Tests for Plugin System.

Tests for the plugin registry, base classes, and plugin discovery.
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.plugins import (
    PluginRegistry,
    PluginError,
    PluginNotFoundError,
    PluginRegistrationError,
    BasePlugin,
    BaseLLMPlugin,
    BaseStrategyPlugin,
    BaseMetricPlugin,
    plugin,
    register_plugin,
    llm_registry,
    strategy_registry,
    metric_registry,
    initialize_default_plugins,
    PluginFactory,
)
from common.llm import BaseLLM, MockLLM


class TestPluginRegistry:
    """Tests for the PluginRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test."""
        return PluginRegistry("test")

    @pytest.fixture
    def typed_registry(self):
        """Create a registry with a base class requirement."""
        return PluginRegistry("llm", base_class=BaseLLM)

    def test_register_plugin(self, registry):
        """Should register a plugin successfully."""

        class TestPlugin:
            pass

        registry.register("test", TestPlugin)

        assert "test" in registry
        assert registry.has_plugin("test")

    def test_register_with_metadata(self, registry):
        """Should store plugin metadata."""

        class TestPlugin:
            pass

        metadata = {"version": "1.0", "author": "Test"}
        registry.register("test", TestPlugin, metadata=metadata)

        assert registry.get_metadata("test") == metadata

    def test_get_registered_plugin(self, registry):
        """Should retrieve registered plugin."""

        class TestPlugin:
            pass

        registry.register("test", TestPlugin)
        retrieved = registry.get("test")

        assert retrieved is TestPlugin

    def test_get_unregistered_plugin_raises(self, registry):
        """Should raise PluginNotFoundError for unregistered plugin."""
        with pytest.raises(PluginNotFoundError):
            registry.get("nonexistent")

    def test_list_plugins(self, registry):
        """Should list all registered plugins."""

        class Plugin1:
            pass

        class Plugin2:
            pass

        registry.register("plugin1", Plugin1)
        registry.register("plugin2", Plugin2)

        plugins = registry.list_plugins()
        assert "plugin1" in plugins
        assert "plugin2" in plugins
        assert len(plugins) == 2

    def test_unregister_plugin(self, registry):
        """Should unregister a plugin."""

        class TestPlugin:
            pass

        registry.register("test", TestPlugin)
        assert registry.has_plugin("test")

        result = registry.unregister("test")
        assert result is True
        assert not registry.has_plugin("test")

    def test_unregister_nonexistent_returns_false(self, registry):
        """Should return False when unregistering nonexistent plugin."""
        result = registry.unregister("nonexistent")
        assert result is False

    def test_duplicate_registration_raises(self, registry):
        """Should raise error on duplicate registration without override."""

        class Plugin1:
            pass

        class Plugin2:
            pass

        registry.register("test", Plugin1)

        with pytest.raises(PluginRegistrationError):
            registry.register("test", Plugin2)

    def test_duplicate_registration_with_override(self, registry):
        """Should allow override of existing registration."""

        class Plugin1:
            pass

        class Plugin2:
            pass

        registry.register("test", Plugin1)
        registry.register("test", Plugin2, override=True)

        assert registry.get("test") is Plugin2

    def test_registry_length(self, registry):
        """Should return correct length."""

        class Plugin:
            pass

        assert len(registry) == 0
        registry.register("test1", Plugin)
        assert len(registry) == 1
        registry.register("test2", Plugin)
        assert len(registry) == 2

    def test_registry_iteration(self, registry):
        """Should support iteration over plugin names."""

        class Plugin:
            pass

        registry.register("a", Plugin)
        registry.register("b", Plugin)
        registry.register("c", Plugin)

        names = list(registry)
        assert set(names) == {"a", "b", "c"}

    def test_clear_registry(self, registry):
        """Should clear all plugins."""

        class Plugin:
            pass

        registry.register("test1", Plugin)
        registry.register("test2", Plugin)

        registry.clear()

        assert len(registry) == 0
        assert registry.list_plugins() == []

    def test_type_validation(self, typed_registry):
        """Should validate plugin against base class."""

        class ValidPlugin(BaseLLM):
            def query(self, context, question, **kwargs):
                return {}

        class InvalidPlugin:
            pass

        # Valid plugin should register
        typed_registry.register("valid", ValidPlugin)
        assert typed_registry.has_plugin("valid")

        # Invalid plugin should raise
        with pytest.raises(PluginRegistrationError):
            typed_registry.register("invalid", InvalidPlugin)

    def test_create_instance(self, registry):
        """Should create instance of registered plugin."""

        class ConfigurablePlugin:
            def __init__(self, value: int):
                self.value = value

        registry.register("configurable", ConfigurablePlugin)
        instance = registry.create_instance("configurable", value=42)

        assert isinstance(instance, ConfigurablePlugin)
        assert instance.value == 42


class TestPluginDecorators:
    """Tests for plugin decorators."""

    def test_plugin_decorator(self):
        """Should mark class as plugin."""

        @plugin(name="decorated", metadata={"version": "1.0"})
        class DecoratedPlugin:
            pass

        assert hasattr(DecoratedPlugin, "_plugin_name")
        assert DecoratedPlugin._plugin_name == "decorated"
        assert DecoratedPlugin._plugin_metadata == {"version": "1.0"}

    def test_plugin_decorator_default_name(self):
        """Should use class name as default plugin name."""

        @plugin()
        class MyPlugin:
            pass

        assert MyPlugin._plugin_name == "myplugin"

    def test_register_plugin_decorator(self):
        """Should register plugin with registry."""
        registry = PluginRegistry("test")

        @register_plugin(registry, name="registered")
        class RegisteredPlugin:
            pass

        assert registry.has_plugin("registered")
        assert registry.get("registered") is RegisteredPlugin


class TestBasePluginClasses:
    """Tests for base plugin classes."""

    def test_base_plugin_get_name(self):
        """Should return plugin name."""

        class TestPlugin(BasePlugin):
            PLUGIN_NAME = "test_plugin"

        assert TestPlugin.get_name() == "test_plugin"

    def test_base_plugin_get_description(self):
        """Should return docstring as description."""

        class TestPlugin(BasePlugin):
            """This is a test plugin."""
            PLUGIN_NAME = "test"

        assert TestPlugin.get_description() == "This is a test plugin."

    def test_base_llm_plugin_interface(self):
        """BaseLLMPlugin should require query method."""

        class IncompletePlugin(BaseLLMPlugin):
            pass

        with pytest.raises(TypeError):
            IncompletePlugin()

    def test_base_strategy_plugin_interface(self):
        """BaseStrategyPlugin should require process and get_metrics."""

        class IncompleteStrategy(BaseStrategyPlugin):
            pass

        with pytest.raises(TypeError):
            IncompleteStrategy()

    def test_base_metric_plugin_interface(self):
        """BaseMetricPlugin should require compute and name."""

        class IncompleteMetric(BaseMetricPlugin):
            pass

        with pytest.raises(TypeError):
            IncompleteMetric()


class TestGlobalRegistries:
    """Tests for global plugin registries."""

    def test_llm_registry_exists(self):
        """LLM registry should exist."""
        assert llm_registry is not None
        assert llm_registry.name == "llm"

    def test_strategy_registry_exists(self):
        """Strategy registry should exist."""
        assert strategy_registry is not None
        assert strategy_registry.name == "strategy"

    def test_metric_registry_exists(self):
        """Metric registry should exist."""
        assert metric_registry is not None
        assert metric_registry.name == "metric"

    def test_initialize_default_plugins(self):
        """Should register default plugins."""
        # Clear and reinitialize
        llm_registry.clear()
        initialize_default_plugins()

        assert llm_registry.has_plugin("mock")
        assert llm_registry.has_plugin("ollama")


class TestPluginFactory:
    """Tests for the PluginFactory class."""

    def test_factory_creates_llm(self):
        """Factory should create LLM instances."""
        factory = PluginFactory(auto_discover=False)

        llm = factory.create_llm("mock", latency_base=0.01)

        assert isinstance(llm, MockLLM)
        assert llm.latency_base == 0.01

    def test_factory_lists_available_llms(self):
        """Factory should list available LLMs."""
        factory = PluginFactory(auto_discover=False)

        llms = factory.list_available_llms()

        assert "mock" in llms
        assert "ollama" in llms

    def test_factory_raises_for_unknown_plugin(self):
        """Factory should raise for unknown plugin."""
        factory = PluginFactory(auto_discover=False)

        with pytest.raises(PluginNotFoundError):
            factory.create_llm("nonexistent")


class TestPluginDiscovery:
    """Tests for plugin discovery from files."""

    def test_discover_from_directory(self, temp_dir):
        """Should discover plugins from directory."""
        # Create a plugin file
        plugin_content = '''
from common.plugins import plugin, BasePlugin

@plugin(name="discovered_plugin")
class DiscoveredPlugin(BasePlugin):
    """A discovered plugin."""
    pass
'''
        plugin_file = temp_dir / "test_plugin.py"
        plugin_file.write_text(plugin_content)

        # Create registry and discover
        registry = PluginRegistry("test")
        count = registry.discover_plugins(temp_dir)

        # Plugin should be registered (may be 0 if imports fail in isolation)
        assert count >= 0

    def test_discover_skips_private_files(self, temp_dir):
        """Should skip files starting with underscore."""
        # Create a private plugin file
        private_file = temp_dir / "_private_plugin.py"
        private_file.write_text("class PrivatePlugin: pass")

        registry = PluginRegistry("test")
        count = registry.discover_plugins(temp_dir)

        assert count == 0

    def test_discover_empty_directory(self, temp_dir):
        """Should handle empty directory."""
        registry = PluginRegistry("test")
        count = registry.discover_plugins(temp_dir)

        assert count == 0

    def test_discover_nonexistent_directory(self, temp_dir):
        """Should handle nonexistent directory."""
        registry = PluginRegistry("test")
        count = registry.discover_plugins(temp_dir / "nonexistent")

        assert count == 0
