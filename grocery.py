from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import fractions
from decimal import Decimal

def s_get(url):
    # Attempts to get content from url by making an HTTP GET request.
    # If the content-type of response is HTML/XML, return text content
    # Otherwise return None.

    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.text
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

def get_ingredients(url):
    #Downloads the recipe page and returns a list of strings, one per ingredient
    response = s_get(url)

    if response is not None:
        soup = BeautifulSoup(response, 'html.parser')
        data = soup.find('script', type='application/ld+json');
        oJson = json.loads(data.contents[0])
        #print(oJson['@graph'][7]["recipeIngredient"])
        ingr = oJson['@graph'][7]["recipeIngredient"]
        return ingr

def get_grocery_list():
    measurements = {'Tbsp', 'Tsp', '{}oz','cup', 'cups', 'tsp', 'tbsp'}
    grocery_list = {}
    print("Enter recipe URLs. Press ENTER when done.")
    inputs = []
    while True:
        inp = input()
        if inp == "":
            break
        newList = get_ingredients(inp)
        for ingr in newList:
            ingrtemp = set(ingr.split())

            #Check if there is a measurement in the ingredient name
            measurementType = ""
            if not ingr[0].isdigit():
                ingrNameAct = ingr.rsplit(' ', 1)[0].strip()
                measurementAct = ""
            else:
                if ingrtemp & measurements:
                    measurementType = " ".join(ingrtemp.intersection(measurements)).strip()
                    ingrNameAct = ingr.split(measurementType)[1].rsplit(' ', 1)[0].strip()
                    measurementAct = ingr.split(measurementType)[0].strip() + " " + measurementType
                else:
                    ingrNameAct = ingr.split(" ", 1)[1].rsplit(' ', 1)[0].strip()
                    measurementAct = ingr.split(" ", 1)[0].strip()

            #Check if the ingredient is already in grocery_list
            if ingrNameAct in grocery_list:
                #If their measurement types match, add their measurements together
                if (len(measurementType) > 0 and set(grocery_list[ingrNameAct]) & set(measurementType)):
                    existingMeasurementAmt = convert_to_float(grocery_list[ingrNameAct].split(measurementType)[0].strip())
                    thisMeasurementAmt = convert_to_float(ingr.split(measurementType)[0].strip())
                    newMeasurementAmt = existingMeasurementAmt + thisMeasurementAmt
                    if not newMeasurementAmt % 1 == 0:
                        newMeasurementAmt = fractions.Fraction(Decimal(newMeasurementAmt))
                    grocery_list[ingrNameAct] = str(newMeasurementAmt) + " " + measurementType

                # Measurement types do not match but there is still a measurement type
                elif len(measurementType) > 0:
                    grocery_list[ingrNameAct] = grocery_list[ingrNameAct] + " and " + measurementAct

                #No measurement type
                elif not measurementAct == "":
                    existingMeasurementAmt = convert_to_float(grocery_list[ingrNameAct])
                    thisMeasurementAmt = convert_to_float(measurementAct)
                    newMeasurementAmt = existingMeasurementAmt + thisMeasurementAmt
                    if not newMeasurementAmt % 1 == 0:
                        newMeasurementAmt = fractions.Fraction(Decimal(newMeasurementAmt))
                    grocery_list[ingrNameAct] = str(newMeasurementAmt)

                else:
                    grocery_list[ingrNameAct] = ""

            #Ingredient is not in grocery list
            else:
                grocery_list[ingrNameAct] = measurementAct

    for ingr in grocery_list:
        print (grocery_list[ingr] + " " + ingr)

def main():
    get_grocery_list()
 

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac

if __name__ == "__main__":
    main()
