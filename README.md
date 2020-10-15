# sufkes_redcap
Scripts for REDCap API functions, quality control, report generation, and special-purpose scripts for the Stroke Team at SickKids.

# Getting started
## Installation
All scripts require Python 2.7.

Most of the scripts require the Python module "PyCap". See https://github.com/redcap-tools/PyCap

PyCap requires the module "requests". See https://pypi.org/project/requests

Some scripts require the Python module "pyyaml". See https://pypi.org/project/PyYAML

Some scripts require the Python module "Pandas". See https://pandas.pydata.org/pandas-docs/stable/install.html
## Configure `settings.yml` and `api_keys.yml`
Most scripts use REDCap API functions. To interact with a REDCap project through the API, a user must have API rights enabled in the User Rights tab of the REDCap project page, and an API token. Users can then interact with the project using their API token and the API URL of the REDCap instance in which the project is hosted. The API URL for a REDCap instance can be found in the API Playground of any of the projects it hosts. The API URLs for the REDCap instances at SickKids are:
| REDCap Instance | API URL |
|:-|:-|
| External | https://redcapexternal.research.sickkids.ca/api/ |
| Internal | https://redcapinternal.research.sickkids.ca/api/ |
| Internal Survey | https://staffsurveys.sickkids.ca/api/ |

Most scripts allow the user to specify an API token and URL as arguments. To limit the need to retrieve passwords, a user can instead configure a `settings.yml` file and an `api_keys.yml` file, so that API tokens and URLs can be retrieved using a short, user-defined keyword ("code name"). While most scripts allow the user to specify API URLs and tokens manually, the data package and quality control scripts (`makeDataPackage.py` and `mainIntraProject.py`) *require* the following setup. To set up the files:
1. Create an `api_keys.yml` file. This is a YAML file which assigns a code name to each API (URL, token) pair. An entry must be created for each project with which the user will interact. The `api_keys.yml` file can be saved in any safe location on your computer, but should not be readable by other users.

   Each entry must be of the form:
   ```
   my_code_name_for_this_project:
     url: <API URL for this project's REDCap instance>
     key: <my API token for this project>
   ```
   E.g.
   ```
   ipss_v4:
     url: https://redcapexternal.research.sickkids.ca/api/
     key: 1234567890ABCDEFGHIJKLMNOPQRSTUV
   ```
   Note that the URL and token must be indented from the code name using the same number of spaces, and tab characters must not be used.

   **Note for Stroke Team:** This repository has a template `api_keys.yml` file, which has an entry for all REDCap projects associated with the Stroke Team as of April 2020. If you are using this repository in the Stroke Team, simply copy that file to another location, and replace the API key entries with your own tokens. For consistency within the Stroke Team, do not change the code names from the values used in the template.
2. Create a `settings.yml` file. This is a YAML file in which a user can specify defaults to be used in the functions in this repository. Create a copy of the `settings_template.yml`, name it `settings.yml`, and place it in the root directory of this repository (i.e. the directory that contains `settings_template.yml`). Modify the values of the new `settings.yml` file, which will be used in scripts automatically.
   * (**Important**) Set the `api_key_path` to the full path of your `api_keys.yml` file. Once this is done, you will be able to interact with REDCap projects by specifying a code name instead of an API (URL, token) pair. For example, you could export all records from the project `ipss_v4` using the following commands:
     * Before coniguring api_keys.yml and settings.yml:
       ```
       python exportRecords.py my_file.csv -u https://redcapexternal.research.sickkids.ca/api/ -k 1234567890ABCDEFGHIJKLMNOPQRSTUV
       ```
     * After configuring api_keys.yml and settings.yml:
       ```
       python exportRecords.py my_file.csv -n ipss_v4
       ```
   * (**Optional**) The `default_api_url` can be set to the API URL that you most commonly use. This is *not* required to retrieve API (URL, token) pairs by code name, but can be useful for interacting with projects which do not have an entry in the `api_keys.yml` file.
   * (**Optional**) The `event_ids_path` can be set to the full path of the `event_ids.yml` file which sits in the root directory of this repository, or to the path of a user's own `event_ids.yml` file. The `event_ids.yml` file associates the human-readable event names defined in the REDCap (e.g. `acute_arm_1`) with the numeric codes associated with those events that appear in URL addresses for pages corresponding to those events (e.g. `34247`). This is *only* used in the quality control script. Its sole purpose is to enable automatic generation of a REDCap link for a specific record, instrument, and event name. This file must be updated for each project for which a user wishes to automatically generate links in the quality control script. Note that the code names used in this file must match the code names used in the the user's `api_keys.yml` file.

     **Note for Stroke Team:** This file already contains entries for all REDCap projects associated with the Stroke Team as of April 2020. You simply need to modify the `event_ids_path` entry in your `settings.yml` file to point to it.
   * (**Optional**) Set the `default_backups_dir`. This is the default directory to which project backups will be saved by `backupProjects.py`.

# Documentation
This section contains a list of the most useful functions in this repository, and limited information about their usage. Most of the useful scripts are command-line tools which will print usage information if the `-h/--help` option is provided.

E.g. to figure out how to use `exportRecords.py`, do:
```
python exportRecords.py -h
```
Note that the `python` may be omitted depending on the user's Python configuration.

