import shutil

#archive() will archive file, remove the old one, and move it to the destination
#it will
def archive(path, destination, format: str = "zip") -> bool:
    #it should support multiple format, if the format is not in a supported list return false
    pass

#move() will move a file from it's orignial palce
def move(path, destination) -> bool:
    #it should check if the destination file name is there, if it's there it should handle duplication
    pass

#remove() will remove the file
def remove(path) -> bool:
    pass

#rename() will rename a file from
def rename(path, new_name) -> bool:
    #it should handle if the file it's trying to renmae is there
    pass

RULES = {
    "archive": archive,
    "move": move,
    "remove": remove,
    "rename": rename,
}

def run_action (path, rules):
    if rules.get("action") == "rename":
        pass
    elif rules.get("action") == "archive":
        pass
    elif rules.get("action") == "move":
        pass
    elif rules.get("action") == "remove":
        pass

