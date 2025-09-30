# -*- coding: utf-8 -*-
import zipfile
import lief
import os
import sys


def analyze_so(so_path, apk_so_names=None):
    try:
        elf = lief.parse(so_path)
    except Exception as e:
        print("[ERROR] Failed to parse {}: {}".format(so_path, e))
        return

    print("\n===== Analyzing {} =====".format(os.path.basename(so_path)))
    print("  Machine/Arch: {}".format(elf.header.machine_type))

    # Check hash sections
    has_dt_hash = any([entry.tag.name == "HASH" for entry in elf.dynamic_entries])
    has_gnu_hash = any([entry.tag.name == "GNU_HASH" for entry in elf.dynamic_entries])
    print("  DT_HASH: {}".format("FOUND" if has_dt_hash else "MISSING"))
    print("  DT_GNU_HASH: {}".format("FOUND" if has_gnu_hash else "MISSING"))

    # Print dependencies
    needed = [entry.name for entry in elf.libraries]
    if needed:
        print("  Dependencies:")
        for lib in needed:
            status = ""
            if apk_so_names is not None:
                status = " (FOUND)" if lib in apk_so_names else " (MISSING)"
            print("    - {}{}".format(lib, status))
    else:
        print("  No dependencies found.")


def analyze_apk(apk_path):
    with zipfile.ZipFile(apk_path, 'r') as apk:
        so_files = [f for f in apk.namelist() if f.startswith("lib/") and f.endswith(".so")]
        if not so_files:
            print("[!] No .so files found in APK")
            return

        # Collect all so names in APK for dependency check
        apk_so_names = set([os.path.basename(f) for f in so_files])

        temp_dir = "apk_so_extract"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        for so in so_files:
            so_path = os.path.join(temp_dir, os.path.basename(so))
            with apk.open(so) as so_data, open(so_path, 'wb') as f:
                f.write(so_data.read())
            analyze_so(so_path, apk_so_names)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_so.py your.apk")
        print("   or: python check_so.py libxxx.so")
        sys.exit(1)

    target = sys.argv[1]
    if target.endswith(".apk"):
        analyze_apk(target)
    elif target.endswith(".so"):
        analyze_so(target)
    else:
        print("[ERROR] Only .apk or .so files are supported")
