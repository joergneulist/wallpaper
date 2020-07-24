from helpers import getHtml, getJson

DESCRIPTION = 'Get a wallpaper from the ESA Image page'

PARAMETERS = {}


def do(wpObject, parameters):
    base_url = 'https://www.esa.int'

    try:
        html = getHtml(base_url + '/ESA_Multimedia/Images')        
        html = getHtml(base_url + html.find('a', class_ = 'cta')['href'])
        wpObject.url = html.find('meta', {'property': 'og:image'})['content']
        wpObject.caption = html.find('meta', {'property': 'og:title'})['content']
        wpObject.description = html.find('div', class_ = 'modal__tab-description').find('p').string

    except Exception as exception:
        wpObject.errors[__name__] = exception

    return wpObject
