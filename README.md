# fswepp-baer-db

This is separate from fsweppy-docker to encapsulate the build from the database files needed by the application.
	
## Updating baer-db

**Prerequisites (for macOS/Linux programmatic export):**
- `mdbtools` (Install via: `brew install mdbtools`)
- `pandas` (Install via: `pip install pandas`)

**Steps:**

1. Replace `fswepp-baer-db/baer-db/Ebaer.accdb` with the new version. Commit this as a baseline.

2. Export the Projects, Treatments, and Treatment Costs tables. Overwrite the files in `baer-db/`.
   - **Option A (Programmatic - Recommended for macOS/Linux):**
     Run the export script:
     ```bash
     python3 baer-db/scripts/export_tables.py
     ```
   - **Option B (Manual - Windows):**
     Open `Ebaer.accdb` in MS Access and export the `Projects`, `Treatments`, and `Treatment Costs` tables to XML.

3. Sanitize the non-printable and non-ascii characters using the `baer-db/sanitize_characters.py` script.
   - Use `git diff` to view sanitization edits.
   
4. Need to match the 2500-8 reports to the generated file naming scheme and copy them into `baer-db/2500-8/` with the correct name. 
   1. Copy the new 2500-8 pdfs into `raw_data/all_pdfs/`
   2. Use the report matching script:
      - **Agentic (Recommended for macOS/Linux):**
        ```bash
        python3 baer-db/scripts/agentic_process_2500.py
        ```
      - **Interactive:**
        ```bash
        python3 baer-db/scripts/process_2500.py
        ```
   
5. Commit and Push changes.

## Deployment on forest.moscowfsl.wsu.edu
`/workdir/fswepp-docker/docker-compose.yml` volume mounts `/workdir/fswepp-baer-db/baer-db:/var/www/BAERTOOLS/baer-db`

```
cd /workdir/fswepp-baer-db
git pull
```

### fsweppy-docker baer-db notes

`var/www/BAERTOOLS/baer-db` is were the app looks for the .xml and pdfs. it is mounted through docker

`var/www/cgi-bin/BAERTOOLS/baer-db` is where the perl scripts for the app are located
