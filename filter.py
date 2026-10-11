import os
import time
from pathlib import Path
import fnmatch


def extension_filter(path, extension) -> bool:
    """Filters by file extension (supports single extension, set, or list)."""
    if not extension:
        return False
    file_ext = Path(path).suffix.lstrip(".").lower()
    
    if isinstance(extension, (list, tuple, set)):
        return file_ext in [str(ext).lstrip(".").lower() for ext in extension]
    return file_ext == str(extension).lstrip(".").lower()


def get_origin_url(path):
    """Attempts to read the download URL from file extended attributes."""
    try:
        if hasattr(os, "getxattr"):
            url_bytes = os.getxattr(path, "user.xdg.origin.url")
            return url_bytes.decode("utf-8")
        return None
    except (OSError, AttributeError):
        return None


def url_filter(path, url) -> bool:
    """Filters by matching download source URL."""
    if not url or not isinstance(url, str):
        return False
    origin_url = get_origin_url(path)
    if not origin_url:
        return False
    return url in origin_url


def _parse_size_in_mb(val):
    """Parses numeric values or strings like '500KB', '2MB', '1GB' into MB."""
    if isinstance(val, (int, float)):
        return float(val) if val >= 0 else None
    if isinstance(val, str):
        val = val.strip().upper()
        multipliers = [("GB", 1024), ("MB", 1), ("KB", 1 / 1024), ("B", 1 / (1024 * 1024))]
        for unit, mult in multipliers:
            if val.endswith(unit):
                try:
                    num = float(val[:-len(unit)].strip())
                    return num * mult if num >= 0 else None
                except ValueError:
                    return None
        try:
            return float(val)
        except ValueError:
            return None
    return None


def size_filter(path, size) -> bool:
    """
    Filters by size in MB.
    Supports numbers, strings ('10MB'), or range dict: {'greater_than': X, 'less_than': Y}
    """
    try:
        if not os.path.isfile(path):
            return False
        size_mb = os.path.getsize(path) / (1024 * 1024)
        
        if isinstance(size, dict):
            if "greater_than" in size:
                gt = _parse_size_in_mb(size["greater_than"])
                if gt is not None and not (size_mb > gt):
                    return False
            if "less_than" in size:
                lt = _parse_size_in_mb(size["less_than"])
                if lt is not None and not (size_mb < lt):
                    return False
            return True
            
        target = _parse_size_in_mb(size)
        return size_mb >= target if target is not None else False
    except OSError:
        return False


def age_days_filter(path, age) -> bool:
    """
    Filters by file age in days since last modification.
    Supports numbers or range dict: {'greater_than': X, 'less_than': Y}
    """
    try:
        if not os.path.exists(path):
            return False
        mtime = os.path.getmtime(path)
        age_in_days = (time.time() - mtime) / 86400.0
        
        if isinstance(age, dict):
            if "greater_than" in age:
                try:
                    gt = float(age["greater_than"])
                    if not (age_in_days > gt):
                        return False
                except (ValueError, TypeError):
                    pass
            if "less_than" in age:
                try:
                    lt = float(age["less_than"])
                    if not (age_in_days < lt):
                        return False
                except (ValueError, TypeError):
                    pass
            return True
            
        return age_in_days >= float(age)
    except (OSError, ValueError, TypeError):
        return False


def name_filter(path, name) -> bool:
    """Filters by filename matching exact name, pattern, or wildcard (e.g. Screenshot*, *2026*)."""
    if not name or not isinstance(name, str):
        return False
    filename = Path(path).name
    return fnmatch.fnmatch(filename, name)


MATCHERS = {
    "extension": extension_filter,
    "size_mb": size_filter,
    "age_days": age_days_filter,
    "name": name_filter,
    "url": url_filter,
}


def matches(path, conditions) -> bool:
    """Checks if a file matches all given criteria in the 'when' block."""
    if not isinstance(conditions, dict):
        return False
        
    for key, value in conditions.items():
        matcher = MATCHERS.get(key)
        if not matcher:
            continue
        try:
            if not matcher(path, value):
                return False
        except Exception:
            return False
    return True


def first_matching_rule(path, rules):
    """Finds and returns the first rule whose conditions match the file."""
    if not isinstance(rules, list):
        return None
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        conditions = rule.get("when", {})
        if matches(path, conditions):
            return rule
    return None
