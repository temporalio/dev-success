
import os
from pathlib import Path
from typing import Tuple, List
from pathlib import Path
import re


def strip_iframes(markdown_content: str) -> str:
    """
    Removes all iframe tags from markdown content.

    Args:
        markdown_content: The markdown text containing possible iframes

    Returns:
        The markdown text with iframes removed
    """
    # Pattern matches <iframe ...></iframe> including multiline
    iframe_pattern = r'<iframe[^>]*>.*?</iframe>'

    # re.DOTALL makes . match newlines too
    cleaned_content = re.sub(iframe_pattern, '', markdown_content, flags=re.DOTALL)

    return cleaned_content

def stitch_markdown_files(repo_path: Path, relative_paths: list[str]) -> Tuple[str, List[str]]:
    """
    Combines multiple markdown files into a single string with separators.

    Args:
        repo_path: Base directory path
        relative_paths: List of relative paths to markdown files

    Returns:
        Tuple of (combined content, list of failed files)
    """
    contents = []
    failed_files = []

    for rel_path in relative_paths:
        full_path = repo_path / rel_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                contents.append(f.read().strip())
        except Exception as e:
            print(f"Error reading {full_path}: {e}")
            failed_files.append(rel_path)

    return "\n\n---\n\n".join(contents), failed_files

def save_combined_markdown(output_content: str, output_dir: Path, course: str, language: str) -> bool:
    """
    Saves the combined markdown content to a file.

    Args:
        output_content: Combined markdown content

    Returns:
        bool: True if save was successful, False otherwise
    """

    try:
        output_folder = output_dir / course
        output_folder.mkdir(parents=True, exist_ok=True)

        output_filename = f"{language}.md"

        with open(output_folder / output_filename, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Successfully saved combined markdown to {output_filename}")
        return True
    except Exception as e:
        print(f"Error saving combined file: {e}")
        return False

def stitcher_main(repo_path: Path, list_of_relative_paths_inside_given_repo: List[str], output_dir: Path, course: str, language: str):

    combined_content, failed_files = stitch_markdown_files(repo_path, list_of_relative_paths_inside_given_repo)

    combined_content = strip_iframes(combined_content)

    if failed_files:
        print("Warning: The following files could not be read:")
        for file in failed_files:
            print(f"  - {file}")

    if combined_content:  # Only save if we have content
        save_combined_markdown(combined_content, output_dir, course, language)
