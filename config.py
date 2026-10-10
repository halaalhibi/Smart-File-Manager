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
def validate_json(json_path) -> bool:
    try:
        with open(json_path) as json_data:
            data = json.load(json_data)
    except:
        return False
    if 'rules' not in data:
        return False
    try:
        for row in data['rules']:
            for required in REQUIRED_KEYS:
                if required not in row:
                    return False
            for keys,values in row.items():
                if keys == "when":
                    if not values:
                        return False
                    for value, subvalues in values.items():
                        if value not in FILTER:
                            return False
                        if value == "size_mb":
                            if not ("greater_than" in subvalues or "less_than" in subvalues):
                                return False
                        if value == "age_days":
                            if not ("greater_than" in subvalues or "less_than" in subvalues):
                                return False
                elif keys == "action":
                    if values not in ACTIONS:
                        return False
                    if values == "move" or values == "archive":
                        if row.get("dest") is None:
                            return False
                    elif values == "rename":
                        if row.get("format") is None:
                            return False
                elif keys == "format":
                    if row['action'] == 'archive':
                        if values not in FORMATS:
                            return False
    except:
        return False

    #defulat case
    return True