
import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports"
REPORT_DIR = BASE_DIR / "docs"

def calculate_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def main():
    files = sorted(EXPORT_DIR.glob("*"))

    if not files:
        print("No export files found.")
        return

    results = {}

    for file_path in files:
        if file_path.is_file():
            checksum = calculate_checksum(file_path)
            results[file_path.name] = checksum
            print(f"{file_path.name}: {checksum}")

    REPORT_DIR.mkdir(exist_ok=True)

    report_path = REPORT_DIR / "reproducibility_checksums.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("\nChecksum report saved:")
    print(report_path)


if __name__ == "__main__":
    main()
