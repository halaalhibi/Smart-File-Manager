import json

#"action" should equal one of those in the given JSON.
actions = ["move", "archive", "rename", "remove"]
#"when" should equal one of those in the given JSON or multiple.
filter  = ["url", "extension","size_mb", "age_days", "name"]
#"format" should equal one of those in the give JSON.
formats = ["zip", "tar"]
#those are the required fields
required = ["when", "action"]

# validate JSON, if something in the JSON outside of the desired structure return false.
# look at example.json to understand
def validate_json(json_file) -> bool:
    pass

# those functions will take where to search and the metric to the filter
# it will return a list to the valid path


def extension_filter(source_path, extension) -> list:
    pass

def url_filter(source_path, url) -> list:
    pass

def size_filter(source_path, size: int) -> list:
    pass

def age_days_filter(source_path, age) -> list:
    pass

def name_filter(source_path, name) -> list:
    pass
