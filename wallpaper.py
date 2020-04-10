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


def remove_tempfile(wpObject):
    try:
        os.remove(wpObject.filename)
    except Exception as exception:
        wpObject.errors[__name__ + ".remove_tempfile"] = exception
    
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


def parseGlobalParameters(arguments):
    assert(arguments[0][0] == "GLOBAL")

    parameters = cmdline.applyArgList(PARAMETERS, arguments[0][1])
    if parameters["help"]:
        showGlobalHelp(PARAMETERS)
        exit(0)

    if parameters["plugins"]:
        showPluginList(addons)
        exit(0)

    if parameters["show"]:
        showPlugin(addons, parameters["show"])
        exit(0)
        
    if parameters["silent"]:
        return 0
    elif parameters["verbose"]:
        return 2
    return 1


def parsePluginParameters(addons, id, parameters):
    matched = plugins.resolve(addons, id)
    if len(matched) < 1:
        raise Exception("Unable to identify plugin {}!".format(id))
    elif len(matched) > 1:
        raise Exception("Plugin code {} is not unique (candidates are {})!" \
                        .format(id, ", ".join(matched)))
    
    name = matched[0]
    plugin = plugins.get(addons, name)[name]
    return { "name": name, "plugin": plugin,
             "config": cmdline.applyArgList(plugin.PARAMETERS, parameters) }


def parseProcessingChain(ingest, addons, arguments):
    chain = [ parsePluginParameters(ingest, arguments[1][0], arguments[1][1]) ]

    for segment in arguments[2:]:
        chain.append(parsePluginParameters(addons, segment[0], segment[1]))

    return chain


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
#TODO Verify there is exactly one get task
#TODO use all strings in lower case

ingest = plugins.load(["get"])
addons = plugins.load(["modify", "apply"])

arguments = cmdline.segment(sys.argv[1:])

verbosity = parseGlobalParameters(arguments)
processingChain = parseProcessingChain(ingest, addons, arguments)

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

download(img)

# Execute remainder of the chain
for step in processingChain[1:]:
    if verbosity > 1:
        print(" - {}".format(step["name"]))
        print("   configuration: {}".format(step["config"]))

    step["plugin"].do(img, step["config"])

remove_tempfile(img)

# Give feedback again
if verbosity > 1:
    print("done!")

if verbosity > 0:
    if img.errors:
        print("There were errors:")
        for error in img.errors:
            print("E {}: {}".format(error, img.errors[error]))

