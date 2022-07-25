import copy
import os
import sys
import glob
from pathlib import Path

import P4


# ---------------------CONFIGURE THESE GLOBALS-----------------------
# depot path to library directory in the main library stream with NO trailing / or ... (eg. "//ProjectName/Library-main")
MAIN_LIBRARY_BRANCH = "//ProjectName/Library-main"
# relative path to library folder in mainline stream on depot with NO trailing / or ... (eg. "Library/UE/Content/Library")
MAIN_LIBRARY_PATH = "Library/UE/Content/Library"
# relative path to library folder in local workspace with NO trailing / or ... (eg. "UE/Content/Library")
LOCAL_LIBRARY_PATH = "UE/Content/Library"

# -------------------------------------------------------------------

p4 = P4.P4()
p4.connect()


def main():
    workspace_root = get_root()
    local_library = workspace_root / LOCAL_LIBRARY_PATH
    local_folders = get_local_library_folders(local_library)
    shares, imports = get_shares_and_imports(local_folders)
    print_results(shares, imports)


def print_results(shares, imports):
    print("Copy either the Share or Import paths below into your library dev stream.")
    print()
    print("Share paths: (preferred for child streams of main library)")
    for share in sorted(shares):
        print(f"share {share}")
    print()
    print("Import paths: (use for non-child streams)")
    for imp in sorted(imports):
        print(f"import+ {imp}")


def get_local_library_folders(local_library):
    """Returns a Set of all unique directories in the local workspace's library folder"""
    all_folders = list({Path(file).parent.relative_to(local_library) for file in local_library.rglob("*") if file.is_file()})
    return {folder: sum(f in folder.parents for f in all_folders) for folder in all_folders}


def get_shares_and_imports(local_folders):
    shares = [f"{MAIN_LIBRARY_PATH}/{folder.as_posix()}/..." for folder, parent_count in local_folders.items() if parent_count == 0 ]
    imports = [f"{MAIN_LIBRARY_BRANCH}/{MAIN_LIBRARY_PATH}/{folder.as_posix()}/..." for folder, parent_count in local_folders.items() if parent_count == 0]
    return shares, imports


def get_root():
    try:
        workspace_root = Path(sys.argv[1])
    except Exception:
        while True:
            try:
                workspace_root = Path(input("Enter Workspace Root (eg. C:\\workspaces\\user_workspace): "))
                assert workspace_root.exists() and workspace_root.is_dir()
                break
            except Exception:
                print("Could not resolve path on local machine. Make sure it is a directory that exists on this machine.")
    return workspace_root


if __name__ == "__main__":
    main()