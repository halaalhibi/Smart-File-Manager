import shutil
from pathlib import Path
from datetime import datetime


#archive() will archive directory containing files, remove the old one, and move it to the destination
#it will
def archive_action(source, destination, format: str = "zip") -> bool:
    #it should support multiple format, if the format is not in a supported list return false
    now = datetime.now()
    archive_name = now.strftime("%d-%b-%Y")
    try:
        archive_path = shutil.make_archive(archive_name, format, source)
        destination_path = Path(destination)
        if not destination_path.exists():
            destination_path.mkdir()
        else:
            if not destination_path.is_dir():
                destination_path.mkdir()
        shutil.move(archive_path, destination / f"{archive_name}.{format}")
        return True
    except:
        return False

#move() will move a file from it's orignial palce
def move_action(path, destination) -> bool:
    #it should check if the destination file name is there, if it's there it should handle duplication
    try:
        shutil.move(path, destination)
        return True
    except:
        return False

#remove() will remove the file
def remove_action(path) -> bool:
    try:
        shutil.rmtree(path)
        return True
    except:
        return False

#rename() will rename a file from
def rename_action(path, new_name) -> bool:
    #it should handle if the file it's trying to renmae is there
    try:
        Path(path).rename(new_name)
        return True
    except:
        return False


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

