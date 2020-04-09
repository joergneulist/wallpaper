from urllib.request import urlretrieve
        

class wpObject:
    def __init__(self):
        self.url = None
        self.caption = None
        self.description = None
        self.errors = {}

    def __str__(self):
        return "\"{}\" ({})".format(self.caption, self.url)
