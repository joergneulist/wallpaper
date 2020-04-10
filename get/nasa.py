import datetime
import json

from wpplugin import wpPlugin

class nasa(wpPlugin):

    DESCRIPTION = "Get a wallpaper from the NASA Astronomy Picture of the Day page"

    PARAMETERS = {
        "date": {
            "description": "NASA allows retrieving images according to a time-stamp in format yyyy-mm-dd",
            "default": str(datetime.date.today())
        }
    }


    @staticmethod
    def parseParameter(name, value):
        try:
            date = str(datetime.datetime.strptime(value, "%Y-%m-%d").date())
        except Exception as exception:
            return None, str(exception)

        return date, None


    @staticmethod
    def do(wpObject, parameters):
        base_url = "https://api.nasa.gov/planetary/apod?api_key=uMUs7SQJVxUBaOm3y5wci3BT97X1mylJ0hJdEb0h"
        url = base_url + "&date={}".format(parameters["date"])
        
        try:
            nasa_json = wpPlugin.getFromWeb(url)
            nasa_data = json.loads(nasa_json)

            if nasa_data["media_type"] == "image":
                wpObject.url = nasa_data["hdurl"]
                wpObject.caption = nasa_data["title"]
                wpObject.description = nasa_data["explanation"]
        
        except Exception as exception:
            wpObject.errors[__name__] = exception

        return wpObject
