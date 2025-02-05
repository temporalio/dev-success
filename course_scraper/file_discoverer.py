# WARNING
# This was written by Open AI o1, not a human.
# And we haven't actually checked it. But!
# The way this project is set up, you can actually manually check it, so we're not too afraid of using this
# Also, having said all this, this script has consistently worked for me, so I think we can be confident in using it.
#
# Usage:
# python file_discoverer.py <path_to_top_level_dir>
# python file_discoverer.py temp_repos

import os
import re
import sys

###############################################################################
# Configurable sets and substrings to filter out
###############################################################################
IGNORE_FILENAMES = {
    'readme.md',
    'questions.md',
    'contributing.md',
    'questions-placeholder.md'
}
SKIP_SUBSTRINGS = [
    'final-exam',
    'video-production',
    # Add "about-this-course" to skip from results
    'about-this-course',
]

###############################################################################
# Combined link regex
# Matches lines that start with either:
#   - One or more "-" or "*" characters, e.g. "-" or "***" or "-*"
#   OR
#   - One or more digits followed by a dot, e.g. "1.", "14."
# Then whitespace, then a markdown link "[...](...)"
###############################################################################
ITEM_LINK_REGEX = re.compile(r'^(?:[-*]+|\d+\.)\s+\[(.*?)\]\((.*?)\)', re.IGNORECASE)

###############################################################################
# Headings to look for that trigger "lessons mode" (collect bullet links until
# next heading). Add synonyms such as "lessons", "toc", or "table of contents".
###############################################################################
LESSONS_HEADINGS_REGEX = re.compile(
    r'^#{2,6}\s+(?:lessons|toc|table\s*of\s*contents)\b',
    re.IGNORECASE
)


