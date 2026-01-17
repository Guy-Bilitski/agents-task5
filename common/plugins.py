"""
Plugin Architecture System.

This module provides a flexible plugin system for extending the LLM Context
Window Experiments platform with custom:
- LLM backends
- Memory strategies
- Evaluation metrics
- Experiment types

The plugin system uses a registry pattern with automatic discovery and
supports both programmatic registration and file-based plugin loading.
"""

import importlib
import importlib.util
import inspect
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic plugin types
T = TypeVar('T')


class PluginError(Exception):
    """Base exception for plugin-related errors."""
    pass


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin is not found in the registry."""
    pass


class PluginRegistrationError(PluginError):
    """Raised when plugin registration fails."""
    pass


class PluginRegistry:
    """
    Generic plugin registry for managing extensible components.

    The registry supports:
    - Manual registration via register()
    - Automatic discovery via discover_plugins()
    - Plugin listing and retrieval
    - Type validation against base classes

    Example Usage:
        >>> registry = PluginRegistry("llm")
        >>> registry.register("ollama", OllamaLLM)
        >>> llm_class = registry.get("ollama")
        >>> llm = llm_class(model_name="llama3.2:1b")
    """

    def __init__(self, name: str, base_class: Optional[Type] = None):
        """
        Initialize a plugin registry.

        Args:
            name: Name of this registry (e.g., "llm", "strategy", "metric")
            base_class: Optional base class that all plugins must inherit from
        """
        self.name = name
        self.base_class = base_class
        self._plugins: Dict[str, Type] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        plugin_class: Type[T],
        metadata: Optional[Dict[str, Any]] = None,
        override: bool = False
    ) -> None:
        """
        Register a plugin class with the registry.

        Args:
            name: Unique name for the plugin
            plugin_class: The plugin class to register
            metadata: Optional metadata about the plugin
            override: Whether to override existing registration

        Raises:
            PluginRegistrationError: If registration fails
        """
        # Validate name
        if not name or not isinstance(name, str):
            raise PluginRegistrationError(f"Invalid plugin name: {name}")

        # Check for existing registration
        if name in self._plugins and not override:
            raise PluginRegistrationError(
                f"Plugin '{name}' already registered in {self.name} registry. "
                f"Use override=True to replace."
            )

        # Validate against base class
        if self.base_class is not None:
            if not (inspect.isclass(plugin_class) and issubclass(plugin_class, self.base_class)):
                raise PluginRegistrationError(
                    f"Plugin '{name}' must be a subclass of {self.base_class.__name__}"
                )

        # Register the plugin
        self._plugins[name] = plugin_class
        self._metadata[name] = metadata or {}

        logger.debug(f"Registered plugin '{name}' in {self.name} registry")

    def unregister(self, name: str) -> bool:
        """
        Remove a plugin from the registry.

        Args:
            name: Name of the plugin to remove

        Returns:
            True if removed, False if not found
        """
        if name in self._plugins:
            del self._plugins[name]
            del self._metadata[name]
            logger.debug(f"Unregistered plugin '{name}' from {self.name} registry")
            return True
        return False

    def get(self, name: str) -> Type[T]:
        """
        Get a plugin class by name.

        Args:
            name: Name of the plugin to retrieve

        Returns:
            The registered plugin class

        Raises:
            PluginNotFoundError: If plugin is not found
        """
        if name not in self._plugins:
            available = ", ".join(self._plugins.keys()) or "none"
            raise PluginNotFoundError(
                f"Plugin '{name}' not found in {self.name} registry. "
                f"Available plugins: {available}"
            )
        return self._plugins[name]

    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a registered plugin."""
        if name not in self._metadata:
            raise PluginNotFoundError(f"Plugin '{name}' not found")
        return self._metadata[name]

    def list_plugins(self) -> List[str]:
        """Get list of all registered plugin names."""
        return list(self._plugins.keys())

    def has_plugin(self, name: str) -> bool:
        """Check if a plugin is registered."""
        return name in self._plugins

    def clear(self) -> None:
        """Remove all registered plugins."""
        self._plugins.clear()
        self._metadata.clear()

    def discover_plugins(
        self,
        path: Path,
        pattern: str = "*.py",
        recursive: bool = True
    ) -> int:
        """
        Discover and register plugins from a directory.

        Plugins are discovered by looking for classes decorated with
        @register_plugin or classes that match the registry's base_class.

        Args:
            path: Directory to search for plugins
            pattern: Glob pattern for plugin files
            recursive: Whether to search recursively

        Returns:
            Number of plugins discovered
        """
        if not path.exists():
            logger.warning(f"Plugin directory does not exist: {path}")
            return 0

        discovered = 0
        glob_pattern = f"**/{pattern}" if recursive else pattern

        for plugin_file in path.glob(glob_pattern):
            if plugin_file.name.startswith("_"):
                continue

            try:
                discovered += self._load_plugins_from_file(plugin_file)
            except Exception as e:
                logger.warning(f"Failed to load plugins from {plugin_file}: {e}")

        logger.info(f"Discovered {discovered} plugins in {path}")
        return discovered

    def _load_plugins_from_file(self, file_path: Path) -> int:
        """Load plugins from a single Python file."""
        spec = importlib.util.spec_from_file_location(
            file_path.stem,
            file_path
        )
        if spec is None or spec.loader is None:
            return 0

        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.warning(f"Failed to execute module {file_path}: {e}")
            return 0

        discovered = 0

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip imported classes (only consider classes defined in this module)
            if obj.__module__ != module.__name__:
                continue

            # Check for explicit registration marker
            if hasattr(obj, '_plugin_name'):
                self.register(
                    obj._plugin_name,
                    obj,
                    getattr(obj, '_plugin_metadata', None)
                )
                discovered += 1
                continue

            # Auto-register if matches base class
            if (self.base_class is not None and
                    issubclass(obj, self.base_class) and
                    obj is not self.base_class):
                plugin_name = getattr(obj, 'PLUGIN_NAME', name.lower())
                try:
                    self.register(plugin_name, obj)
                    discovered += 1
                except PluginRegistrationError:
                    pass  # Already registered

        return discovered

    def create_instance(self, name: str, *args, **kwargs) -> T:
        """
        Create an instance of a registered plugin.

        Args:
            name: Name of the plugin
            *args: Positional arguments for the plugin constructor
            **kwargs: Keyword arguments for the plugin constructor

        Returns:
            Instance of the plugin
        """
        plugin_class = self.get(name)
        return plugin_class(*args, **kwargs)

    def __contains__(self, name: str) -> bool:
        """Support 'in' operator for checking plugin existence."""
        return name in self._plugins

    def __len__(self) -> int:
        """Return number of registered plugins."""
        return len(self._plugins)

    def __iter__(self):
        """Iterate over plugin names."""
        return iter(self._plugins)


