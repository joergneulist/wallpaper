from bs4 import BeautifulSoup
from urllib.request import urlopen

class wpPlugin:

    ### IMPLEMENT #############################################################

    DESCRIPTION = "Describe the plugin functionality for display on the command line"

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


    @staticmethod
    def parseParameter(name, value):
        # Parse a given string representation for a parameter. name is already
        # checked, so it will be correct. Check value for correctness,
        # returning the corrected param value (may be None) and a natural
        # language parse result (may also be None).
        # e.g.
        # number = int(value)
        # if number < 0:
        #   return None, "index must be non-negative!"
        # else:
        #   return number, None
        raise NotImplementedError()


    @staticmethod
    def do(wpObject, parameters):
        raise NotImplementedError()


    ### HELPERS ###############################################################

    @staticmethod
    def getHtml(url):
        return BeautifulSoup(wpPlugin.getFromWeb(url), features = "lxml")


    @staticmethod
    def getFromWeb(url):
        return urlopen(url).read().decode("utf-8")


    ### INTERNAL STUFF ########################################################

    def __init__(self):
        raise NotImplementedError()


