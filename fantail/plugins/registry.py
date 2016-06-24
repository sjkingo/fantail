import importlib
import logging
import os

PLUGIN_TYPES = ('filter',)

# Will get populated with a PluginRegistry() instance when load_plugins() is
# called.
registry = None

class PluginRegisterException(Exception):
    pass

class PluginRegistry(object):
    """
    Registry of plugins that are loaded into fantail.
    """

    _plugins = {}

    def __init__(self):
        for plugin_type in PLUGIN_TYPES:
            self._plugins[plugin_type] = set()

    def __len__(self):
        return sum([len(p) for p in self._plugins.values()])

    def register(self, plugin_func):
        """
        Registers a new plugin function.
        Determines correct type of plugin automatically through
        the `plugin_func.plugin_type` attribute.
        """

        name = plugin_func.__name__
        if not hasattr(plugin_func, 'plugin_type'):
            raise PluginRegisterException('Plugin function `' + name +
                                          '` does not have a plugin_type attribute')

        t = plugin_func.plugin_type
        if t not in self._plugins:
            raise PluginRegisterException('Plugin type ' + t + ' unknown.')
        self._plugins[t].add(plugin_func)
        logging.debug('Registered new plugin `' + name + '` of type ' + t)

    @property
    def filters(self):
        return self._plugins['filter']

def load_plugins():
    """
    Imports all plugin modules from the `plugins` package and registers any
    valid register functions within.

    This should only be called once.
    """

    global registry
    if registry is not None:
        return
    registry = PluginRegistry()

    # Import and register each plugin
    for f in os.listdir(os.path.dirname(__file__)):
        if f.startswith('plugin_') and f.endswith('.py'):
            module_name = os.path.splitext(f)[0]
            dotted_path = 'plugins.' + module_name
            module = importlib.import_module(dotted_path)
            logging.debug('Imported plugin module `{}`'.format(dotted_path))

            func_names = [n for n in module.__dict__ if n.startswith('register_')]
            if len(func_names) == 0:
                logging.warning('Plugin module `{}` contains no register '
                                'functions'.format(dotted_path))
                continue

            for name in func_names:
                func = getattr(module, name)
                registry.register(func)

    logging.debug('Loaded {} plugin(s)'.format(len(registry)))
