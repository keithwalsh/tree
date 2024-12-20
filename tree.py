import os
from pathlib import Path
from pathspec import PathSpec
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

def load_treeignore_patterns(ignore_file='.treeignore'):
    """
    Loads the patterns from the .treeignore file.

    Args:
        ignore_file (str): The path to the .treeignore file.

    Returns:
        PathSpec: Compiled PathSpec object with ignore patterns.
    """
    if os.path.exists(ignore_file):
        with open(ignore_file, 'r') as f:
            patterns = f.read().splitlines()
        return PathSpec.from_lines('gitwildmatch', patterns)
    return PathSpec.from_lines('gitwildmatch', [])

def should_ignore(relative_posix_path, pathspec):
    """
    Determines if a given path should be ignored based on the pathspec.

    Args:
        relative_posix_path (str): The POSIX-style path relative to the root directory.
        pathspec (PathSpec): Compiled PathSpec object with ignore patterns.

    Returns:
        bool: True if the path should be ignored, False otherwise.
    """
    return pathspec.match_file(relative_posix_path)

def print_tree(dir_path, prefix, root_path, pathspec):
    """
    Recursively prints the directory tree.

    Args:
        dir_path (str): Current directory path.
        prefix (str): Prefix string for formatting.
        root_path (str): The root directory path for relative calculations.
        pathspec (PathSpec): Compiled PathSpec object with ignore patterns.
    """
    try:
        # List all items in the current directory, sorted alphabetically
        items = sorted(os.listdir(dir_path))
    except PermissionError:
        print(f"{prefix}└── [Permission Denied]")
        return

    # Filter out ignored items
    filtered_items = []
    for item in items:
        item_full_path = os.path.join(dir_path, item)
        # Compute the relative path to the root directory
        relative_path = os.path.relpath(item_full_path, root_path)
        # Convert to POSIX-style path for pathspec
        relative_posix_path = Path(relative_path).as_posix()

        # If it's a directory, append a trailing slash for correct matching
        if os.path.isdir(item_full_path):
            relative_posix_path += '/'

        if should_ignore(relative_posix_path, pathspec):
            continue  # Skip ignored files/directories

        filtered_items.append(item)

    total_items = len(filtered_items)
    for index, item in enumerate(filtered_items):
        item_full_path = os.path.join(dir_path, item)
        relative_path = os.path.relpath(item_full_path, root_path)
        relative_posix_path = Path(relative_path).as_posix()

        is_last_item = index == (total_items - 1)

        connector = '└── ' if is_last_item else '├── '

        if os.path.isdir(item_full_path):
            # Append a trailing slash for directories
            display_name = f"{item}/"
            # Print directory in bold and blue
            print(f"{prefix}{connector}{Fore.BLUE + Style.BRIGHT}{display_name}")
            # Prepare the new prefix for child items
            new_prefix = prefix + ('    ' if is_last_item else '│   ')
            # Recurse into the subdirectory
            print_tree(item_full_path, new_prefix, root_path, pathspec)
        else:
            # Print file in default color
            print(f"{prefix}{connector}{item}")

def main():
    """
    Main function to execute the tree script.
    """
    # Define the root directory (current working directory)
    root_dir = os.path.abspath('.')
    root_name = os.path.basename(root_dir.rstrip(os.sep))
    if not root_name:
        # If the root directory is '/', basename will return empty
        root_name = root_dir

    # Load ignore patterns from .treeignore
    ignore_file = os.path.join(root_dir, '.treeignore')
    pathspec = load_treeignore_patterns(ignore_file)

    # Print the root directory
    print(f"{Fore.GREEN + Style.BRIGHT}{root_name}/")

    # Start printing the tree
    print_tree(root_dir, '', root_dir, pathspec)

if __name__ == "__main__":
    main()
