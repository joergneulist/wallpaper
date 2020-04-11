from importlib import import_module
import os

import helpers


### PLUGIN DETAILS ############################################################
#
# A plugin must implement:
# DESCRIPTION: string, to be displayed on the command line"
# PARAMETERS: dict of dicts, detailing the parameter structure
#             { "parameter1": {"description": string, "default": default_value},
#               ...}
# parseParameter(name, value)
#   Parse a given string representation for a parameter. name is already
#   checked, so it will be correct. Check value for correctness,
#   returning the corrected param value (may be None) and a natural
#   language parse result (may also be None).
# do(wpObject, parameters)
#   implement the actual processing step

def load(path):
    plugins = {}
    for file in os.listdir(path):
        fileParts = file.split(".")
        base = fileParts[0]
        name = path + "." + base
        if len(fileParts) < 2 or not fileParts[1] == "py":
            continue
        
        try:
            module = import_module(name)
            if module.DESCRIPTION is None \
            or module.PARAMETERS is None \
            or module.parseParameter is None \
            or module.do is None:
                raise Exception("not a well-formed plugin!")
            
            plugins[base.lower()] = module

        except Exception as exception:
            print("Unable to load plugin from {}/{}: {}"\
                    .format(path, file, exception))

    return plugins


def resolve(plugins, identifier):
    return helpers.resolveDictKey(identifier, plugins)


def get(plugins, identifier):
    return {id: plugins[id] for id in resolve(plugins, identifier)}
