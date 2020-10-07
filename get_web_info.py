import requests
import bs4
#import selenium
import re

#temp
import json

if __name__ == "__main__":
    # only searches through one site atm
    url = "https://raleigh.craigslist.org/search/hhh?query=<qqq>&availabilityMode=0&sale_date=all+dates"
    swap = "<qqq>"
    delim = "+"

    #regexes
    # gets housing size data, group 1 = num bedrooms, group 2 = square footage
    craigslist_title_housing_regex = r'^.*(\d+br).*?(\d+ft2).*$'

    # get the search queries that you want to use
    queries = []
    with open('./defaults.json') as param_file:
        json_string_data = param_file.read()
        params = json.loads(json_string_data)

        queries = params['queries']
    for i in range(len(queries)):
        queries[i] = queries[i].replace('<location>', params['location'])
        queries[i] = queries[i].replace(' ', delim)

    for query in queries:
        # retrieve the webpage
        search = url.replace(swap, query)

        res = requests.get(search)
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # TODO: implement actual exception handling
            print(f'Issue: {err}')
        
        # use bs4 to parse the retrieved html
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        # for craigslist look through section class=page-container ->
        # form id=searchform -> div class=content -> ul class=rows -> li class=result-row
        search_results = soup.select('body > section > form > div > ul > li')

        # inside of the li tag is:
        # an a tag href=*the url we want*
        # data-pid values, will let us easily check for duplicates
        # data-pid method might only be valid for craigslist

        # avoid parsing duplicate listings by tracking listings already parsed
        checked_results = set() # only need to test for membership

        # want to iterate through the search results and get the urls for each listing
        for res in search_results:
            if res.get('data-pid') in checked_results:
                continue
            
            lurl = res.a.get('href')
            listing = requests.get(lurl)
            try:
                listing.raise_for_status()
            except requests.exceptions.HTTPError as err:
                #TODO: more exception handling
                print(f'Issue: {err}')
            
            lsoup = bs4.BeautifulSoup(listing.text, 'html.parser')

            # get the contents of h1 with class=postingtitle
            title = lsoup.select('h1.postingtitle')[0]
            # get the contents of section with id=postingbody
            body = lsoup.select('section#postingbody')[0]
            
            # retrieve property information
            price = title.find('span', attrs={'class':'price'}).get_text()
            price = price[1:] if price[0] == '$' else price

            housing = title.find('span', attrs={'class':'housing'}).get_text()
            size_stats = re.search(craigslist_title_housing_regex, housing)
            bedrooms = size_stats.group(1)
            sq_ft = size_stats.group(2)
            print(price, bedrooms, sq_ft)
            quit(0)

            checked_results.add(res.get('data-pid'))