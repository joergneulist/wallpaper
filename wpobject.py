import os
from urllib.request import urlretrieve
        

class wpObject:
    def __init__(self):
        self.url = None
        self.caption = None
        self.description = None
        self.errors = {}
        self.filename = None

    def __del__(self):
        if self.filename:
            os.remove(self.filename)

    def __str__(self):
        return "\"{}\" ({})".format(self.caption, self.url)

    def download(self):
        try:
            self.filename, _ = urlretrieve(self.url)
        except Exception as exception:
            self.errors[__name__ + ".download"] = exception
        
        return self



