import json

#"action" should equal one of those in the given JSON.
ACTIONS = ["move", "archive", "rename", "remove"]
#"when" should equal one of those in the given JSON or multiple.
FILTER  = ["url", "extension","size_mb", "age_days", "name"]
#"format" should equal one of those in the give JSON.
FORMATS = ["zip", "tar"]
#those are the main key
REQUIRED_KEYS = ["when", "action"]
#those are the required filds

# validate JSON, if something in the JSON outside of the desired structure return false.
# look at example.json to understand
# TODO: Improve this to make it update an error list, and raise it back to know where the error happened
def validate_json(json_path) -> bool:
    try:
        # try to retrieve data from json file
        with open(json_path) as json_data:
            data = json.load(json_data)
    except:
        return False
    # the dictionary should always start with 'rules'
    if 'rules' not in data:
        return False
    try:
        for row in data['rules']:
            for required in REQUIRED_KEYS:
                # "when" and "action" should always be in the json
                if required not in row:
                    return False
            for keys,values in row.items():
                # validate when key is "when"
                if keys == "when":
                    #check if it's empty
                    if not values:
                        return False
                    for value, subvalues in values.items():
                        #check that it's one of the valid when filters
                        if value not in FILTER:
                            return False
                        # if the filter is "size_mb" or "age_days" it should contain less than or more than
                        if value == "size_mb" or value == "age_days":
                            if not ("greater_than" in subvalues or "less_than" in subvalues):
                                return False
                # validate when key is "action"
                elif keys == "action":
                    #check if it's empty
                    if not values:
                        return False
                    #check that it's a valid action type
                    if values not in ACTIONS:
                        return False
                    # if the action is "move" or "archive" a dist row shoud have "dist" key
                    if values == "move" or values == "archive":
                        if row.get("dest") is None:
                            return False
                    # if the action is rename a "format" key should be there
                    elif values == "rename":
                        if row.get("format") is None:
                            return False
                elif keys == "format":
                    #check if it's empty
                    if not values:
                        return False
                    # if the action is 'archive' the format should be one of the accepted formats
                    if row['action'] == 'archive':
                        if values not in FORMATS:
                            return False
    #for any exception happned trying to parse the json return False
    except:
        return False

    #defulat case
    return True