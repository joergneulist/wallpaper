from importlib import import_module
import os

import helpers
from wpplugin import wpPlugin


def load(paths):
    plugins = {}
    for path in paths:
        plugins[path] = {}
        for file in os.listdir(path):
            fileParts = file.split(".")
            base = fileParts[0]
            name = path + "." + base
            if len(fileParts) < 2 or not fileParts[1] == "py":
                continue
            
            try:
                module = import_module(name)
                pluginclass = getattr(module, base)
                if not issubclass(pluginclass, wpPlugin):
                    raise Exception("not a subclass of wpPlugin")
                
                plugins[path.lower()][base.lower()] = getattr(module, base)

            except Exception as exception:
                print("Unable to load plugin from {}/{}: {}"\
                      .format(path, file, exception))

    return plugins


def resolve(plugins, identifier):
    split = identifier.split(".")
    if len(split) > 1:
        domainInitial = split[0]
        nameInitial = split[1]
    else:
        domainInitial = None
        nameInitial = split[0]

    found = []
    for domain in helpers.resolveDictKey(domainInitial, plugins):
        for name in helpers.resolveDictKey(nameInitial, plugins[domain]):
            found.append("{}.{}".format(domain, name))
    
    return found


def get(plugins, identifier):
    return {id: plugins[id.split(".")[0]][id.split(".")[1]] \
            for id in resolve(plugins, identifier)}
