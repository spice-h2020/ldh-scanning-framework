# Implementation notes
issues and thoughts...

## Progress tracking
- timestamp doesn't work too well. paging of results could lead to duplicate 
entries where new data is created between page requests.
- each scan class can tag activity log entries with its own unique tag to 
it's been scanned by that class. 
- AL scan tags should not be top level attributes, for the danger of 
overwriting critical AL fields. An AL field should be created, where 
scan tags can be created as sub items or added to a list. A list would 
be better as it only requires a single field which can be set to index in
MongoDB. 
- Queries for new AL entries should, instead of filtering by timestamp, filter
by the presence or absence of an entry in the scan tag list. 

## Logging
- `status.json` should be use to log activity.
- Since progress tracking is now done via scan tags in teh AL itself, the
`status.json` file is not needed for the running of the program, only for
human inspection to check activity history and for problems.
- an entry for each running of the main script. Top level info such as 
timestamps and number of AL entries returned plus logging of errors for AL 
request process
- a list of objects for each scan class that runs, each one should contain
details such as number of objects scanned, number of notifications generated 
plus any errors that occurred.
- `status.json` logfile should be rotated once file size reaches a certain 
threshold. Old files should be renamed with a suitable timestamp in the
filename.