def parse_markdown_links(md_file_path):
    """
    Reads a markdown file line by line, looks for bullet OR numbered items
    with a markdown link, and returns a list of (link_text, link_path).
    """
    links = []
    if not os.path.exists(md_file_path):
        return links

    with open(md_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.strip()
            match = ITEM_LINK_REGEX.match(line_stripped)
            if match:
                link_text, link_path = match.groups()
                links.append((link_text, link_path))
    return links


def parse_headings(md_file_path):
    """
    Return a list of (heading_line, heading_text) for lines that match a markdown heading (#...).
    """
    headings = []
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)')
    if not os.path.exists(md_file_path):
        return headings

    with open(md_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.strip()
            match = heading_pattern.match(line_stripped)
            if match:
                heading_line = line_stripped
                heading_text = match.group(2)
                headings.append((heading_line, heading_text))
    return headings


def get_lessons(subfolder_abs):
    """
    In a subfolder, parse its README.md to find bullet/numbered links.
    If there's a heading containing "lessons", "toc", or "table of contents",
    we collect bullet lines AFTER that heading (until the next heading).
    Otherwise, we collect all bullet lines in the file.

    Returns a list of (link_text, link_abs_path, link_rel_path).
    """
    readme_path = os.path.join(subfolder_abs, 'README.md')
    if not os.path.exists(readme_path):
        return []

    # We'll store all lines so that we can do a two-pass approach:
    #   (1) Check if we have a "lessons/toc" heading
    #   (2) If so, only capture lines from that heading to the next heading
    #   (3) Otherwise, parse all bullet/numbered items
    with open(readme_path, 'r', encoding='utf-8') as f:
        content_lines = f.readlines()

    # Check if there's a heading that says "Lessons", "ToC", or "Table of Contents"
    has_lessons_heading = any(LESSONS_HEADINGS_REGEX.match(line.strip()) for line in content_lines)

    lessons = []
    if has_lessons_heading:
        in_lessons_section = False
        for line in content_lines:
            line_stripped = line.strip()

            # If we match the heading, enable "in_lessons_section"
            if LESSONS_HEADINGS_REGEX.match(line_stripped):
                in_lessons_section = True
                continue

            # If we're in the section and hit a new heading (any #...), stop
            if in_lessons_section and line_stripped.startswith('#'):
                break

            if in_lessons_section:
                match = ITEM_LINK_REGEX.match(line_stripped)
                if match:
                    link_text, link_path = match.groups()
                    link_abs = os.path.join(subfolder_abs, link_path)
                    lessons.append((link_text, link_abs, link_path))
    else:
        # No "lessons/toc" heading => capture ALL bullet lines in the entire file
        all_links = parse_markdown_links(readme_path)
        for (link_text, link_path) in all_links:
            link_abs = os.path.join(subfolder_abs, link_path)
            lessons.append((link_text, link_abs, link_path))

    return lessons


def get_chapters(repo_path):
    """
    Parse the repo's top-level README.md to find bullet/numbered links that
    typically point to subfolders.
    Returns a list of (chapter_title, subfolder_abs, subfolder_rel).
    """
    readme_path = os.path.join(repo_path, 'README.md')
    if not os.path.exists(readme_path):
        return []

    bullet_links = parse_markdown_links(readme_path)
    chapters = []
    for title, link_path in bullet_links:
        subfolder_rel = os.path.dirname(link_path)
        if subfolder_rel == "":
            # Means the link is something like "README.md" with no subfolder
            subfolder_abs = repo_path
        else:
            subfolder_abs = os.path.join(repo_path, subfolder_rel)

        chapters.append((title, subfolder_abs, subfolder_rel))
    return chapters


def should_skip_path(path_str):
    """
    Return True if the path should be skipped, based on:
      - File name is in IGNORE_FILENAMES
      - Path contains any SKIP_SUBSTRINGS
      - A directory in the path is "conclusion"
      - The filename starts with "exercise-"
    """
    lower_path = path_str.lower()
    path_parts = lower_path.split(os.sep)

    # 1. If any subfolder is "conclusion", skip
    if 'conclusion' in path_parts:
        return True

    # 2. Check if the path contains any skip substrings
    for skip_substring in SKIP_SUBSTRINGS:
        if skip_substring in lower_path:
            return True

    # 3. Check the base filename
    base = os.path.basename(lower_path)

    # - ignore these known filenames
    if base in IGNORE_FILENAMES:
        return True

    # - ignore files that start with "exercise-"
    if base.startswith('exercise-'):
        return True

    return False


def parse_repo_name(folder_name):
    """
    Convert folder_name into (course_name, language), with special handling for
    an empty language. Examples:
      "edu-101-python" => ("101", "python")
      "edu-interacting-with-workflows-dotnet" => ("interacting-with-workflows", "dotnet")
      "edu-102-go-content" => ("102", "go")
      "edu-intro2cloud-content" => ("intro2cloud", "")
    """
    tokens = folder_name.split('-')

    # 1. Remove "edu" if present
    if tokens and tokens[0] == 'edu':
        tokens = tokens[1:]

    # 2. Remove trailing "content" if present
    if tokens and tokens[-1] == 'content':
        tokens = tokens[:-1]

    # If there's exactly one token left, that means we have no language token
    if len(tokens) == 1:
        course_name = tokens[0]
        language = ""
        return (course_name, language)

    # If there are at least 2 tokens, assume the last token is language
    if len(tokens) >= 2:
        language = tokens[-1]
        course_name_tokens = tokens[:-1]
        course_name = "-".join(course_name_tokens)
        return (course_name, language)

    # fallback scenario
    return ("unknown-course", folder_name)


def main(top_level_dir):
    # We'll build a structure: { course_name: { language: [list_of_paths_in_order] } }
    courses = {}

    # Find all directories that have a `README.md` => treat as "repos"
    repos = []
    for entry in os.scandir(top_level_dir):
        if entry.is_dir():
            repo_readme = os.path.join(entry.path, 'README.md')
            if os.path.exists(repo_readme):
                repos.append(entry.path)

    # Sort for consistent processing
    repos.sort()

    # For each repo, gather all lessons in reading order
    for repo in repos:
        folder_name = os.path.basename(repo)
        course_name, language = parse_repo_name(folder_name)

        chapters = get_chapters(repo)
        paths_in_order = []

        for chapter_title, chapter_abs, chapter_rel in chapters:
            if not os.path.isdir(chapter_abs):
                continue

            lesson_links = get_lessons(chapter_abs)
            for lesson_title, lesson_abs, lesson_rel in lesson_links:
                rel_subpath = os.path.normpath(os.path.join(chapter_rel, lesson_rel))
                if should_skip_path(rel_subpath):
                    continue
                paths_in_order.append(rel_subpath)

        if course_name not in courses:
            courses[course_name] = {}
        if language not in courses[course_name]:
            courses[course_name][language] = []

        courses[course_name][language].extend(paths_in_order)

    # Print everything in TOML format
    # If language is empty, we print "" = [ ... ]
    # Otherwise we print language = [ ... ]
    for course in courses:
        print(f"[{course}]")
        for lang, file_list in courses[course].items():
            if lang == "":
                print("\"\" = [")
            else:
                print(f"{lang} = [")

            for path_str in file_list:
                print(f'  "{path_str}",')
            print("]")
        print()  # blank line after each course


if __name__ == "__main__":
    if len(sys.argv) > 1:
        top_level_path = sys.argv[1]
    else:
        top_level_path = os.getcwd()

    main(top_level_path)
