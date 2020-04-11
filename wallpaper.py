#!/usr/bin/python3

from importlib import import_module
import os
from urllib.request import urlretrieve
import string
import sys

import cmdline
import plugins
from wpobject import wpObject


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
    print("{} -v bing -index=1 eng f -i=/var/opt/wallpaper/wall.jpg".format(sys.argv[0]))
    print("retrieves yesterday's image from bing, engraves the caption on the image, and stores it in the given location.")
    print()


def showPluginList(pluginsGet, pluginsProc):
    for name in pluginsGet:
        plugin = pluginsGet[name]
        print("* GET: {}".format(name))
    for name in pluginsProc:
        plugin = pluginsProc[name]
        print("* PROCESS: {}".format(name))


def showPlugin(pluginsGet, pluginsProc, identifier):
    for id, plugin in plugins.get(pluginsGet, identifier).items():
        print("GET Plugin {}".format(id))
        print("  {}".format(plugin.DESCRIPTION))
        showParameterList(plugin.PARAMETERS)
    for id, plugin in plugins.get(pluginsProc, identifier).items():
        print("PROCESS Plugin {}".format(id))
        print("  {}".format(plugin.DESCRIPTION))
        showParameterList(plugin.PARAMETERS)


def parseGlobalParameters(pluginsGet, pluginsProc, arguments):
    assert(arguments[0][0] == "GLOBAL")

    parameters = cmdline.applyArgList(PARAMETERS, arguments[0][1])
    if parameters["help"]:
        showGlobalHelp(PARAMETERS)
        exit(0)

    if parameters["plugins"]:
        showPluginList(pluginsGet, pluginsProc)
        exit(0)

    if parameters["show"]:
        showPlugin(pluginsGet, pluginsProc, parameters["show"])
        exit(0)
        
    if parameters["silent"]:
        return 0
    elif parameters["verbose"]:
        return 2
    return 1


def parsePluginParameters(pluginList, id, parameters):
    matched = plugins.resolve(pluginList, id)
    if len(matched) < 1:
        raise Exception("Unable to identify plugin {}!".format(id))
    elif len(matched) > 1:
        raise Exception("Plugin code {} is not unique (candidates are {})!" \
                        .format(id, ", ".join(matched.keys())))
    
    return { "name": matched[0], "plugin": pluginList[matched[0]],
             "config": cmdline.applyArgList(pluginList[matched[0]].PARAMETERS, parameters) }


def parseProcessingChain(pluginsGet, pluginsProc, arguments):
    chain = [ parsePluginParameters(pluginsGet, arguments[1][0], arguments[1][1]) ]

    for segment in arguments[2:]:
        chain.append(parsePluginParameters(pluginsProc, segment[0], segment[1]))

    return chain


# _MAIN_ CODE #################################################################

# TODO: think of a better command line syntax

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


plugGet = plugins.load("get")
plugProc = plugins.load("proc")

arguments = cmdline.segment(sys.argv[1:])

verbosity = parseGlobalParameters(plugGet, plugProc, arguments)
processingChain = parseProcessingChain(plugGet, plugProc, arguments)

# Give feedback
if verbosity > 0:
    print("Executing: {}".format(" - ".join([step["name"] for step in processingChain])))

# Execute get task
img = wpObject()
step = processingChain[0]
if verbosity > 1:
    print(" - {}".format(step["name"]))
    print("   configuration: {}".format(step["config"]))

step["plugin"].do(img, step["config"])
if verbosity > 1:
    print(img.caption)
    print(img.description)

img.download()

# Execute remainder of the chain
for step in processingChain[1:]:
    if verbosity > 1:
        print(" - {}".format(step["name"]))
        print("   configuration: {}".format(step["config"]))

    step["plugin"].do(img, step["config"])

# Give feedback again
if verbosity > 1:
    print("done!")

if verbosity > 0:
    if img.errors:
        print("There were errors:")
        for error in img.errors:
            print("E {}: {}".format(error, img.errors[error]))

