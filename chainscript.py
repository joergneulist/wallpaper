#!/usr/bin/python3

import argparse
import json
import plugins
import sys


def setupPlugin(step, pluginList):
    # Identify plugin:
    matched = plugins.resolve(pluginList, step['name'])
    if len(matched) < 1:
        raise Exception('Unable to identify plugin {}!'.format(step['name']))
    elif len(matched) > 1:
        raise Exception('Plugin code {} is not unique (candidates are {})!' \
                        .format(step['name'], ', '.join(matched)))
    
    step['name'] = matched[0]
    step['plugin'] = pluginList[step['name']]

    # Load default config:
    defaults = { key: value['default'] for key, value in step['plugin'].PARAMETERS.items() }

    # Load script config:
    if 'config' in step:
        defaults.update(step['config'])
    step['config'] = defaults


def setupParser(chain):
    help = ''
    for step in chain:
        help += step['plugin'].DESCRIPTION + '. '

    parser = argparse.ArgumentParser(description = help, add_help = False,
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    for step in chain:
        for arg, default in step['config'].items():
            help = '{}: {}'.format(step['name'], step['plugin'].PARAMETERS[arg]['description'])
            if 'alias' in step and arg in step['alias']:
                arg = step['alias'][arg]
            parser.add_argument('--' + arg, default = default, help = help)

    return parser


def configurePlugin(step, cmdLine):
    for arg in step['config']:
        alias = step['alias'][arg] if 'alias' in step and arg in step['alias'] else arg
        step['config'][arg] = cmdLine[alias]


def parse(plugGet, plugProc, script, help, arguments):
    with open(script) as config_file:
        chain = json.load(config_file)

    setupPlugin(chain[0], plugGet)
    for step in chain[1:]:
        setupPlugin(step, plugProc)

    parser = setupParser(chain)
    if help:
        parser.print_help()
        exit(0)
    cmdLine = vars(parser.parse_args(arguments))

    for step in chain:
        configurePlugin(step, cmdLine)

    return chain
