#!/usr/bin/python3

from importlib import import_module
import os
from urllib.request import urlretrieve

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


#TODO COMMAND LINE CONTROL
#TODO DO LESS WITH CLASSES

# STARTUP - First import plugins
plugin_domains = ["get", "modify", "apply"]
plugins = {}
for domain in plugin_domains:
    plugins[domain] = loadPlugins(domain)

# Parse command line
# TODO
selected = {}
selected["get"] = {"name": "bing", "parameters": {"index": 0, "zone": "de"} }
selected["modify"] = {"name": "engrave", "parameters": {
    "font": "DejaVuSans-BoldOblique.ttf", "size": 24, "fgcol": (255, 255, 255),
    "bgcol": (0, 0, 0), "position": (-10, -10), "padding": 5} }
selected["apply"] = {"name": "filesystem", "parameters": {
    "image": "/var/opt/wallpapers/wall.jpg",
    "text": "/var/opt/wallpapers/wall.txt"} }

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
