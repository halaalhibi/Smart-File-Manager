# Download Manager CLI Python Script
# Give config + watch folder
import sys
import os
import json
import argparse
from pathlib import Path
import matchers
import action
import config



#this will parse to get all dest folder
def resolve_path(path):
    return Path(path).expanduser().resolve()

#this function will scan all the files in the base_dir and will skip the destination files
def scan(base_dir: Path, recursive: bool, skip_dir: str) -> list[str]:
    return ["test"]

# here the main logic will be
def main():
    p = argparse.ArgumentParser(description="Organize files using a JSON rules file.")
    p.add_argument("--base-dir", required=True, help="folder to scan")
    p.add_argument("--config", required=True, help="path to the rules JSON")
    p.add_argument("--recursive", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    #parse args
    config_file = resolve_path(args.config)
    base_dir = resolve_path(args.base_dir)
    recursive = args.recursive
    verbose = args.verbose

    #get and parse json
    ok, json_error = config.validate_json(config_file)
    if not ok:
        sys.exit(json_error)
    json_data = json.load(open(config_file))

    #get all files in base_dir
    for item in json_data['rules']:
        all_files = scan(base_dir, recursive, item)
        # filter
        for file in all_files:
            for when in item['when'].items():
                if matchers.matches(file, when):
                    action.run_action(item['action'], item)
                else:
                    continue




if __name__ == "__main__":
    main()