def register_plugin(
    registry: PluginRegistry,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for registering a plugin class.

    Example:
        >>> @register_plugin(llm_registry, name="custom_llm")
        ... class CustomLLM(BaseLLM):
        ...     pass

    Args:
        registry: The registry to register with
        name: Optional name (defaults to class name in lowercase)
        metadata: Optional metadata about the plugin

    Returns:
        Decorator function
    """
    def decorator(cls: Type[T]) -> Type[T]:
        plugin_name = name or cls.__name__.lower()
        registry.register(plugin_name, cls, metadata)
        return cls
    return decorator


def plugin(
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to mark a class as a plugin for automatic discovery.

    Example:
        >>> @plugin(name="my_llm", metadata={"version": "1.0"})
        ... class MyLLM(BaseLLM):
        ...     pass

    Args:
        name: Plugin name (defaults to class name in lowercase)
        metadata: Optional metadata

    Returns:
        Decorator function
    """
    def decorator(cls: Type[T]) -> Type[T]:
        cls._plugin_name = name or cls.__name__.lower()
        cls._plugin_metadata = metadata or {}
        return cls
    return decorator


# =============================================================================
# Base Plugin Classes
# =============================================================================

class BasePlugin(ABC):
    """
    Abstract base class for all plugins.

    Provides common interface and utilities for plugin implementations.
    """

    # Override this in subclasses for auto-registration
    PLUGIN_NAME: Optional[str] = None

    @classmethod
    def get_name(cls) -> str:
        """Get the plugin name."""
        return cls.PLUGIN_NAME or cls.__name__.lower()

    @classmethod
    def get_description(cls) -> str:
        """Get the plugin description from docstring."""
        return cls.__doc__ or "No description available"


class BaseLLMPlugin(BasePlugin):
    """Base class for LLM backend plugins."""

    @abstractmethod
    def query(self, context: str, question: str, **kwargs) -> Dict[str, Any]:
        """
        Query the LLM.

        Args:
            context: Input context
            question: User query
            **kwargs: Additional arguments

        Returns:
            Dict containing 'response', 'latency', 'token_count', 'is_accurate'
        """
        pass

    def health_check(self) -> bool:
        """Check if the LLM backend is available."""
        return True


class BaseStrategyPlugin(BasePlugin):
    """Base class for memory strategy plugins."""

    @abstractmethod
    def process(self, context: str, query: str, history: List[str]) -> str:
        """
        Process context according to the strategy.

        Args:
            context: Current context
            query: Current query
            history: Conversation history

        Returns:
            Processed context string
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get strategy metrics (tokens used, compression ratio, etc.)."""
        pass


class BaseMetricPlugin(BasePlugin):
    """Base class for evaluation metric plugins."""

    @abstractmethod
    def compute(
        self,
        predictions: List[str],
        references: List[str],
        **kwargs
    ) -> Dict[str, float]:
        """
        Compute the metric.

        Args:
            predictions: Model predictions
            references: Ground truth references
            **kwargs: Additional arguments

        Returns:
            Dict of metric name to value
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Metric name."""
        pass

    @property
    def higher_is_better(self) -> bool:
        """Whether higher values indicate better performance."""
        return True


# =============================================================================
# Global Plugin Registries
# =============================================================================

# Import base LLM class for type checking
from common.llm import BaseLLM

# Create global registries
llm_registry = PluginRegistry("llm", base_class=BaseLLM)
strategy_registry = PluginRegistry("strategy", base_class=BaseStrategyPlugin)
metric_registry = PluginRegistry("metric", base_class=BaseMetricPlugin)


def initialize_default_plugins():
    """Register built-in plugins with the registries."""
    from common.llm import MockLLM, OllamaLLM

    # Register built-in LLM backends
    llm_registry.register("mock", MockLLM, {"description": "Mock LLM for testing"})
    llm_registry.register("ollama", OllamaLLM, {"description": "Ollama local LLM"})

    logger.info("Initialized default plugins")


def discover_all_plugins(plugins_dir: Optional[Path] = None):
    """
    Discover and register plugins from the plugins directory.

    Args:
        plugins_dir: Path to plugins directory (defaults to ./plugins)
    """
    if plugins_dir is None:
        plugins_dir = Path(__file__).parent.parent / "plugins"

    if not plugins_dir.exists():
        logger.warning(f"Plugins directory not found: {plugins_dir}")
        return

    # Discover LLM plugins
    llm_path = plugins_dir / "llm"
    if llm_path.exists():
        llm_registry.discover_plugins(llm_path)

    # Discover strategy plugins
    strategy_path = plugins_dir / "strategies"
    if strategy_path.exists():
        strategy_registry.discover_plugins(strategy_path)

    # Discover metric plugins
    metric_path = plugins_dir / "metrics"
    if metric_path.exists():
        metric_registry.discover_plugins(metric_path)


# =============================================================================
# Plugin Factory
# =============================================================================

class PluginFactory:
    """
    Factory for creating plugin instances from configuration.

    Example:
        >>> factory = PluginFactory()
        >>> llm = factory.create_llm("ollama", model_name="llama3.2:1b")
        >>> strategy = factory.create_strategy("select", top_k=3)
    """

    def __init__(self, auto_discover: bool = True):
        """
        Initialize the plugin factory.

        Args:
            auto_discover: Whether to automatically discover plugins
        """
        initialize_default_plugins()
        if auto_discover:
            discover_all_plugins()

    def create_llm(self, name: str, **kwargs) -> BaseLLM:
        """Create an LLM instance."""
        return llm_registry.create_instance(name, **kwargs)

    def create_strategy(self, name: str, **kwargs) -> BaseStrategyPlugin:
        """Create a strategy instance."""
        return strategy_registry.create_instance(name, **kwargs)

    def create_metric(self, name: str, **kwargs) -> BaseMetricPlugin:
        """Create a metric instance."""
        return metric_registry.create_instance(name, **kwargs)

    def list_available_llms(self) -> List[str]:
        """List available LLM plugins."""
        return llm_registry.list_plugins()

    def list_available_strategies(self) -> List[str]:
        """List available strategy plugins."""
        return strategy_registry.list_plugins()

    def list_available_metrics(self) -> List[str]:
        """List available metric plugins."""
        return metric_registry.list_plugins()
