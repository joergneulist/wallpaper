def isInitialOf(initial, fullString):
    return fullString[:len(initial)] == initial


def resolveDictKey(keyInitial, dictionary):
    keys = []
    for key in dictionary:
        if not keyInitial or isInitialOf(keyInitial, key):
            keys.append(key)
    return keys
