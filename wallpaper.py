#!/usr/bin/python3

from importlib import import_module
import os
from urllib.request import urlretrieve
import string
import sys

import cmdline
import plugins
from wpobject import wpObject


def download(wpObject):
    try:
        wpObject.filename, _ = urlretrieve(wpObject.url)
    except Exception as exception:
        wpObject.errors[__name__ + ".download"] = exception
    
    return wpObject


def showParameterList(paramDef):
    if len(paramDef):
        for param in paramDef:
            data = paramDef[param]
            print("  -{} (default: \"{}\")".format(param, data["default"]))
            print("   {}".format(data["description"]))


def showGlobalHelp(paramDef):
    print("Command line parameters:")
    print()
    print("[global parameters] [plugin1 [plugin1-parameters [plugin2 [plugin2-parameters ...]]]]")
    print()
    print("Global Parameters:")
    showParameterList(paramDef)
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


def showPluginList(addons, domain = None):
    if not domain:
        for domain in addons:
            showPluginList(addons, domain)

    else:
        for name in addons[domain]:
            plugin = addons[domain][name]
            print("* {}.{}".format(domain, name))

    return 0


def showPlugin(addons, identifier):
    matchingaddons = getPlugin(addons, identifier)
    for id in matchingaddons:
        plugin = matchingaddons[id]
        print("Plugin {}".format(id))
        print("  {}".format(plugin.DESCRIPTION))
        showParameterList(plugin.PARAMETERS)


# _MAIN_ CODE #################################################################

PARAMETERS = {
    "help": {
        "description": "show this explanation",
        "default": None
    },
    "plugins": {
        "description": "list all plugins",
        "default": None
    },
    "show": {
        "description": "show detailed explanation for the given plugin",
        "default": None
    },
    "silent": {
        "description": "give no output (even if errors occur)",
        "default": None
    },
    "verbose": {
        "description": "give detailed output",
        "default": None
    }
}

#TODO DO LESS WITH CLASSES
#TODO use all strings in lower case

addons = plugins.load(["get", "modify", "apply"])

arguments = cmdline.segment(sys.argv[1:])

try:
    parameters = cmdline.applyArgList(PARAMETERS, arguments["GLOBAL"])

except Exception as ex:
    print(ex)
    showGlobalHelp(PARAMETERS)
    exit(1)

if parameters["help"]:
    showGlobalHelp(PARAMETERS)
    exit(0)

if parameters["plugins"]:
    showPluginList(addons)
    exit(0)

if parameters["show"]:
    showPlugin(addons, parameters["show"])
    exit(0)
    
verbosity = 1
if parameters["silent"]:
    verbosity = 0
elif parameters["verbose"]:
    verbosity = 2


for id in arguments:
    if id != "GLOBAL":
        matched = plugins.resolve(addons, id)
        if len(matched) < 1:
            raise Exception("Unable to identify plugin {}!".format(id))
        elif len(matched) > 1:
            raise Exception("Plugin code {} is not unique (candidates are {})!".format(id, ", ".join(matched.keys())))
        print(matched[0])

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

        plugin = resolvePlugin(addons, domain, name)
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
if not selected["get"]["name"] in addons["get"]:
    raise NotImplementedError("Plugin get.{} does not exist!".format(selected["get"]["name"]))
addons["get"][selected["get"]["name"]].do(img, selected["get"]["parameters"])

# Retrieve file
download(img)

# Execute chosen modify tasks
if not selected["modify"]["name"] in addons["modify"]:
    raise NotImplementedError("Plugin modify.{} does not exist!".format(selected["modify"]["name"]))
addons["modify"][selected["modify"]["name"]].do(img, selected["modify"]["parameters"])

# Execute chosen apply tasks
if not selected["apply"]["name"] in addons["apply"]:
    raise NotImplementedError("Plugin apply.{} does not exist!".format(selected["apply"]["name"]))
addons["apply"][selected["apply"]["name"]].do(img, selected["apply"]["parameters"])

print(img)
for error in img.errors:
    print("E {}: {}".format(error, img.errors[error]))
