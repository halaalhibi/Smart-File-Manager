# those functions will take a path and apply the metric to the file
# it will return a true ---> match, or false ---> doesn't match
import platform

# basic function just checking for extensions.
def extension_filter(path, extensions:list) -> bool:
    for extension in extensions:
        if path.endswith(extension):
            return True
    return False

# this function will get the origin url supporting Windows, Linux, MacOS
def get_origin_url(path: str) -> str:
    os_type = platform.system()
    # tested it works
    if os_type == "Windows":
        try:
            with open(paht + ":Zone.Identifier") as file:
                url = file.read()
            return (url.split()[2].split("=")[1].split("\x00")[0])
        except FileNotFoundError:
            return None
    #only theoritical
    elif os_type == "Darwin":
        out = subprocess.run(
            ["xattr", "-px", "com.apple.metadata:kMDItemWhereFroms", path],
            capture_output=True, text=True, check=True,
        ).stdout
    #linux
    else:
        return os.getxattr(path,"user.xdg.origin.url")


# check if that file contains the URL
def url_filter(path, url) -> bool:
    file_url = get_origin_url(path)
    if file_url.contains(url):
        return True
    else:
        return False


#TODO: Make this
def size_filter(path, size: int) -> bool:
    pass

#TODO: Maket this
def age_days_filter(path, age) -> bool:
    pass

#TODO: Make this
def name_filter(path, name) -> bool:
    pass

# a mapper for functions with the json.
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

