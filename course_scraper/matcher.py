from pathlib import Path
from typing import List, Dict, Set

def should_include_file(relative_path: str) -> bool:
    """
    Determines if a file should be included in the comparison.

    Args:
        relative_path: Relative path of the file

    Returns:
        bool: True if the file should be included, False if it should be filtered out
    """
    # Convert to forward slashes for consistency
    path = relative_path.replace("\\", "/")

    # Files to exclude
    if (
        path.endswith("README.md") or
        path.endswith("questions.md") or
        path.endswith("CONTRIBUTING.md") or
        path.endswith("questions-placeholder.md") or
        'final-exam' in path or
        'video-production' in path
    ):
        return False

    # Files to exclude
    if "/exercise-" in path:
        return False

    # Paths to exclude
    excluded_prefixes = ["about-this-course", "conclusion"]
    return not any(path.startswith(prefix) for prefix in excluded_prefixes)

def find_all_markdown_files(base_path: str) -> Set[str]:
    """
    Recursively finds all markdown files in the base path.
    Returns them as relative paths from the base.
    """
    base = Path(base_path)

    if not base.exists():
        raise ValueError(f"Base path does not exist: {base_path}")

    if not base.is_dir():
        raise ValueError(f"Base path is not a directory: {base_path}")

    markdown_files = set()

    for path in base.rglob("*.md"):
        relative_path = str(path.relative_to(base)).replace("\\", "/")
        if should_include_file(relative_path):
            markdown_files.add(relative_path)

    return markdown_files

def compare_markdown_lists(base_path: str, relative_paths: List[str]) -> Dict[str, Set[str]]:
    """
    Compares the given list of markdown files against what exists in the directory.

    Args:
        base_path: Base directory path
        relative_paths: List of relative paths to check

    Returns:
        Dictionary with:
            - 'missing': Files in directory but not in list
            - 'extra': Files in list but not in directory
    """
    # Convert input paths to use forward slashes for consistency
    given_paths = {path.replace("\\", "/") for path in relative_paths
                  if should_include_file(path)}

    try:
        actual_paths = find_all_markdown_files(base_path)
    except ValueError as e:
        print(f"Error: {e}")
        return {'missing': set(), 'extra': given_paths}  # If dir doesn't exist, all paths are "extra"

    return {
        'missing': actual_paths - given_paths,
        'extra': given_paths - actual_paths
    }

def matcher_main(base_path: Path, relative_paths: List[str], course: str, language: str):

    try:
        comparison = compare_markdown_lists(base_path, relative_paths)

        output = []

        output.append("\n")
        output.append("@@@@@@@@")

        output.append(f"@@ {course}")
        output.append(f"@@ {language}")

        output.append("@@@@@@@@")

        if comparison['missing']:
            output.append("\nFiles in directory but missing from your list:")
            for file in sorted(comparison['missing']):
                output.append(f"  - {file}")

        if comparison['extra']:
            output.append("\nFiles in your list but not found in directory:")
            for file in sorted(comparison['extra']):
                output.append(f"  - {file}")

        if not comparison['missing'] and not comparison['extra']:
            output.append("\nYour list matches exactly with the markdown files in the directory!")

        # Print everything at once
        print("\n".join(output))

    except Exception as e:
        print(f"Error during comparison: {e}")

