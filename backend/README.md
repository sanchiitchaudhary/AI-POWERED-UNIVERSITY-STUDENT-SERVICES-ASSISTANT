# University Student Services Assistant (backend)

Python 3.11 backend scaffold. Install `requirements.txt`, then run `pytest -q` or `uvicorn app.main:app --reload` from this directory.

To validate or load Annex C CSVs, run `python scripts/validate_students.py --dir <dir>` or `python scripts/load_students.py --dir <dir> [--db path]`.

To rebuild the checked student CSV export from the seed, run `python scripts/seed_to_csv.py` from this directory.
