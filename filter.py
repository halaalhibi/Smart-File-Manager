# those functions will take a path and apply the metric to the file
# it will return a true ---> match, or false ---> doesn't match


def extension_filter(path, extension) -> bool:
    pass

def get_origin_url(path: str) -> str:
    pass

def url_filter(path, url) -> bool:
    pass

def size_filter(path, size: int) -> bool:
    pass

def age_days_filter(path, age) -> bool:
    pass

def name_filter(path, name) -> bool:
    pass

MATCHERS = {
    "extension": extension_filter,
    "url": url_filter,
    "name": name_filter,
    "size_mb": size_filter,
    "age_days": age_days_filter,
}

# this function will run the filter functions on the path.
def matches(path, when):
    for key, value in when.items():
        # find the right function
        check = MATCHERS[key]
        # run it on the file
        if not check(path, value):
            return False
    return True

# this function will be used to pass the whole rule.
def first_matching_rule(path, rules):
    for rule in rules:
        if matches(path, rule["when"]):
            return rule
    return None

