from PIL import Image, ImageFont, ImageDraw 

DESCRIPTION = "Write a wallpaper's caption on the image"

PARAMETERS = {
    "font": {
        "description": "Set font to use for the caption",
        "default": "DejaVuSans-BoldOblique.ttf"
    },
    "size": {
        "description": "Set font size to use for the caption",
        "default": 24
    },
    "fgcol": {
        "description": "Set font colour to use for the caption",
        "default": (255, 255, 255)
    },
    "bgcol": {
        "description": "Set caption box colour, may be None to skip box generation",
        "default": (0, 0, 0)
    },
    "position": {
        "description": "Set caption box position on the image",
        "default": (-10, -10)
    },
    "padding": {
        "description": "Set space between text and caption box",
        "default": 5
    }
}


def textbox(image, text, font, size, fgcol, bgcol, position, padding):
    # TODO: transparency, rounded corners
    font = ImageFont.truetype(font, size)
    draw = ImageDraw.Draw(image)
    
    textsize = draw.textsize(text, font)
    x, y = position
    if x < 0:
        x += image.size[0] - textsize[0]
    if y < 0:
        y += image.size[1] - textsize[1]
    box = (x - padding, y - padding, x + textsize[0] + padding, y + textsize[1] + padding)

    draw.rectangle(box, outline = fgcol, fill = bgcol)
    draw.text((x, y), text, fgcol, font = font)


def parseParameter(name, value):
    return value, None


def do(wpObject, parameters):
    try:
        image = Image.open(wpObject.filename)
        textbox(image, wpObject.caption, parameters["font"],              \
            parameters["size"], parameters["fgcol"], parameters["bgcol"], \
            parameters["position"], parameters["padding"])
        image.save(wpObject.filename, "jpeg")
    except Exception as exception:
        wpObject.errors[__name__] = exception
    
    return wpObject
