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
    regexes = []
    # craigslist title regex
    # gets housing size data, group1 = rent price, group2 = num bedrooms, group3 = square footage
    regexes.append(r'\$(\d{1,3}(,?))+ / (\d+)br - (\d+)ft2')
    # general params checking
    #regexes.append(r'(\d+ (\w+\s?)+)') # street address
    #regexes.append(r'((\w+\s?)+),? (\w\w) (\d{5})') # city state and zip code
    regexes.append(r'(\$(\d{1,3}?(,?))+)') # cost of rent
    #regexes.append(r'(\d) Bed(room)?(s)?') # num beds
    #regexes.append(r'(\d) ((Full )?Bath(room)?(s)?)') # num baths
    
    # compile parsers
    patterns = []
    for regex in regexes:
        patterns.append(re.compile(regex))

    n_regexes = len(patterns)

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
        print(query)
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

            # stats that are being searched for
            address = ''
            price = -1
            bedrooms = -1
            bathrooms = -1

            # get the contents of the page body
            # section tag with class body
            # should contain all the relevant info
            page_body = lsoup.select('section.body')[0]

            page_text = " ".join(page_body.text.split())

            for pattern in patterns:
                match = pattern.findall(page_text)

                if match is None:
                    print('oh no')
                    continue
                
                for res in match:
                    print(res)
            
            '''
            # retrieve property information contained within the title
            price = title.find('span', attrs={'class':'price'})
            if price is not None:
                #price = price.get_text()
                price = price.text[1:] if price.text[0] == '$' else price

            housing = title.find('span', attrs={'class':'housing'})
            if housing is not None:
                #housing = housing.get_text()
                size_stats = patterns[0].search(housing.text) # should do re.compile then match
                if size_stats is None:
                    print(housing)
                else:
                    bedrooms = size_stats.group(1)
                    sq_ft = size_stats.group(2) #don't really need this stat
            print(price, bedrooms, sq_ft)

            brs = body.find_all('br')
            for br in brs:
                for i in range(1, n_regexes):
                    br.get_text()
                    '''
            quit(0)

            checked_results.add(res.get('data-pid'))