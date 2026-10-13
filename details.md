# Smart File Manager — In-Depth Codebase Reference (`details.md`)

This document provides a comprehensive, function-by-function and line-by-line explanation of every component across the entire **Smart File Manager** codebase.

---

# Table of Contents
1. [app.py — CLI Entrypoint & File Discovery](#1-apppy--cli-entrypoint--file-discovery)
2. [config.py — Configuration Schema & Validation](#2-configpy--configuration-schema--validation)
3. [matchers.py — Rule Matching & Filter Engine](#3-matcherspy--rule-matching--filter-engine)
4. [action.py — Action Execution Engine](#4-actionpy--action-execution-engine)
5. [example.json — Configuration Rules Format](#5-examplejson--configuration-rules-format)

---

# 1. `app.py` — CLI Entrypoint & File Discovery

[`app.py`](file:///home/lotekk/Coding/Python/Download-Manager/app.py) is the central coordinator of the application. It parses command-line arguments, discovers candidate files on disk, and passes each file through the matching and execution pipeline.

---

### `resolve_path(path)`
```python
def resolve_path(path):
    if path is None:
        return path
    return Path(path).expanduser().resolve()
```
* **Purpose:** Sanitizes and converts any string or Path into an absolute filesystem path.
* **Parameters:**
  * `path` (`str | Path | None`): The raw input path.
* **Returns:** An absolute, resolved `Path` object, or `None` if the input was `None`.
* **How It Works:**
  1. `if path is None:`: Guards against `NoneType` input.
  2. `.expanduser()`: Expands the tilde `~` shortcut into the user's home directory (e.g., `~/Downloads` becomes `/home/user/Downloads`).
  3. `.resolve()`: Resolves relative paths (e.g. `.` or `..`) and symlinks into an absolute canonical path.

---

### `scan(base_dir: Path, recursive: bool, skip_dir) -> list[str]`
```python
def scan(base_dir: Path, recursive: bool, skip_dir) -> list[str]:
    files = []
    base = Path(base_dir).resolve()
    skip = Path(skip_dir).resolve() if skip_dir else None
    if not base.is_dir():
        return files
    if recursive:
        paths = base.rglob("*")
    else:
        paths = base.iterdir()
    for path in paths:
        if path.is_file():
            if skip and (path.resolve() == skip or skip in path.resolve().parents):
                continue
            files.append(str(path))
    return files
```
* **Purpose:** Traverses the target folder and collects paths of regular files to be processed.
* **Parameters:**
  * `base_dir` (`Path`): The directory to search for files.
  * `recursive` (`bool`): If `True`, searches subdirectories; if `False`, only inspects the top level.
  * `skip_dir` (`Path | str | None`): An optional directory path to exclude from the search (e.g. to avoid scanning destination folders).
* **Returns:** `list[str]` of absolute file path strings.
* **How It Works:**
  1. `base = Path(base_dir).resolve()`: Ensures the search base is an absolute path.
  2. `if not base.is_dir(): return files`: Safety check. If the directory does not exist or is a file, returns an empty list immediately.
  3. `base.rglob("*")` vs `base.iterdir()`:
     * `rglob("*")`: Recursive search that visits all subfolders.
     * `iterdir()`: Shallow search that only yields items directly inside `base_dir`.
  4. `if path.is_file():`: Ignores subdirectories (we only move/archive files).
  5. `if skip and (path.resolve() == skip or skip in path.resolve().parents):`: Skips any file located inside the `skip_dir` folder.
  6. `files.append(str(path))`: Adds the file path to the result list.

---

### `main()`
```python
def main():
    p = argparse.ArgumentParser(description="Organize files using a JSON rules file.")
    p.add_argument("--base-dir", required=True, help="folder to scan")
    p.add_argument("--config", required=True, help="path to the rules JSON")
    p.add_argument("--recursive", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    # parse args
    config_file = resolve_path(args.config)
    base_dir = resolve_path(args.base_dir)
    recursive = args.recursive
    dry_run = args.dry_run

    # get and parse json
    ok, json_error = config.validate_json(config_file)
    if not ok:
        sys.exit(json_error)

    with open(config_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    all_files = scan(base_dir, recursive, skip_dir=None)
    for file in all_files:
        rule = matchers.first_matching_rule(file, json_data["rules"])
        if rule:
            action.run_action(file, rule, dry_run)
```
* **Purpose:** Command-line entrypoint that coordinates the entire workflow.
* **How It Works:**
  1. **CLI Parsing:** Sets up `argparse` with `--base-dir`, `--config`, `--recursive`, and `--dry-run`.
  2. **Path Sanitization:** Calls `resolve_path()` on both `--config` and `--base-dir`.
  3. **Config Validation:** Calls `config.validate_json(config_file)`. If invalid, prints the exact error message and exits (`sys.exit(json_error)`).
  4. **Config Loading:** Safely opens the configuration JSON using `with open(...)`.
  5. **Discovery:** Scans for all files using `scan(base_dir, recursive)`.
  6. **Pipeline Loop:** Iterates through each file:
     * Finds the highest-priority matching rule with `matchers.first_matching_rule()`.
     * If a rule matches, executes the action with `action.run_action(file, rule, dry_run)`.

---

# 2. `config.py` — Configuration Schema & Validation

[`config.py`](file:///home/lotekk/Coding/Python/Download-Manager/config.py) guards against invalid, missing, or malformed rules before any files on disk are touched.

---

### Constants
```python
ACTIONS = ["move", "archive", "rename", "remove"]
FILTER  = ["url", "extension", "size_mb", "age_days", "name", "contains_text"]
FORMATS = ["zip", "tar"]
REQUIRED_KEYS = ["when", "action"]
```
* `ACTIONS`: Whitelist of valid operations a rule can execute.
* `FILTER`: Whitelist of condition keys accepted inside `"when"`.
* `FORMATS`: Whitelist of archive compression formats supported.
* `REQUIRED_KEYS`: Mandatory keys that every single rule must contain.

---

### `validate_json(json_path, json_error = "") -> tuple[bool, str]`
```python
def validate_json(json_path, json_error = "") -> tuple[bool, str]:
```
* **Purpose:** Validates the structure, types, and values of the JSON rules file.
* **Parameters:**
  * `json_path` (`str | Path`): Path to the JSON configuration file.
  * `json_error` (`str`, optional): Default error string accumulator.
* **Returns:** `(True, "")` if the file is 100% valid, or `(False, error_message)` if any validation check fails.
* **Validation Steps:**
  1. **File Opening:** Attempts to open and parse JSON using `json.load()`. Catches syntax errors (missing commas, quotes) and returns an informative error.
  2. **Root Key Check:** Verifies that `"rules"` is a top-level key in the JSON object.
  3. **Required Keys Check:** Loops through each rule dictionary in `data['rules']` and ensures both `"when"` and `"action"` are present.
  4. **`"when"` Block Validation:**
     * Ensures `"when"` is not an empty dictionary.
     * Verifies every condition key is in the allowed `FILTER` whitelist.
     * If condition is `"size_mb"` or `"age_days"` and is a dictionary, ensures it contains at least `"greater_than"` or `"less_than"`.
  5. **`"action"` Block Validation:**
     * Ensures `"action"` is not empty and is in the `ACTIONS` whitelist.
     * If action is `"move"` or `"archive"`, verifies that `"dest"` is defined.
     * If action is `"rename"`, verifies that `"format"` is defined.
  6. **`"format"` Block Validation:**
     * If action is `"archive"`, ensures the format is in `FORMATS` (`"zip"` or `"tar"`).
  7. **Default Return:** If all checks pass, returns `(True, "")`.

---

# 3. `matchers.py` — Rule Matching & Filter Engine

[`matchers.py`](file:///home/lotekk/Coding/Python/Download-Manager/matchers.py) evaluates files against rules using a **Dispatch Table** (Strategy Pattern).

---

### `extension_filter(path: str, extensions: list[str]) -> bool`
```python
def extension_filter(path: str, extensions: list[str]) -> bool:
    if isinstance(extensions, str):
        extensions = [extensions]
    file_ext = Path(path).suffix.lstrip(".").lower()
    for ext in extensions:
        if file_ext == ext.lstrip(".").lower():
            return True
    return False
```
* **Purpose:** Checks if a file's extension matches a given list (or string) of allowed extensions.
* **Parameters:**
  * `path` (`str`): File path.
  * `extensions` (`list[str] | str`): Extensions to check (e.g. `["pdf", "docx"]` or `"pdf"`).
* **Features:**
  * Normalizes string inputs into a single-element list.
  * Strips leading dots (`.pdf` $\to$ `pdf`).
  * Case-insensitive comparison (`PDF` matches `pdf`).

---

### `get_origin_url(path: str) -> str | None`
```python
def get_origin_url(path: str) -> str | None:
```
* **Purpose:** Extracts the URL where the file was downloaded from using operating system metadata.
* **Cross-Platform Implementation:**
  * **Windows:** Opens NTFS Alternate Data Stream (`<path>:Zone.Identifier`). Browsers write `HostUrl=` and `ReferrerUrl=` into this stream upon download. It parses lines and extracts the URL.
  * **macOS (`Darwin`):** Runs `xattr -px com.apple.metadata:kMDItemWhereFroms <path>`. Decodes hex bytes into a binary plist via `plistlib.loads()` and extracts the source URL.
  * **Linux:** Queries extended filesystem attribute `user.xdg.origin.url` using `os.getxattr()`.
* **Returns:** The URL string if found, otherwise `None`.

---

### `url_filter(path, url) -> bool`
```python
def url_filter(path, url) -> bool:
    file_url = get_origin_url(path)
    if file_url is None:
        return False
    return url in file_url
```
* **Purpose:** Checks if a target substring exists inside the file's download URL.
* **Returns:** `True` if the URL contains the substring, otherwise `False`.

---

### `_parse_size_in_mb(val) -> float | None`
```python
def _parse_size_in_mb(val):
```
* **Purpose:** Internal helper that converts numbers or strings with size units into megabytes (`float`).
* **Supported Units:**
  * `"GB"`: Multiplied by `1024`
  * `"MB"`: Multiplied by `1`
  * `"KB"`: Divided by `1024`
  * `"B"`: Divided by `1024 * 1024`
* **Returns:** Size in megabytes as a `float`, or `None` if invalid.

---

### `size_filter(path, size) -> bool`
```python
def size_filter(path, size) -> bool:
```
* **Purpose:** Evaluates whether a file matches size criteria.
* **Supports:**
  * Range dictionaries: `{"greater_than": 10, "less_than": 50}`
  * Human-readable units: `{"greater_than": "1.5GB"}`
  * Direct shorthand: `500` or `"500MB"` (treated as $\ge 500\text{MB}$).
* **How It Works:**
  1. Computes `size_mb = os.path.getsize(path) / (1024 * 1024)`.
  2. If dictionary: evaluates `greater_than` and/or `less_than`.
  3. If direct number/string: evaluates `size_mb >= target`.

---

### `age_days_filter(path, age) -> bool`
```python
def age_days_filter(path, age) -> bool:
```
* **Purpose:** Checks the age of a file based on its last modification timestamp (`os.path.getmtime`).
* **Formula:** `age_in_days = (time.time() - mtime) / 86400.0`.
* **Supports:**
  * Range dictionaries: `{"greater_than": 30}`
  * Direct number: `30` (treated as $\ge 30\text{ days}$).

---

### `name_filter(path, name) -> bool`
```python
def name_filter(path, name) -> bool:
    if not name or not isinstance(name, str):
        return False
    filename = Path(path).name
    return fnmatch.fnmatch(filename, name)
```
* **Purpose:** Evaluates file names against glob patterns using Python's `fnmatch`.
* **Examples:**
  * `"Screenshot*"` $\to$ matches `Screenshot_2026.png`
  * `"*2026*"` $\to$ matches `Report_2026_Final.pdf`

---

### `contains_text_filter(path: str, text: str) -> bool`
```python
def contains_text_filter(path: str, text: str) -> bool:
    if not isinstance(text, str) or not text:
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            return text.lower() in f.read().lower()
    except (OSError, UnicodeDecodeError):
        return False
```
* **Purpose:** Inspects plain text files (`.txt`, `.csv`, `.json`, `.log`) to check if a specific keyword exists inside the file content.
* **Safety:** Safely catches `UnicodeDecodeError` so binary files don't cause crashes.

---

### `MATCHERS` Dispatch Table
```python
MATCHERS = {
    "extension": extension_filter,
    "size_mb": size_filter,
    "age_days": age_days_filter,
    "name": name_filter,
    "url": url_filter,
    "contains_text": contains_text_filter,
}
```
* **Design Pattern:** Strategy Pattern / Dispatch Table.
* **Benefit:** Replaces long chains of `if/elif` statements. New matchers are registered here without changing the evaluation engine.

---

### `matches(path, when) -> bool`
```python
def matches(path, when):
    for key, value in when.items():
        check = MATCHERS[key]
        if not check(path, value):
            return False
    return True
```
* **Purpose:** Evaluates if a file satisfies **ALL** conditions in a rule's `"when"` block (**`AND` logic**).
* **Short-Circuiting:** If any condition returns `False`, it immediately stops evaluation and returns `False`.

---

### `first_matching_rule(path, rules) -> dict | None`
```python
def first_matching_rule(path, rules):
    for rule in rules:
        if matches(path, rule["when"]):
            return rule
    return None
```
* **Purpose:** Implements **First-Match-Wins Priority**.
* **Behavior:** Checks rules sequentially from top to bottom. Returns the first rule that evaluates to `True`. If no rules match, returns `None`.

---

# 4. `action.py` — Action Execution Engine

[`action.py`](file:///home/lotekk/Coding/Python/Download-Manager/action.py) executes filesystem modifications on matched files.

---

### `archive_action(source, destination, format: str = "zip") -> bool`
```python
def archive_action(source, destination, format: str = "zip") -> bool:
```
* **Purpose:** Compresses a file into an archive and removes the original source file.
* **Key Features:**
  * **Daily Shared Archive:** Archive is named `Archive_<DD-Mon-YYYY>.<format>` inside `destination`.
  * **Append Mode (`mode="a"`):** Creates the archive if it doesn't exist, or appends into it if it does. This bundles all matching files from the same run into **one single archive**.
  * **Duplicate Avoidance:** Checks existing file names inside the archive (`zf.namelist()` or `tf.getnames()`). If a duplicate filename exists, appends `_1`, `_2`, etc.
  * **Removal:** Calls `os.remove(src)` after successful compression.
* **Returns:** `True` on success, `False` on failure.

---

### `move_action(path, destination) -> bool`
```python
def move_action(path, destination) -> bool:
    try:
        src = Path(path)
        dest_dir = Path(destination)
        dest_dir.mkdir(parents=True, exist_ok=True)

        target = dest_dir / src.name
        counter = 1
        while target.exists():
            target = dest_dir / f"{src.stem}_{counter}{src.suffix}"
            counter += 1
        shutil.move(src, target)
        return True
    except OSError:
        return False
```
* **Purpose:** Moves a file to the target destination folder.
* **Key Features:**
  * Recursively creates missing parent directories (`mkdir(parents=True, exist_ok=True)`).
  * **Collision Avoidance:** If `report.pdf` already exists in `destination`, it renames the incoming file to `report_1.pdf`, `report_2.pdf`, preventing accidental file overwrites.
  * Moves using `shutil.move()`.

---

### `remove_action(path) -> bool`
```python
def remove_action(path) -> bool:
    try:
        os.remove(path)
        return True
    except OSError:
        return False
```
* **Purpose:** Deletes unwanted files (e.g. temporary `.tmp` or `.part` files).

---

### `rename_action(path, destination, format) -> bool` (Specification)
* **Purpose:** Renames a file using template tokens or raw strings.
* **Tokens:**
  * `{name}`: Original filename without suffix (`Path(path).stem`).
  * `{extension}`: Suffix without leading dot (`Path(path).suffix.lstrip(".")`).
  * `{date}`: Today's date (`datetime.now().strftime("%Y-%m-%d")`).
* **Behavior:**
  * If `destination` is provided, moves the file to `destination` under the new name.
  * If `destination` is empty/None, renames the file in place inside `Path(path).parent`.

---

### `run_action(path, rules, dry_run = False) -> bool`
```python
def run_action (path, rules, dry_run = False) -> bool:
    destination = ""
    action = rules.get("action")
    if action in ["move", "archive"]:
        dest = Path(rules.get("dest")).expanduser()
        destination = dest if dest.is_absolute() else Path.home() / dest
```
* **Purpose:** Dispatches the file and rule to the appropriate action function.
* **Destination Resolution Rule:**
  * Absolute paths stay absolute.
  * Relative paths (`Work/Example`) resolve relative to the user's home directory (`Path.home() / dest`), ensuring files never land in unpredictable terminal working directories.
* **Dry Run Support:** If `dry_run` is enabled, prints the intended operation and returns `True` without touching the disk.

---

# 5. `example.json` — Configuration Rules Format

Example configuration demonstrating all filter types:

```json
{
  "rules": [
    {
      "when": { "url": "example.com", "extension": ["pdf"] },
      "action": "move",
      "dest": "Work/Example"
    },
    {
      "when": { "name": "Screenshot*", "age_days": { "greater_than": 30 } },
      "action": "archive",
      "dest": "Archive",
      "format": "zip"
    },
    {
      "when": { "size_mb": { "greater_than": 500 } },
      "action": "move",
      "dest": "Large"
    },
    {
      "when": { "extension": ["tmp", "part"] },
      "action": "remove"
    },
    {
      "when": { "name": "IMG_*" },
      "action": "rename",
      "format": "{date}_{name}.{extension}"
    }
  ]
}
```

* **Rule 1:** Files downloaded from `example.com` ending in `.pdf` are moved to `~/Work/Example`.
* **Rule 2:** Files named `Screenshot*` older than 30 days are bundled into `~/Archive/Archive_<DATE>.zip`.
* **Rule 3:** Files strictly larger than 500 MB are moved to `~/Large`.
* **Rule 4:** Temporary files (`.tmp`, `.part`) are deleted.
* **Rule 5:** Image files named `IMG_*` are formatted to `<DATE>_<NAME>.<EXT>`.
