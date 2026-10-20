"""Download CGMacros v1.0.0 (CC BY-NC-SA 4.0) from the PhysioNet open-data mirror,
verify SHA-256, and extract only CSV files (meal photos are skipped; not used).

Usage: python scripts/download_cgmacros.py
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
BASE = "https://physionet-open.s3.amazonaws.com/cgmacros/1.0.0/"
ZIP = "CGMacros_dateshifted365.zip"
EXTRA = ["DataDictionary_Bio.csv", "DataDictionary_CGMacros-00X.csv", "SHA256SUMS.txt"]


def fetch(name: str) -> Path:
    dest = RAW / name
    if dest.exists() and dest.stat().st_size > 0:
        print(f"exists: {dest}")
        return dest
    print(f"downloading {BASE + name}")
    urllib.request.urlretrieve(BASE + name, dest)
    return dest


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    for n in EXTRA:
        fetch(n)
    z = fetch(ZIP)
    sums = {}
    for line in (RAW / "SHA256SUMS.txt").read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1].lstrip("*")] = parts[0]
    if ZIP in sums:
        got = sha256(z)
        if got != sums[ZIP]:
            print(f"CHECKSUM MISMATCH for {ZIP}: {got} != {sums[ZIP]}")
            return 1
        print("checksum OK")
    else:
        print("WARNING: zip not listed in SHA256SUMS.txt; checksum skipped")
    out = RAW / "cgmacros"
    out.mkdir(exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        members = [m for m in zf.namelist() if m.lower().endswith(".csv")]
        for m in members:
            target = out / Path(m).name if Path(m).name.lower() in {"bio.csv"} else out / m
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(m) as src, open(target, "wb") as dst:
                dst.write(src.read())
        print(f"extracted {len(members)} CSV files to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
