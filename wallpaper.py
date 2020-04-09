#!/usr/bin/python3

from importlib import import_module
import os
from urllib.request import urlretrieve
import string
import sys

from wpobject import wpObject
from wpplugin import wpPlugin


def loadPlugins(path):
    plugins = {}
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
            
            plugins[base] = getattr(module, base)

        except Exception as exception:
            print("Unable to load plugin from {}: {}".format(file, exception))

    return plugins


def download(wpObject):
    try:
        wpObject.filename, _ = urlretrieve(wpObject.url)
    except Exception as exception:
        wpObject.errors[__name__ + ".download"] = exception
    
    return wpObject


def isInitialOf(initial, fullString):
    return fullString[:len(initial)] == initial


def resolveDictKey(keyInitial, dictionary):
    keys = []
    for key in dictionary:
        if not keyInitial or isInitialOf(keyInitial, key):
            keys.append(key)
    return keys


def crackParameter(cmdline, paramList):
    split = cmdline[1:].split("=")
    value = "=".join(split[1:]) if len(split) > 1 else None
    names = resolveDictKey(split[0], paramList)
    if len(names) != 1:
        return None, None
    
    return names[0], value


def resolvePlugin(plugins, identifier):
    split = identifier.split(".")
    if len(split) > 1:
        domain = split[0]
        name = split[1]
    else:
        domain = None
        name = split[0]

    found = []
    for domain in resolveDictKey(domain, plugins):
        for name in resolveDictKey(name, plugins[domain]):
            found.append("{}.{}".format(domain, name))
    return found


def getPlugin(plugins, identifier):
    return {id: plugins[id.split(".")[0]][id.split(".")[1]] for id in resolvePlugin(plugins, identifier)}


def showGlobalHelp():
    print("Command line parameters:")
    print()
    print("[global parameters] [plugin1 [plugin1-parameters [plugin2 [plugin2-parameters ...]]]]")
    print()
    print("Global Parameters:")
    print("  -help")
    print("   show this explanation")
    print("  -help=plugin")
    print("   show detailed explanation for the given plugin")
    print("  -plugins")
    print("   list all plugins")
    print("  -silent")
    print("   give no output (even if errors occur)")
    print("  -verbose")
    print("   give detailed output")
    print()
    print(" * the domain (initial) part of a plugin may be left out, as long as its name is still unique")
    print(" * plugin and parameter names may be abbreviated, as long as they are still unique")
    print(" * the program will set an exit code of 1 to indicate errors, 0 otherwise")
    print(" * You have to select *exactly* one get-Plugin. For all others, you are free to choose.")
    print()
    print("Example:")
    print("{} -v get.bing -i=1 eng apply.f -i=/var/opt/wallpaper/wall.jpg".format(sys.argv[0]))
    print("retrieves yesterday's image from bing, engraves the caption on the image, and stores it in the given location.")
    print()

    return 0


def showPluginList(plugins, domain = None):
    if not domain:
        for domain in plugins:
            showPluginList(plugins, domain)

    else:
        for name in plugins[domain]:
            plugin = plugins[domain][name]
            print("* {}.{}".format(domain, name))

    return 0


def showPlugin(plugins, identifier):
    matchingPlugins = getPlugin(plugins, identifier)
    for id in matchingPlugins:
        plugin = matchingPlugins[id]
        print("Plugin {}".format(id))
        print("  {}".format(plugin.DESCRIPTION))

        if len(plugin.PARAMETERS):
            for param in plugin.PARAMETERS:
                data = plugin.PARAMETERS[param]
                print("  -{} (default: \"{}\")".format(param, data["default"]))
                print("   {}".format(data["description"]))

    return 0


def setVerbosity(params, target):
    params["verbosity"] = target


def parseGlobalParameters():
    params = {}
    setVerbosity(params, 1)

    plugin = None
    for param in sys.argv[1:]:
        if param[0] != '-':
            break

        parameters = {
            "help": lambda value: showPlugin(plugins, value) if value else showGlobalHelp(),
            "plugins": lambda value: showPluginList(plugins),
            "silent": lambda value: setVerbosity(params, 0),
            "verbose": lambda value: setVerbosity(params, 2)
        }
        name, value = crackParameter(param, list(parameters.keys()))
        if name:
            result = parameters[name](value)
            if result is not None:
                exit(result)

        else:
            print("Could not parse parameter \"{}\"!".format(param))
            print()
            showGlobalHelp()
            exit(1)

    return params

# _MAIN_ CODE #################################################################

#TODO DO LESS WITH CLASSES
#TODO use all strings in lower case
#TODO use plugin parameter approach for global parameters as well

# STARTUP - First import plugins
plugins = {}
for domain in ["get", "modify", "apply"]:
    plugins[domain] = loadPlugins(domain)

# Parse command line, global parameters
verbosity = parseGlobalParameters()["verbosity"] # silent = 0, verbose = 2

# Parse command line, plugins and their parameters
exit(3)
for param in sys.argv[1:]:
    if param[0] == '-':
        split = param[1:].split("=")
        name = split[0]
        value = split[1] if len(split) > 1 else None
        print("{}, parameter {}={}".format(plugin if plugin else "<global>", name, value))
    else:
        split = param.split(".")
        if len(split) > 1:
            domain = split[0]
            name = split[1]
        else:
            domain = None
            name = split[0]

        plugin = resolvePlugin(plugins, domain, name)
        print("select plugin {}".format(plugin))


selected = {}
selected["get"] = {"name": "bing", "parameters": {"index": 0, "zone": "de"} }
selected["modify"] = {"name": "engrave", "parameters": {
    "font": "DejaVuSans-BoldOblique.ttf", "size": 24, "fgcol": (255, 255, 255),
    "bgcol": (0, 0, 0), "position": (-10, -10), "padding": 5} }
selected["apply"] = {"name": "filesystem", "parameters": {
    "image": "/var/opt/wallpapers/wall.jpg",
    "text": "/var/opt/wallpapers/wall.txt"} }

exit()

# Execute chosen get task
img = wpObject()
if not selected["get"]["name"] in plugins["get"]:
    raise NotImplementedError("Plugin get.{} does not exist!".format(selected["get"]["name"]))
plugins["get"][selected["get"]["name"]].do(img, selected["get"]["parameters"])

# Retrieve file
download(img)

# Execute chosen modify tasks
if not selected["modify"]["name"] in plugins["modify"]:
    raise NotImplementedError("Plugin modify.{} does not exist!".format(selected["modify"]["name"]))
plugins["modify"][selected["modify"]["name"]].do(img, selected["modify"]["parameters"])

# Execute chosen apply tasks
if not selected["apply"]["name"] in plugins["apply"]:
    raise NotImplementedError("Plugin apply.{} does not exist!".format(selected["apply"]["name"]))
plugins["apply"][selected["apply"]["name"]].do(img, selected["apply"]["parameters"])

print(img)
for error in img.errors:
    print("E {}: {}".format(error, img.errors[error]))
