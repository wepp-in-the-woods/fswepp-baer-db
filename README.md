# fswepp-baer-db

## Current server directories are
```
    /local/data/org/os/var/www/BAERTOOLS/baer-db
    /local/data/org/os/var/www/cgi-bin/BAERTOOLS/baer-db
```
	
## Updating baer-db

1. Open the new baer access database from Pete

2. Export the Projects, Treatments, and Treatment Costs tables. (note that the Projects.xml will
   fail to load if the database contains special characters (non-ASCII)).
   
3. Need to match the 2500-8 reports to the new files. Use the baer-db/scripts/process_2500.py script
