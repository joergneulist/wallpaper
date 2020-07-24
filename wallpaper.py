#!/usr/bin/python3

import argparse
from importlib import import_module
import json
import os
from urllib.request import urlretrieve
import string
import sys

import chainscript
import plugins
from wpobject import wpObject


def showParameterList(paramDef):
    if len(paramDef):
        for param in paramDef:
            data = paramDef[param]
            print('  -{} (default: \'{}\')'.format(param, data['default']))
            print('   {}'.format(data['description']))


def showPluginList(pluginsGet, pluginsProc):
    for name in pluginsGet:
        plugin = pluginsGet[name]
        print('* GET: {}'.format(name))
    for name in pluginsProc:
        plugin = pluginsProc[name]
        print('* PROCESS: {}'.format(name))


def showPlugin(pluginsGet, pluginsProc, identifier):
    for id, plugin in plugins.get(pluginsGet, identifier).items():
        print('GET Plugin {}'.format(id))
        print('  {}'.format(plugin.DESCRIPTION))
        showParameterList(plugin.PARAMETERS)
    for id, plugin in plugins.get(pluginsProc, identifier).items():
        print('PROCESS Plugin {}'.format(id))
        print('  {}'.format(plugin.DESCRIPTION))
        showParameterList(plugin.PARAMETERS)



def findFile(name, path, ext):
    if os.access(name, os.R_OK):
        return name
    if os.access(name + ext, os.R_OK):
        return name + ext
    
    name = os.path.join(path, name)
    if os.access(name, os.R_OK):
        return name
    if os.access(name + ext, os.R_OK):
        return name + ext



# _MAIN_ CODE #################################################################

exec_rel = os.path.join(os.getcwd(), sys.argv[0])
exec_abs = os.path.realpath(exec_rel)
path = os.path.dirname(exec_abs)

plugGet = plugins.load(path, 'get')
plugProc = plugins.load(path, 'proc')

parser = argparse.ArgumentParser(description = 'Find wallpapers online and manipulate them.', add_help = False)
parser.add_argument('script', nargs = '?', help = 'the wallpaper script to execute (look in subdir scripts)')
parser.add_argument('-h', '--help', action = 'store_true', help = 'show global or script help and exit')
parser.add_argument('-p', '--plugins', nargs = '?', const = '', help = 'list all plugins OR show details for a given plugin')
parser.add_argument('-q', '--quiet', action = 'store_true', help = 'give no output (even if errors occur)')
parser.add_argument('-v', '--verbose', action = 'store_true', help = 'give detailed output')

arguments, script_arguments = parser.parse_known_args()

if arguments.help and arguments.script is None:
    parser.print_help()

elif arguments.plugins is not None:
    if len(arguments.plugins) == 0:
        showPluginList(plugGet, plugProc)
    else:
        showPlugin(plugGet, plugProc, arguments.plugins)

else:
    verbosity = 1
    if arguments.quiet:
        verbosity = 0
    elif arguments.verbose:
        verbosity = 2

    processingChain = chainscript.parse(plugGet, plugProc, findFile(arguments.script, os.path.join(path, 'scripts'), '.json'), arguments.help, script_arguments)

    # Give feedback
    if verbosity > 0:
        print('Executing: {}'.format(' - '.join([step['name'] for step in processingChain])))

    # Execute get task
    img = wpObject()
    step = processingChain[0]
    if verbosity > 1:
        print(' - {}'.format(step['name']))
        print('   configuration: {}'.format(step['config']))

    step['plugin'].do(img, step['config'])
    if verbosity > 1:
        print(img.caption)
        print(img.description)

    img.download()

    # Execute remainder of the chain
    for step in processingChain[1:]:
        if verbosity > 1:
            print(' - {}'.format(step['name']))
            print('   configuration: {}'.format(step['config']))

        step['plugin'].do(img, step['config'])

    # Give feedback again
    if verbosity > 1:
        print('done!')

    if verbosity > 0:
        if img.errors:
            print('There were errors:')
            for error in img.errors:
                print('E {}: {}'.format(error, img.errors[error]))