The scripts are organized in three directories:
* `misc` contains various scripts which can be used with any REDCap project.
* `qc` contains contains project quality control scripts, which can be used with any REDCap project.
* `ipss` contains scripts that perform functions associated with REDCap projects in the Stroke Team at SickKids.

## misc - Miscellaneous scripts for any REDCap project
This directory contains a few useful command line tools (described now), and many helper scripts.
### Command-line tools in `misc`
* `exportRecords.py`

  Export records from a project. Can request specific records, events, instruments, or fields.

  E.g. export all records from project `ipss_v4`:
  ```
  python exportRecords my_file.csv -n ipss_v4
  ```
  E.g. export fields `sex` and `weight` for records `123` and `345` from project `ipss_v4`:
  ```
  python exportRecords my_file.csv -n ipss_v4 -r 123 345 -f sex weight
  ```
* `importRecords.py`

  Import records to a project. The input records must be stored in a CSV file.

  E.g. import the data in `my_file.csv` into `ipss_v4`:
  ```
  python importRecords my_file.csv -n ipss_v4
  ```
* `backupProjects.py`

  Backup REDCap projects. Project settings are saved to an XML file; all records are saved to a CSV file; files stored in "file upload" fields are saved.

  E.g. save a backup of project `ipss_v4`, to a specified directory:
  ```
  python backupProjects.py -n ipss_v4 -o /home/steve/Desktop/
  ```
  E.g. save a backup of every project that has an entry in your `api_keys.yml` file:
  ```
  python backupProjects.py -o /home/steve/Desktop/
  ```
  E.g. save a backup of project `ipss_v4` to the default backup location specified in your `settings.yml` file:
  ```
  python backupProjects.py -n ipss_v4
  ```
* `exportUsers.py`

  Generate a CSV containing information about each REDCap user.

### `importMetadata.py`


### `parseLogging.py`

### `setFormCompleteBlanks.py`

### `transferUsers.py`

### Helper scripts in `misc`
These are small scripts in the `misc` directory which are used in various places throughout the repository. Most of these are rarely useful on their own.
* `ApiSettings.py` - Defines the `ApiSettings` class, with methods for parsing the user's `settings.yml` file, and retrieving API (URL, token) pairs from the user's `api_keys.yml` file
* `Color.py` - Class for coloured terminal output
* `Field.py` - Class which gets attributes and methods from the data dictionary
* `ProgressBar.py` - Class for terminal progress bar
* `Timer.py` - Class for timing execution
* `createDAGRecordMap.py` - Method that returns a dictionary with information about each data access group
* `createFormRepetitionMap.py` - Method that returns a dictionary with information about how and where each instrument repeats
* `createRecordIDMap.py` Method that returns dictionary that maps record IDs to a list of row numbers in the exported data
* `deleteRecords.py` - Method that deletes all or specific records in a project. This script has not been thoroughly tested.
* `exportFiles.py` - Method that exports files uploaded to "file upload" fields. This is used in `backupProjects.py`.
* `exportFormEventMapping.py` - Method that returns a list of dictionaries specifying the events in which each instrument appears
* `exportFormsOrdered.py` - Method that returns a list of instruments and information about them, in the order in which they appear in the project
* `exportProjectInfo.py` - Method that returns a dictionary containing information about the project (e.g. project name, project ID)
* `exportProjectXML.py` - Method that export the project XML, containing all settings for the project. This is used by `backupProjects.py`.
* `exportRepeatingFormsEvents.py` - Method that returns a list of dictionaries, specifying the events in which each instrument appears
* `getDAGs.py` - Method that returns a list of data access groups for which records exists. Data access groups with no records are excluded.
* `getEvents.py` - Method that returns a dictionary containing information about each event. This script attempts to read numeric event IDs from the user's `event_ids.yml` file, if present.
* `getRecord.py` - Helper methods used to retrieve records in the branching logic functions
* `getRecordIDList.py` - Method that returns a list of record IDs in a project, without duplicates. This function may fail to return record IDs which contain no data in the instrument which contains the record ID field (i.e. the first instrument in the project).
* `isEventFieldInstanceValid.py` - Method which determines whether or not a specific field can contain data in a specific row of exported data. For example, in a longitudinal project, rows corresponding to a particular event will only contain fields that are part of the event; all other fields will be blank.
* `labelRecords.py` - Method which attempts to replace values in exported records. Values are replaced with the label `rr_hidden` if the field is hidden by branching logic; `rr_invalid` if the field cannot contain data in the current row (e.g. if the field is not part of the event to which the current row corresponds); and `rr_error` if there is an error in the field's branching logic or the branching logic cannot be parsed.
* `parseMetadata.py` - Method that reads a data dictionary and returns a dictionary mapping field names to instances of the `Field` class (defined in `Field.py`)
* `tokenizeBranchingLogic.py` - Helper method used in `writeBranchingLogicFunction.py`
* `translateTokens.py` - Helper method used in `writeBranchingLogicFunction.py`
* `writeBranchingLogicFunction.py` - Attempts to create a Python function mimicking the behaviour of a field's branching logic function. The returned function will not behave identically to the REDCap branching logic in all cases.

## qc - Quality control scripts for any REDCap project
## ipss - Scripts for special tasks related to the Stroke Team at SickKids
