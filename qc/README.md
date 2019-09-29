# Quality control pipeline for REDCap projects

* Written for Python 2. 
* Requires PyCap module.

* Usage:
```
python mainIntraProject.py <API URL> <API key> <out dir> <checklist 1> [checklist 2] ... 
```

* For external REDCap projects, the API URL is https://redcapexternal.research.sickkids.ca/api/
* Users should use their own API token (key) obtained through the web page of the REDCap project you wish to check.
* An easy way to run (in Bash) is to write the arguments to a file (e.g. see sample_args.txt), and run `python main_intra-project.py $(cat sips2/sips2_args.txt)`). If you use this method, please create your own argument list with your own API token in the argument list and place on your local machine.
