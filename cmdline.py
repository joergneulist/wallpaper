import helpers


def segment(argvector):
    section ="GLOBAL"
    arguments = {section: []}
    for arg in argvector:
        if arg[0] != "-": 
            section = arg
            arguments[section] = []
        
        else:
            split = arg[1:].split("=")
            key = split[0]
            value = "=".join(split[1:]) if len(split) > 1 else True
            arguments[section].append((key, value))

    return arguments


def applyArgList(paramDef, argList):
    parameters = {}

    for paramCandidate in argList:
        paramNames = helpers.resolveDictKey(paramCandidate[0], paramDef)
        if len(paramNames) < 1:
            raise Exception("Unable to identify parameter {}!".format(paramCandidate))
        elif len(paramNames) > 1:
            raise Exception("Parameter code {} is not unique (candidates are {})!".format(paramCandidate, ", ".join(paramNames)))
        
        parameters[paramNames[0]] = paramCandidate[1]
    
    for param in paramDef:
        if param not in parameters:
            parameters[param] = paramDef[param]["default"]
    
    return parameters
