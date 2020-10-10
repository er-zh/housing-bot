import requests
import bs4
#import selenium
import re
# need this to timeout regexes that take forever
# means that this is incompatible with non-UNIX envs
import signal
#temp
import json

def handler(signum, frame):
    print("regex taking too long")
    raise RuntimeError("killing regex, and skipping to next listing")

if __name__ == "__main__":
    # only searches through one site atm
    url = "https://raleigh.craigslist.org/search/hhh?query=<qqq>&availabilityMode=0&sale_date=all+dates"
    swap = "<qqq>"
    delim = "+"

    #regexes
    suffixes = r'(St(reet)?|R(oa)?d|Dr(ive)?|Ave(nue)?|Way|Pl(ace)?|C(our)?t|Cir(cle)?)'
    street_addr_pattern = re.compile(r'((\d+-)?(\d+) (\w+\s?){1,3} ' + suffixes + r')') # street address
    price_pattern = re.compile(r'(\$(\d{1,3}?),?(\d{1,3},?)*)') # cost of rent
    bed_pattern = re.compile(r'(\d)\s?(Bed(room)?(s)?|br|BR|Br)') # num beds
    bath_pattern = re.compile(r'(\d)\s?((Full )?Bath(room)?(s)?|ba|Ba|BA)') # num baths

    # timeout function to stop slow regexes
    signal.signal(signal.SIGALRM, handler)
    
    # avoid parsing duplicate listings by tracking listings already parsed
    checked_results = set() # only need to test for membership

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
            print(f'Err: failed to request {lurl}')
            print(err)
            continue
        
        # use bs4 to parse the retrieved html
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        # for craigslist look through section class=page-container ->
        # form id=searchform -> div class=content -> ul class=rows -> 
        # li class=result-row -> <a>
        # inside of the a tag is:
        # href=*the url we want*
        search_results = soup.select('body > section > form > div > ul > li > a')

        # want to iterate through the search results and get the urls for each listing
        for k, res in enumerate(search_results):
            print(k)
            
            lurl = res.get('href')
            listing = requests.get(lurl)
            try:
                listing.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(f'Err: failed to request {lurl}')
                print(err)
                continue
            
            lsoup = bs4.BeautifulSoup(listing.text, 'html.parser')

            # get the contents of the page body
            # section tag with class body
            # should contain all the relevant info
            page_body = lsoup.select('section.body')[0]

            page_text = " ".join(page_body.text.split())

            # stats that are being searched for
            # will be unchanged if the regex searches return none
            address = ''
            price = -1
            bedrooms = -1
            bathrooms = -1

            signal.alarm(10)
            # sometimes a listing just doesn't contain an address that is 
            # findable by the street_addr regex, so defn a function that 
            # is responsible for looking for the address and if the search takes
            # too long time it out
            try:
                addr = street_addr_pattern.search(page_text)
            except RuntimeError as ex:
                addr = None
            signal.alarm(0)

            if addr is not None:
                address = addr.group(0)
            
            if address in checked_results:
                continue

            print(address)

            # method for getting the numeric price value is ratchet
            matches = price_pattern.findall(page_text)
            for match in matches:
                match_val = ''
                for i in range(1, len(match)):
                    match_val = match_val + match[i]
                try:
                    match_val = float(match_val)
                except ValueError as ver:
                    print(ver)
                    price = -1
                    break
                if match_val > price:
                    price = match_val

            matches = bed_pattern.findall(page_text)
            if len(matches) != 0:
                bedrooms = int(matches[0][0])
            
            matches = bath_pattern.findall(page_text)
            if len(matches) != 0:
                bathrooms = int(matches[0][0])

            checked_results.add(address)

