# AI Security Engineer Trainee - Assignment

All my answers are in **Assignment.pdf**.

## What's in here

```
Assignment(AI Security).pdf      -> all answers (Assignment 1, 2 and 3)
simple/             -> the simple codes, same as in the PDF
advanced/           -> larger, more high level versions of the same codes
data/               -> bigger data used by the advanced codes
requirements.txt
```

## Simple vs advanced

In the PDF I kept the code very simple on purpose, that's how I start, I break things down first.
The `advanced/` folder is the bigger version of the same 3 problems:

| Problem | Simple | Advanced |
|---|---|---|
| 1. API to SQLite | 2 books | 60 books, retries, fallback file, no duplicates, stats |
| 2. Scores + chart | 4 students | 100 students, average, median, grades, 2 charts saved |
| 3. CSV to SQLite | 4 users | 124 rows with messy data, email check, duplicates skipped, report |

The API links are example links, so if the API is not reachable the advanced codes use the files in `data/` and still run.

## How to run

```bash
pip install -r requirements.txt
cd advanced
python q1_books_api.py
python q2_scores_chart.py
python q3_csv_import.py
```
