import json

#"action" should equal one of those in the given JSON.
ACTIONS = ["move", "archive", "rename", "remove"]
#"when" should equal one of those in the given JSON or multiple.
FILTER  = ["url", "extension","size_mb", "age_days", "name"]
#"format" should equal one of those in the give JSON.
FORMATS = ["zip", "tar"]
#those are the main key
RULE_KEYS = ["when", "action"]
#those are the required filds
REQUIRED = {
    "move": ["dest"],
    "archive": ["dest"],
    "rename": ["format"],
    "remove": [],
}

# validate JSON, if something in the JSON outside of the desired structure return false.
# look at example.json to understand
def validate_json(json_file) -> bool:
    pass