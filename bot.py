import requests
import bs4
import json
#import seleniums

if __name__ == "__main__":
    param_file_loc = "./defaults.json"
    
    params = {}

    with open(param_file_loc) as param_file:
        json_string_data = param_file.read()
        params = json.loads(json_string_data)

    # create the correct search queries
    searches = []
    for key in params['queries']:
        searches.append(params['queries'][key].replace('<location>', params['location']))

    for site in params['websites']:
        for search in params['queries']:
            
    