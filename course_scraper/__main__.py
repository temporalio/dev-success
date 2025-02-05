"""
Note to set user config before running this
"""


import git
from pathlib import Path
import shutil
from concurrent.futures import ThreadPoolExecutor
import os
from tomllib import load
from stitcher import stitcher_main
from matcher import matcher_main
from typing import List, Dict
from constants import RunMode
try:
    from user_config import DELETE_TEMP_DIRECTORIES, RUNMODE
except ImportError:
    print("Please create a user_config.py file. See the readme for help.")


OUTPUT_DIR = Path("output")


def process_repos(config: Dict[str, Dict[str, List[str]]]):
    # Make a temp directory
    temp_dir = Path("./temp_repos")

    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    temp_dir.mkdir(exist_ok=True)

    # Use number of CPUs for thread count, but cap it at a reasonable number
    max_workers = min(os.cpu_count() or 4, 8)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all repos to the thread pool

        for course, course_info in config.items():
            for language, list_of_relative_paths_inside_given_repo in course_info.items():
                    if RUNMODE == RunMode.MATCH:
                        # if doing match, don't run in parallel b/c we want to keep the order
                        process_single_repo(temp_dir, list_of_relative_paths_inside_given_repo, course, language)
                    else:
                        executor.submit(process_single_repo, temp_dir, list_of_relative_paths_inside_given_repo, course, language)


    # Clean up temp directory
    if DELETE_TEMP_DIRECTORIES:
        shutil.rmtree(temp_dir, ignore_errors=True)

def process_single_repo(temp_dir: Path, list_of_relative_paths_inside_given_repo: List[str], course: str, language: str):
    if language:
      repo_name = f"edu-{course}-{language}-content"
    else:
      repo_name = f"edu-{course}-content"
    repo_path = temp_dir / repo_name

    try:
        # Clone the repository
        git.Repo.clone_from(f"git@github.com:temporalio/{repo_name}.git", repo_path)

        """
        example values for this call:
        - repo_path
          Path('temp_repos/edu-interacting-with-workflows-python-content')
        - list_of_relative_paths_inside_given_repo
          ['workflow-cancellations/cancel-vs-terminate-workflows.md', 'workflow-cancellations/handling-workflow-cancelation.md']
        - output_dir
          Path('output)
        - course
          'interacting-with-workflows'
        - language
          'python'
        """
        if RUNMODE == RunMode.STITCH:
            stitcher_main(repo_path, list_of_relative_paths_inside_given_repo, OUTPUT_DIR, course, language)
        elif RUNMODE == RunMode.MATCH:
            matcher_main(repo_path, list_of_relative_paths_inside_given_repo, course, language)
        elif RUNMODE == RunMode.JUST_CLONE:
            pass

    except Exception as e:
        print(f"Error with {course} {language}: {e}")

    # Clean up this repository
    if DELETE_TEMP_DIRECTORIES:
        if repo_path.exists():
            shutil.rmtree(repo_path)

# read the toml file at config.toml
with open("config.toml", "rb") as f:
    config: Dict[str, Dict[str, List[str]]] = load(f)

process_repos(config)
