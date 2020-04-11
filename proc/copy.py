import os
import shutil

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
