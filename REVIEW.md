# Code Review

This document summarizes the findings from a code review of the `Yuuqq/POLI7002-TextAsData` repository, organized by severity.

## CRITICAL

### Hardcoded Secrets in Source Code
* **File:**
  * `code/python/nyt_demo.py` (Line 2)
  * `homework/hw2/Hu_replication.py`
  * `homework/hw2/Hu_trump.py`
  * `homework/hw2/Hu_hillary.py`
* **Impact:** A hardcoded NYT API key (`api-key=<redacted>` and `api-key=<redacted>`) is exposed in the repository. Hardcoded secrets can lead to unauthorized access, malicious use, and quota exhaustion.
* **Fix Suggestion:** Remove the hardcoded API key from the script. Load the key securely using environment variables (e.g., `os.environ.get('NYT_API_KEY')`) or a configuration file that is added to `.gitignore`. Revoke the exposed key immediately.

## HIGH

### Insecure HTTP API Calls
* **Files:**
  * `code/python/nyt_demo.py` (Line 2)
  * `code/python/stemming.py` (Line 16)
  * `homework/hw2/Hu_replication.py`
  * `homework/hw2/Hu_trump.py`
  * `homework/hw2/Hu_hillary.py`
* **Impact:** API requests are being made over plain HTTP (`http://api.nytimes.com/...` and `http://avalon.law.yale.edu/...`). This makes requests vulnerable to Man-in-the-Middle (MitM) attacks where traffic can be intercepted or manipulated.
* **Fix Suggestion:** Change the URLs to use `https://` to ensure all data is encrypted in transit.

## MEDIUM

### Hardcoded Absolute Paths
* **Files:**
  * `code/python/lexis_dtm.py` (Line 8: `wd = "/Users/brycedietrich/Desktop/"`)
  * `code/python/dictionaries.py` (Line 13: `wd = "/Users/brycedietrich/Desktop/"`)
  * `code/python/lexis.py` (Line 12: `wd = "/Users/brycedietrich/Desktop/"`)
  * `homework/hw3/lexis_dtm.py` (Line 7: `wd = "/Users/brycedietrich/Desktop/"`)
  * `homework/hw3/lexis.py` (Line 12: `wd = "/Users/brycedietrich/Desktop/"`)
  * `code/r/lda.R` (Line 12: `setwd("/Users/brycedietrich/Dropbox/text_class/lectures/lda/")`)
  * `homework/hw4/dictionary.R` (Line 5: `setwd("/Users/brycedietrich/Dropbox/text_class/homework/homework4/")`)
  * `code/r/svm.R` (Line 5: `setwd("/Users/bjdietrich/Dropbox/text_class/lectures/svm/")`)
* **Impact:** Code is tightly coupled to a specific user's file system, making it completely unportable. It will fail to run for other developers or in Continuous Integration environments.
* **Fix Suggestion:** Use relative paths (e.g., `./` or `../`) or utilize path-resolution libraries like `os.path` / `pathlib` in Python and the `here` package in R to build file paths dynamically relative to the project root.

### Lack of Test Coverage
* **Files:** Global / Project-wide
* **Impact:** The repository currently has 0% test coverage. There are no unit or integration tests, meaning all logical paths are high-risk and untested, increasing the likelihood of silent regressions when changes are made.
* **Fix Suggestion:** Introduce testing frameworks (`pytest` for Python, `testthat` for R) and begin adding unit tests for core text processing logic.

## LOW

### Inefficient File I/O in Loops
* **Files:**
  * `code/python/lexis_dtm.py` (Line ~39)
  * `code/python/dictionaries.py` (Line ~76)
  * `homework/hw3/lexis_dtm.py` (Line ~39)
  * `homework/hw3/trump_dtm.py` (Line ~31)
* **Impact:** Opening a file in append mode (`'a'`) inside a `for` loop for every iteration causes severe I/O overhead and performance degradation, especially with larger datasets.
* **Fix Suggestion:** Open the file once outside the loop and write rows within the context manager block.

### Unclosed File Handles / Resource Leaks
* **File:** `code/python/dictionaries.py` (Line 43)
* **Impact:** The script uses `f = open(...)` to read files without explicitly calling `f.close()` or using a context manager. This can lead to file descriptor exhaustion if run over a large directory of files.
* **Fix Suggestion:** Refactor to use the `with open(...) as f:` context manager, which ensures files are automatically closed even if exceptions occur.

### Code Organization & Developer Experience
* **Files:** Global / Project-wide
* **Impact:** Missing standard dependency management files (e.g., `requirements.txt` for Python, `renv` for R). Additionally, several scripts (e.g., `lexis.py`, `lexis_dtm.py`) are duplicated between `code/` and `homework/hw3/` directories.
* **Fix Suggestion:** Document setup instructions in `README.md`, extract duplicated code into a shared module to adhere to DRY principles, and provide dependency lockfiles.
