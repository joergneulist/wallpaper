import os
import shutil

from wpplugin import wpPlugin

class filesystem(wpPlugin):

    DESCRIPTION = "Store a wallpaper in a specific location in the filesystem"

    PARAMETERS = {
        "image": {
            "description": "Target location for the image file, may be None",
            "default": "~/wallpaper.jpg"
        },
        "text": {
            "description": "Target location for the long form text description file, may be None",
            "default": None
        }
    }


    @staticmethod
    def parseParameter(name, value):
        if value and not os.access(value, W_OK):
            return None, "File {} is not writeable!".format(value)

        return value, None


    @staticmethod
    def do(wpObject, parameters):
        try:
            if parameters["image"]:
                shutil.copyfile(wpObject.filename, parameters["image"])

            if parameters["text"]:
                with open(parameters["text"], "w") as file:
                    print(wpObject.caption, file = file)
                    print(wpObject.description, file = file)

        except Exception as exception:
            wpObject.errors[__name__] = exception

        return wpObject
