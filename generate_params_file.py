import json

if __name__ == "__main__":
    with open("./param_template.json") as params:
        json_string_data = params.read()
        json_data = json.loads(json_string_data)

        for search_param in json_data:
            if type(json_data[search_param]) is dict:
                for subparam in json_data[search_param]:
                    print(json_data[search_param][subparam])
            else:
                print(json_data[search_param])

'''
{
    "location":"chickawawa",
    "distance":
    {
        "radial":0, 
        "walking":0
    }, 
    "price":
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
    }
}
'''