#!/usr/bin/python3

import argparse
import json
import plugins
import sys


def setupPlugin(step, pluginList, parser):
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
    
    # Load command line config:
    for arg, default in step['config'].items():
        help = '{}: {}'.format(step['name'], step['plugin'].PARAMETERS[arg]['description'])
        if 'alias' in step and arg in step['alias']:
            arg = step['alias'][arg]
        parser.add_argument('--' + arg, default = default, help = help)


def configurePlugin(step, cmdLine):
    for arg in step['config']:
        alias = step['alias'][arg] if 'alias' in step and arg in step['alias'] else arg
        step['config'][arg] = cmdLine[alias]


def parse(plugGet, plugProc, script, help, arguments):
    with open(script) as config_file:
        data = json.load(config_file)

    parser = argparse.ArgumentParser(description = data['help'], add_help = False,
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    setupPlugin(data['chain'][0], plugGet, parser)
    for step in data['chain'][1:]:
        setupPlugin(step, plugProc, parser)

    if help:
        parser.print_help()
        exit(0)
    
    cmdLine = vars(parser.parse_args(arguments))
    for step in data['chain']:
        configurePlugin(step, cmdLine)

    return data['chain']
