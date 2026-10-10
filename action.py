import shutil
import pathlib

#archive() will archive file, remove the old one, and move it to the destination
#it will
def archive_action(path, destination, format: str = "zip") -> bool:
    #it should support multiple format, if the format is not in a supported list return false
    pass

#move() will move a file from it's orignial palce
def move_action(path, destination) -> bool:
    #it should check if the destination file name is there, if it's there it should handle duplication
    pass

#remove() will remove the file
def remove_action(path) -> bool:
    pass

#rename() will rename a file from
def rename_action(path, new_name) -> bool:
    #it should handle if the file it's trying to renmae is there
    pass


def run_action (path, rules):
    destination = ""
    action = rule.get("action")
    if action in ["move", "archive"]:
        if rule.get("destination") is None:
            return False
        else:
            destination = Path(rule.get("destination"))
    if action == "rename":
        if rule.get("format") is None:
            return False
        else:
            return rename_action(path, rules.get("format"))
    elif action == "archive":
        return archive_action(path, destination)
    elif action == "move":
        return move_action(path, destination)
    elif action == "remove":
        return remove_action(path)
    else:
        return False

