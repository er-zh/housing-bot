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

    # get the search queries that you want to use
    queries = []
    with open('./defaults.json') as param_file:
        json_string_data = param_file.read()
        params = json.loads(json_string_data)

        queries = params['queries']
    for i in range(len(queries)):
        queries[i] = queries[i].replace('<location>', params['location'])
        queries[i] = queries[i].replace(' ', delim)

    #regexes
    suffixes = r'(St(reet)?|R(oa)?d|Dr(ive)?|Hwy|Ave(nue)?|Blvd|Way|Pl(ace)?|C(our)?t|Cir(cle)?)\.?'
    street_addr_pattern = re.compile(r'((\d+) (\w+\s?)+ ' + suffixes + r')') # street address
    
    #city_pattern = re.compile(params['location'] + r',? (\w\w) (\d{5})') # city state and zip code

    price_pattern = re.compile(r'(\$(\d{1,3}?),?(\d{1,3},?)*)') # cost of rent

    bed_pattern = re.compile(r'(\d)\s?(Bed(room)?(s)?|br|BR|Br)') # num beds
    bath_pattern = re.compile(r'(\d)\s?((Full )?Bath(room)?(s)?|ba|Ba|BA)') # num baths

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
            price = -1
            bedrooms = -1
            bathrooms = -1

            # get the contents of the page body
            # section tag with class body
            # should contain all the relevant info
            page_body = lsoup.select('section.body')[0]

            page_text = " ".join(page_body.text.split())
            print(page_text)

            matches = street_addr_pattern.findall(page_text)
            address = matches[0][0]
            print(address)
            
            # method for getting the numeric price value is super ratchet
            matches = price_pattern.findall(page_text)
            print(matches)
            for match in matches:
                match_val = ''
                for i in range(1, len(match)):
                    match_val = match_val + match[i]
                match_val = float(match_val)
                if match_val > price:
                    price = match_val
            print(price)
            
            matches = bed_pattern.findall(page_text)
            bedrooms = int(matches[0][0])
            print(bedrooms)
            
            matches = bath_pattern.findall(page_text)
            bathrooms = int(matches[0][0])
            print(bathrooms)
            
            quit(0)

            checked_results.add(res.get('data-pid'))

            