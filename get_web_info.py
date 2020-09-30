import requests
import bs4
#import selenium

#temp
import json

if __name__ == "__main__":
    # only searches through one site atm
    url = "https://raleigh.craigslist.org/search/hhh?query=<qqq>&availabilityMode=0&sale_date=all+dates"
    swap = "<qqq>"

    # get the search queries that you want to use
    queries = {}
    with open('./defaults.json') as param_file:
        json_string_data = param_file.read()
        params = json.loads(json_string_data)

        queries = list(params['queries'].values())
        for i in range(len(queries)):
            queries[i] = queries[i].replace('<location>', params['location'])

    print(queries)

    for query in queries:
        # retrieve the webpage
        search = url.replace(swap, query)

        res = requests.get(search)
        try:
            res.raise_for_status()
        except Exception as ex:
            print(f'Issue: {ex}')
        
        # use bs4 to parse the retrieved html
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        # for craigslist look through section class=page-container ->
        # form id=searchform -> div class=content -> ul class=rows ->
        # li class=result-row -> a href=*the url we want*
        print(type(soup))
        search_results = soup.select('body > section > form > div > ul > li > a')

        print(type(search_results), len(search_results), str(search_results[0]))