
# Plugin Architecture for Frostfire IoT Hub

## Overview

The **Frostfire IoT Hub** is designed to be modular and extensible through a flexible plugin architecture. This allows users to define and load plugins dynamically to handle various IoT device interactions. The plugins are located in the `/plugins` directory, and they adhere to a standard interface to ensure consistency and ease of use.

## Plugin Structure

The plugins follow a directory-based structure where each plugin can reside either as a single Python file or within a subdirectory containing multiple files. While `__init__.py` files are not required, plugins can still use them to create more complex structures if needed.

### Example Directory Structure:

```plaintext
app/
├── plugins/
│   ├── tv_plugin.py
│   ├── bravia/
│   │   ├── bravia_plugin.py
│   │   └── services/
│   │       └── tv_service.py
```

In the example above:
- `tv_plugin.py` is a standalone plugin.
- `bravia` is a more complex plugin that has its own subdirectory with additional services.

## The `IotPlugin` Interface

All plugins must implement the `IotPlugin` interface, which defines the core methods that the plugin must provide to interact with the system.

```python
from abc import ABC, abstractmethod

class IotPlugin(ABC):
    """
    Abstract base class for IoT plugins. All plugins must implement the defined methods.
    """

    @abstractmethod
    async def initialize(self):
        """
        This method handles initialization logic for the plugin, such as setting up connections
        or loading configurations.
        """
        pass

    @abstractmethod
    def can_handle_topic(self, topic: str) -> bool:
        """
        Checks if the plugin can handle the given MQTT topic.
        """
        pass

    @abstractmethod
    def get_topics(self) -> list:
        """
        Returns a list of topics the plugin is subscribed to.
        """
        pass

    @abstractmethod
    async def process_message(self, topic: str, payload: str):
        """
        Processes the message received from an MQTT topic.
        """
        pass

    @abstractmethod
    async def shutdown(self):
        """
        Handles plugin cleanup and shutdown logic.
        """
        pass
```

### Important Notes
- Every plugin must implement all methods defined in the `IotPlugin` interface.
  
## Plugin Loading Process

The Frostfire IoT Hub dynamically loads plugins from the `/plugins` directory by recursively traversing the directory structure. The following steps are performed during the loading process:

1. **Directory Traversal**: The system uses `os.walk()` to recursively find all Python files (`*.py`) in the `/plugins` directory.
2. **Module Import**: Each Python file is dynamically imported using `importlib.import_module()`.
3. **Class Inspection**: The system inspects each module to find classes that implement the `IotPlugin` interface.
4. **Initialization**: Each plugin is instantiated and its `initialize()` method is called.
5. **Error Handling**: If any issues arise during plugin loading, errors are logged, and the loading process continues.

### Example Plugin Loading Code:

```python
async def load_plugins(self):
    """
    Dynamically load all plugins from the 'plugins' directory that implement the IPlugin interface,
    and call their initialize method.
    """
    plugins = []

    for root, dirs, files in os.walk(self.plugin_dir):
        for file_name in files:
            if file_name.endswith('.py') and not file_name.startswith('__'):
                relative_path = os.path.relpath(root, self.plugin_dir).replace(os.sep, ".")
                module_path = f"app.plugins.{relative_path}.{file_name[:-3]}" if relative_path != '.' else f"app.plugins.{file_name[:-3]}"
                
                try:
                    module = importlib.import_module(module_path)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, IotPlugin) and obj is not IotPlugin:
                            plugin_instance = obj()
                            await plugin_instance.initialize()
                            plugins.append(plugin_instance)
                except Exception as e:
                    self.logger.error(f"Error loading plugin from {module_path}: {e}")

    return plugins
```

### Plugin Topics

Each plugin can define the topics it subscribes to through the `get_topics()` method. The topics should be returned as a list, with MQTT wildcard support (e.g., `domus/devices/tv/#`).

## Example Plugin

To illustrate the basic structure, here is an example plugin that can be placed in the `/plugins/example_plugin/` directory:

```python
# /plugins/example_plugin/example_plugin.py
from app.plugins.plugin_interface import IotPlugin

class ExamplePlugin(IotPlugin):
    async def initialize(self):
        print("ExamplePlugin initialized")

    def can_handle_topic(self, topic: str) -> bool:
        return topic.startswith("example/topic")

    def get_topics(self) -> list:
        return ["example/topic/#"]

    async def process_message(self, topic: str, payload: str):
        print(f"Received message on {topic}: {payload}")

    async def shutdown(self):
        print("ExamplePlugin shutting down")
```

## Conclusion

The plugin architecture of the **Frostfire IoT Hub** allows for flexible, scalable, and easily extensible functionality. By following the outlined structure, developers can create custom plugins that handle device-specific behavior, without modifying the core hub functionality.
