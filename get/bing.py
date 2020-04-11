import json

from helpers import getHtml, getJson

DESCRIPTION = "Get a wallpaper from the Microsoft Bing search engine"

PARAMETERS = {
    "index": {
        "description": "Bing allows retrieving older images; use 0 to get today's, 1 for yesterday's, etc.",
        "default": 0
    },
    "zone": {
        "description": "Bing may deliver different images based on the region (i.e. TLD)",
        "default": "de"
    }
}


def parseParameter(name, value):
    if name == "index":
        try:
            number = int(value)
        except Exception as exception:
            return None, str(exception)
        if number < 0:
            return None, "index must be non-negative!"
        else:
            return number, None

    return value, None # No checking of zone!


def do(wpObject, parameters):
    base_url = "http://www.bing.com"
    url = base_url + "/HPImageArchive.aspx?format=js&idx={0}&n=1&mkt={1}".format(parameters["index"], parameters["zone"])

    try:
        bing_data = getJson(url)["images"][0]

        wpObject.url = base_url + "/hpwp/" + bing_data["hsh"]
        wpObject.caption = bing_data["title"]
        wpObject.description = getHtml(bing_data["copyrightlink"]).find("div", class_ = "ency_desc").string 

    except Exception as exception:
        wpObject.errors[__name__] = exception

    return wpObject
