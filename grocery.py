from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def s_get(url):
    # Attempts to get content from url by making an HTTP GET request.
    # If the content-type of response is HTML/XML, return text content
    # Otherwise return None.

    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.formal(url,str(e)))
        return None

def is_good_response(resp):
    #Returns True if response seems to be HTML, False, Otherwise
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    #Prints error to console
    print(e)

def get_ingredients():
    #Downloads the recipe page and returns a list of strings, one per ingredient
    url = 'https://www.budgetbytes.com/greek-turkey-rice-skillet/'
    response = s_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        site_json = json.loads(html.text)
        ingr = set()
        for item in site_json['recipeIngredient']:
            print(item)

get_ingredients()
