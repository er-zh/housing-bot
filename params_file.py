import json
import os

# class defined to manage parameter data
# holds on to search parameters and writing new json files
# when a search appears that matches the search parameters

class Param():
    def __init__(self, param_file='./param_template.json'):
        search_params = {}
        with open(param_file) as pf:
            json_string = pf.read()
            search_params = json.loads(json_string)

        # the location being searched
        self.location = search_params['location']

        # location that distances are measured with respect to
        self.loc_wrt = search_params['distance']['wrt']

        # the direct distance between the potential housing and 
        self.graph_dist = search_params['distance']['gr_dist']

        # walking distance measured in minutes
        self.walking = search_params['distance']['walking']

        # the actual cost of renting per month
        self.raw_price = search_params['pricing'][0]

        # the cost per roommate
        self.roommate_price = search_params['pricing'][1]
        self.n_roommates = search_params['pricing'][2]

        # websites to scrape and their respective search urls
        self.websites = search_params['websites']

        # the search strings used on each site
        self.queries = []
        for query in search_params['queries']:
            self.queries.append(query.replace('<location>', self.location))
        
        # size of the property by beds and baths
        self.beds = search_params['sizing'][0]
        self.baths = search_params['sizing'][1]
    
    def write_search_params(self, param_file='./new_params.json'):
        json_data = {}
        json_data['location'] = self.location
        json_data['distance'] = {}
        json_data['distance']['wrt'] = self.loc_wrt
        json_data['distance']['gr_dist'] = self.graph_dist
        json_data['distance']['walking'] = self.walking
        json_data['pricing'] = [self.raw_price, self.roommate_price, self.n_roommates]
        json_data['websites'] = self.websites
        json_data['queries'] = self.queries
        json_data['sizing'] = [self.beds, self.baths]

        if os.path.exists(param_file):
            print('error, file already exists')
            #return

        with open(param_file, 'w') as pout:
            json.dump(json_data, pout)

if __name__ == "__main__":
    s = Param()

'''
{
    "location":"chickawawa",
    "distance":
    {
        "wrt":"some address",
        "gr_dist":0, 
        "walking":0
    }, 
    "pricing":[1000, 500, 2],
    "websites":
    {
        "craigslist":false,
        "fb":false,
        "zillow":false
    },
    "queries":[
        "rental properties in <location>", 
        "apartments <location>", 
        "<location> rental properties"
    ],    
    "sizing":[1, 1]
}
'''

# should check for pet availability at some point in the future