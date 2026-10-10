# Download Manager CLI Python Script
# Give config + watch folder
import argparse

#this function will scan all the files in the base_dir and will skip the destination files
def scan(base_dir: str, recursive: bool, skip_dir: list[str]) -> list[str]:
    pass

# here the main logic will be
def main():
    p = argparse.ArgumentParser(description="Organize files using a JSON rules file.")
    p.add_argument("--base-dir", required=True, help="folder to scan")
    p.add_argument("--config", required=True, help="path to the rules JSON")
    p.add_argument("--recursive", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.parse_args()


if __name__ == "__main__":
    main()
