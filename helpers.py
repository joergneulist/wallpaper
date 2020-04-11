from bs4 import BeautifulSoup
import json
from urllib.request import urlopen


def isInitialOf(initial, fullString):
    return fullString[:len(initial)] == initial


def resolveDictKey(keyInitial, dictionary):
    keys = []
    for key in dictionary:
        if not keyInitial or isInitialOf(keyInitial, key):
            keys.append(key)
    return keys


def getFromWeb(url):
    return urlopen(url).read().decode("utf-8")


def getHtml(url):
    return BeautifulSoup(getFromWeb(url), features = "lxml")


def getJson(url):
    return json.loads(getFromWeb(url))

