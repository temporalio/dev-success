# Markdown Crawler

This course scraper has two uses:

1. In course content repos, compare the list of files specified in the READMEs against the files that actually exist in the repos.
2. To scrape/stitch the markdown files together from a list of repos so we can upload them to Kapa.

We'll start by discussing the workflows you can use for these tasks, then details are at the bottom.

## Use Case 1: Performing The Comparison

1. run main.py with the `JUST_CLONE` setting.
2. run file_discoverer.py. This will print out a list of configs
3. paste those configs into config.toml
4. run the matcher.
   This will compare the config against the files that actually exist in the clone (note that it can't check chapter/lesson order -- only existence of files).
5. go through the matcher's results and see if we're missing anything

## Use Case 2: Performing the Stitching


1. Perform the comparison as described above
8. run main.py with the `STITCH` setting.
9. upload to kapa

---

## Reference and Details

### main.py

This handles three things:

- cloning the repos
- running the comparison/matching between config.toml vs what actually in the repos
- stitching the markdown files together

This does not handle the discovery of files based on the readmes. That's done in the file discoverer.

The list of repos to scrape is configured in config.toml.

To run it, make sure you have a user_config.py file, and then run main.py

#### user_config.py

```python
from constants import RunMode

RUNMODE = RunMode.JUST_CLONE
DELETE_TEMP_DIRECTORIES = False
```

The run mode has the following options:

- `JUST_CLONE` - just clones the repos and leaves them in the temp_repos folder.
  This is nice in two scenarios:

  1. if you just want to look at the files in the repos but don't want to do any matching or anything.
  2. if you want to clone the repos so you can run the file discoverer (more on this below)

- `MATCH` - will clone all the repos listed in config.toml, and it will compare the files in those repos to the ones listed in config.toml.
  It will print to the console any differences it finds between them.
  **Note that the matcher does not pay attention to file order -- only file existence.**
  To a large degree, you can consider this matcher to be the source of truth, rather than the File Discoverer.
  That's because this checks what files are _actually_ there, whereas the file discoverer checks what the readmes say _should_ be there.
  Having said that, if you see a discrepancy, it might be worth fixing with the education team so we can get the readmes to match the files.
- `STITCH` - clones all the repos listed in config.toml, and it grabs their markdown files and stitches them into one markdown file per repo, and it puts them into the output folder
  This will scrape a list of repos, and for each, it will combine the markdown files in it into a single markdown file.
  It will put the resulting markdown files into an output folder at the top of thir repo.

The `DELETE_TEMP_DIRECTORIES` flag determines whether or not to delete the temp_directories folder when it's finished.
I usually leave this as false because I like to poke around in the repos even after the script is done.
Note that when the code runs, if temp_directories exists, it will clear it before it starts.
Meaning, it starts fresh every time, so this flag just determines whether you want to clean -> clone -> clean or just clean -> clone.

### File Discoverer

To run: `python file_discoverer.py path/to/folder/of/repos`.
Note that if you're running the script from the the course_scraper directory, the path to the folder of repos is `temp_directories`.

The file discoverer crawls through the repos in the folder you pass in, and, in short, it goes through the READMEs to find the chapters and lessons, and prints them to the console.

In detail, it does the following

1. For each repo, it gathers the chapters listed in the top level readme
2. For each chapter gathered, go to its readme, and gather the lessons listed
3. print them all out in order

Note that this assumes a few things

- the readmes have the correct chapter/lesson order
- the file names in the readmes are the actual file names in the repo (this can be mitigated, as mentioned below)

We can't mitigate the first one other than by manual check against the LMS. Fortunately though, we can mitigate number two by running the matcher.

Note that this uses the pre-cloned repos, so before you run this, run main.py with at least the `JUST_CLONE` command, and `DELETE_TEMP_DIRECTORIES` false.

You can paste the output of this script into config.toml.
