from oem_framework.plugin import Plugin

import imp
import inspect
import logging
import os
import sys

log = logging.getLogger(__name__)

PLUGIN_DATABASE_PREFIX = 'oem-database-'
PLUGIN_FORMAT_PREFIX = 'oem-format-'

PLUGIN_PREFIXES = [
    PLUGIN_DATABASE_PREFIX,
    PLUGIN_FORMAT_PREFIX
]


class PluginManager(object):
    search_paths = [os.path.abspath(os.curdir)]

    _available = {'database': {}, 'format': {}}
    _loaded = {'database': {}, 'format': {}}

    @classmethod
    def discover(cls):
        # Reset current state
        cls._available = {'database': {}, 'format': {}}

        # Discover available plugins
        for name, path in cls._list_plugins():
            # Parse plugin name
            kind, key = cls._parse_package_name(name)

            # Store available plugin
            if key in cls._available[kind]:
                log.warn('Found multiple installations of %r, using installation at %r', name, cls._available[kind][key])
                continue

            cls._available[kind][key] = path

    @classmethod
    def get(cls, kind, key):
        # Ensure plugin is loaded
        if key not in cls._loaded[kind]:
            # Load plugin
            if not cls.load(kind, key):
                return None

        # Return loaded plugin
        return cls._loaded[kind][key]

    @classmethod
    def load(cls, kind, key):
        # Parse module `key`
        plugins = cls._parse_plugins_key(key)

        for name, module_name in plugins:
            # Retrieve plugin installation descriptor
            descriptor = cls._available[kind].get(name)

            if descriptor is None:
                log.warn('Unable to find installation of %r plugin', key)
                return False

            # Try load the plugin module
            module = cls._load_module(descriptor, module_name)

            if module is None:
                return False

        # Find plugin class
        plugin = None

        for value in module.__dict__.itervalues():
            if not inspect.isclass(value):
                continue

            if value.__module__ != module.__name__:
                continue

            if not issubclass(value, Plugin):
                continue

            if value.__key__ is None:
                continue

            # Found plugin
            plugin = value
            break

        if plugin is None:
            log.warn('Unable to find plugin in %r', module)
            return False

        # Store loaded plugin
        cls._loaded[kind][key] = plugin
        return True

    @classmethod
    def _parse_plugins_key(cls, key):
        if not key:
            return None, None

        plugins = key.split('+')

        result = []

        # Parse extra plugins
        for plugin_key in plugins[:-1]:
            # Parse plugin key
            plugin_name, plugin_module = cls._parse_plugin_key(plugin_key)

            if not plugin_name or not plugin_module:
                continue

            result.append((plugin_name, plugin_module))

        # Parse main plugin
        result.append(cls._parse_plugin_key(key.replace('+', '-')))

        return result

    @classmethod
    def _parse_plugin_key(cls, key):
        # Parse plugin name
        fragments = key.split('/', 1)

        if len(fragments) == 1:
            return fragments[0], 'main'

        if len(fragments) == 2:
            return fragments[0], fragments[1]

        return None, None

    @classmethod
    def _load_module(cls, descriptor, module_name):
        # Load package
        fp, filename, (suffix, mode, type) = imp.find_module(
            descriptor['package_name'],
            [descriptor['root_path']]
        )

        if type != imp.PKG_DIRECTORY:
            log.warn('Invalid package at %r (expected python package)', descriptor['package_path'])
            return None

        try:
            package = imp.load_module(descriptor['package_name'], fp, filename, (suffix, mode, type))
        except Exception, ex:
            log.warn('Unable to load package %r - %s', descriptor['package_name'], ex, exc_info=True)
            return None

        # Load module
        fp, filename, (suffix, mode, type) = imp.find_module(module_name, package.__path__)

        if type not in [imp.PY_SOURCE, imp.PY_COMPILED]:
            log.warn('Invalid module at %r (expected python source or compiled module)', descriptor['module_path'])
            return None

        name = descriptor['package_name'] + '.' + module_name

        try:
            module = imp.load_module(name, fp, filename, (suffix, mode, type))
        except Exception, ex:
            log.warn('Unable to load module %r - %s', name, ex, exc_info=True)
            return None

        return module

    @classmethod
    def _list_plugins(cls):
        for package_path in cls.search_paths + sys.path:
            # Ignore invalid paths
            if package_path.endswith('.egg') or package_path.endswith('.zip'):
                continue

            if not os.path.exists(package_path):
                continue

            # List items in `package_path`
            try:
                items = os.listdir(package_path)
            except Exception, ex:
                log.debug('Unable to list directory %r - %s', package_path, ex, exc_info=True)
                continue

            # Find valid plugins in `items`
            for name in items:
                path = os.path.join(package_path, name)

                # Ignore files
                if os.path.isfile(path):
                    continue

                # Ensure package name matches a valid plugin prefix
                if not cls._is_plugin(name):
                    continue

                # Find module
                module_name = name.replace('-', '_')
                module_path = os.path.join(path, module_name)

                if not os.path.exists(module_path):
                    continue

                yield name, {
                    'root_path': path,

                    'package_path': module_path,
                    'package_name': module_name
                }

    @classmethod
    def _parse_package_name(cls, name):
        if not name:
            return None, None

        fragments = name.split('-', 2)

        if fragments[0] != 'oem':
            return None, None

        if len(fragments) < 3:
            return None, None

        return fragments[1], fragments[2]

    @classmethod
    def _is_plugin(cls, name):
        for prefix in PLUGIN_PREFIXES:
            if name.startswith(prefix):
                return True

        return False
