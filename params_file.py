import json
import os

# class defined to manage parameter data
# holds on to search parameters and writing new json files
# when a search appears that matches the search parameters

class Search():
    def __init__(self, param_file='./param_template.json'):
        # the location being searched
        self.location = ''
        self.dist_wrt = ''
        self.graph_dist = 0
        self.walking = 0
        self.raw_price = 0
        self.roommate_price = 0
        self.websites = {}
        self.queries = []
        self.beds = 0
        self.baths = 0.0
    
        search_params = {}
        with open(param_file) as pf:
            json_string = pf.read()
            search_params = json.loads(json_string)

        self.location = search_params['location']
        self.dist_wrt = search_params['distance']['wrt']
        self.graph_dist = search_params['distance']['gr_dist']
        self.walking = search_params['distance']['walking']
        self.raw_price = search_params['pricing'][0]
        self.roommate_price = search_params['pricing'][1]
        self.websites = search_params['websites']

        for query in search_params['queries']:
            self.queries.append(query.replace('<location>', self.location))
        
        self.beds = search_params['sizing'][0]
        self.baths = search_params['sizing'][1]
    
    def write_search_params(self, param_file='./new_params.json'):
        json_data = {}
        json_data['location'] = self.location
        json_data['distance'] = {}
        json_data['distance']['wrt'] = self.dist_wrt
        json_data['distance']['gr_dist'] = self.graph_dist
        json_data['distance']['walking'] = self.walking
        json_data['pricing'] = [self.raw_price, self.roommate_price]
        json_data['websites'] = self.websites
        json_data['queries'] = self.queries
        json_data['sizing'] = [self.beds, self.baths]

        if os.path.exists(param_file):
            print('error, file already exists')
            #return

        with open(param_file, 'w') as pout:
            json.dump(json_data, pout)

if __name__ == "__main__":
    s = Search()

'''
{
    "location":"chickawawa",
    "distance":
    {
        "wrt":"some address",
        "gr_dist":0, 
        "walking":0
    }, 
    "pricing":
    {
        "raw": 0,
        "per_roommate":0
    },
    "websites":
    {
        "craigslist":false,
        "fb":false,
        "zillow":false
    },
    "queries":
    {
        "1":"rental properties in <location>",
        "2":"apartments <location>",
        "3":"<location> rental properties"
    },
    "sizing":
    {
        "beds":2,
        "baths":2
    }
}
'''