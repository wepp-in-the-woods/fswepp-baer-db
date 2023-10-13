# fswepp-baer-db

## Install in fsweppy-docker var/www/
```
    var/www/BAERTOOLS/baer-db
    var/www/cgi-bin/BAERTOOLS/baer-db
```

This is separate from fsweppy-docker to encapulate the build from the database files needed by the application.
	
## Updating baer-db

1. Open the new baer access database from Pete

2. Export the Projects, Treatments, and Treatment Costs tables. (note that the Projects.xml will
   fail to load if the database contains special characters (non-ASCII)).
   
3. Need to match the 2500-8 reports to the new files. Use the baer-db/scripts/process_2500.py script
