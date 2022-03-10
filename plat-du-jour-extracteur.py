from htmlparser import *
from http.client import HTTPSConnection
from urllib.parse import urlparse


# Number of page to query
NB_PAGE = 1
DATA_FILENAME = "data.txt"


# There is so many errors in Marmiton HTML code ...
parser = HTMLParser(ignore_errors = True, quiet = True)


def request(url):
    parsed = urlparse(url)
    
    conn = HTTPSConnection(parsed.netloc)
    conn.request("GET", parsed.path + ("?" + parsed.query if parsed.query else ""))
    r = conn.getresponse()

    if r.status in [300, 301, 302, 308]:
        loc = r.getheader("Location")
        if loc:
            if loc[0] == '/':
                newurl = parsed.scheme + "://" + parsed.netloc + loc
            else:
                newurl = loc
            return request(newurl)
        else:
            return {'status': r.status, 'reason': r.reason, 'body': None}

    else:
        return {'status': r.status, 'reason': r.reason, 'body': r.read().decode('utf-8')}


file = open(DATA_FILENAME, "w", encoding="utf-8")


for page in range(1, NB_PAGE + 1):
    print("\nRequesting page %i ..." % page)

    url = "https://www.marmiton.org/recettes?type=platprincipal&page=%i" % page
    response = request(url)

    print("Page %i requested" % page)

    if response['body'] is not None and response['status'] == 200:
        err, parsed = parser.parse(response['body'])
        parser.reset()

        if err == HTML_SUCCESS:
            recipes = parsed.findByClass("recipe-card-link")
            print("%i recipes found" % len(recipes))

            i = 1
            for recipe in recipes:
                print("\nQuery recipe %i ..." % i)

                recipe_url = recipe.getAttribute("href")
                recipe_resp = request(recipe_url)

                print("Recipe %i queried" % i)
                i += 1

                if recipe_resp['body'] is not None and recipe_resp['status'] == 200:
                    err, recipe_parsed = parser.parse(recipe_resp['body'])
                    parser.reset()

                    if err == HTML_SUCCESS:
                        data = recipe_parsed.findByClass("RCP__sc-1qnswg8-1") # Class "iDYkZP" work too
                        duration = data[0].getInnerText()
                        difficulty = data[1].getInnerText()
                        price = data[2].getInnerText()
                        file.write(duration + "; " + difficulty + "; " + price + "; " + recipe_url + "\n")

                    else:
                        print("Error when parsing recipe response: %s" % err.toString())

                else:
                    print("Error when requesting \"%s\" and return code is %i %s" % (recipe_url, recipe_resp['status'], recipe_resp['reason']))

        else:
            print("Error when parsing response: %s" % err.toString())

    else:
        print("Error when requesting \"%s\" and return code is %i %s" % (url, response['status'], response['reason']))

file.close()
