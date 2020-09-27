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
