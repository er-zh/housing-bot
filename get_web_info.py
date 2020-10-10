import requests
import bs4
#import selenium
import re
import multiprocessing
import time

#temp
import json


def get_address(text, queue):
    # too expensive to do a findall
    # will occassionally fail anyways
    addr = street_addr_pattern.search(text)
    if addr is not None:
        queue.put(addr.group(0))


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
    suffixes = r'(St(reet)?|R(oa)?d|Dr(ive)?|Ave(nue)?|Way|Pl(ace)?|C(our)?t|Cir(cle)?)\.?'
    street_addr_pattern = re.compile(r'((\d+-)?(\d+) (\w+\s?)+ ' + suffixes + r')') # street address
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
            print(f'Err: failed to request {lurl}')
            print(err)
            continue
        
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
        for k, res in enumerate(search_results):
            print(k)
            if res.get('data-pid') in checked_results:
                continue
            
            lurl = res.a.get('href')
            listing = requests.get(lurl)
            try:
                listing.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(f'Err: failed to request {lurl}')
                print(err)
                continue
            
            lsoup = bs4.BeautifulSoup(listing.text, 'html.parser')

            # stats that are being searched for
            # will be unchanged if the regex searches return none
            address = ''
            price = -1
            bedrooms = -1
            bathrooms = -1

            # get the contents of the page body
            # section tag with class body
            # should contain all the relevant info
            page_body = lsoup.select('section.body')[0]

            page_text = " ".join(page_body.text.split())

            # method for getting the numeric price value is ratchet
            matches = price_pattern.findall(page_text)
            for match in matches:
                match_val = ''
                for i in range(1, len(match)):
                    match_val = match_val + match[i]
                match_val = float(match_val)
                if match_val > price:
                    price = match_val

            # get the address via super ratchet method
            # sometimes a listing just doesn't contain an address that is 
            # findable by the street_addr regex, so defn a function that 
            # is responsible for looking for the address and if the search takes
            # too long time it out
            try:
                q = multiprocessing.Queue()

                p = multiprocessing.Process(target=get_address, args=(page_text, q))
                p.start()

                p.join(5)

                if p.is_alive():
                    p.kill()
                    p.join()
                else:
                    address = q.get()
            except multiprocessing.ProcessError as bigoof:
                print(f'{bigoof}')
                quit()
            print(address)

            matches = bed_pattern.findall(page_text)
            if matches is not None:
                bedrooms = int(matches[0][0])
            
            matches = bath_pattern.findall(page_text)
            if matches is not None:
                bathrooms = int(matches[0][0])

            checked_results.add(res.get('data-pid'))

            