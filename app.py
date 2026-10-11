# Download Manager CLI Python Script
# Give config + watch folder
import argparse
import matchers
import action
import config
from pathlib import Path
import sys
import os


#this function will scan all the files in the base_dir and will skip the destination files
def scan(base_dir: str, recursive: bool, skip_dir: str) -> list[str]:
    pass

# here the main logic will be
def main():
    p = argparse.ArgumentParser(description="Organize files using a JSON rules file.")
    p.add_argument("--base-dir", required=True, help="folder to scan")
    p.add_argument("--config", required=True, help="path to the rules JSON")
    p.add_argument("--recursive", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    config_file = Path(args.config)
    ok, json_error = config.validate_json(config_file)
    if not ok:
        sys.exit(json_error)




if __name__ == "__main__":
    main()
