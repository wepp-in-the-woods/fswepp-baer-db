# fswepp-baer-db

This is separate from fsweppy-docker to encapsulate the build from the database files needed by the application.
	
## Updating baer-db

1. Open the new baer access database from Pete. This will likely require adding the file as a trusted file in MS Access

3. Export the Projects, Treatments, and Treatment Costs tables. Overwrite the files in baer-db.
   - Commit changes as a intermediary step. We have git we should use it!
   
4. Replace fswepp-baer-db/Ebaer.accdb and commit! This way it is ready for next year.

5. Sanitize the non-printable and non-ascii characters using the `baer-db/sanitize_characters.py` script.
   - Use git diff to view sanitization edits.
   
6. Need to match the 2500-8 reports to the generated file naming scheme and copy them into `baer-db/2500-8`
   with the correct name. 
   1. Copy the new 2500-8 pdfs into `raw_data/all_pdfs`
   2. Use the `baer-db/scripts/process_2500.py` script
   
7. Commit and Push changes

## Deployment on forest.moscowfsl.wsu.edu
`/workdir/fswepp-docker/docker-compose.yml` volume mounts `/workdir/fswepp-baer-db/baer-db:/var/www/BAERTOOLS/baer-db`

```
cd /workdir/fswepp-baer-db
git pull
```

### fsweppy-docker baer-db notes

`var/www/BAERTOOLS/baer-db` is were the app looks for the .xml and pdfs. it is mounted through docker

`var/www/cgi-bin/BAERTOOLS/baer-db` is where the perl scripts for the app are located
