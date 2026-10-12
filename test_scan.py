
import tempfile
from pathlib import Path
from app import scan


with tempfile.TemporaryDirectory() as folder:
    base = Path(folder)
    (base / "a.txt").write_text("hello")

    sub = base / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("hello")

    dest = base / "destination"
    dest.mkdir()
    (dest / "c.txt").write_text("hello")

    files = scan(str(base), False, str(dest))
    assert len(files) == 1
    print("Test 1 passed")

    files = scan(str(base), True, str(dest))
    assert len(files) == 2
    print("Test 2 passed")

    files = scan(str(base), True, "")
    assert len(files) == 3
    print("Test 3 passed")

    # Test 4: destination is a file
    files = scan(str(base), True, str(base / "a.txt"))
    assert len(files) == 2
    print("Test 4 passed")

    # Test 5: base directory does not exist
    files = scan(str(base / "missing"), True, "")
    assert len(files) == 0
    print("Test 5 passed")
