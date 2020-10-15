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
This directory contains a few useful command line tools, and many helper scripts.
### Command-line tools in `misc`
#### `exportRecords.py`

  Export records from a project. Can request specific records, events, instruments, or fields.

  E.g. export all records from project `ipss_v4`:
  ```
  python exportRecords my_file.csv -n ipss_v4
  ```
  E.g. export fields `sex` and `weight` for records `123` and `345` from project `ipss_v4`:
  ```
  python exportRecords my_file.csv -n ipss_v4 -r 123 345 -f sex weight
  ```
  E.g. export all records from project `ipss_v4`; replace fields with labels to indicate if they are hidden by branching logic, or cannot be completed for the current row (see `labelRecords.py` for more information):
  ```
  python exportRecords my_file.csv -n ipss_v4 -l
  ```
#### `importRecords.py`

  Import records to a project. The input records must be stored in a CSV file.

  E.g. import the data in `my_file.csv` into `ipss_v4`:
  ```
  python importRecords my_file.csv -n ipss_v4
  ```
#### `backupProjects.py`

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
#### `exportUsers.py`

  Generate a CSV containing information about each REDCap user.

#### `importMetadata.py`
Import a data dictionary CSV to a REDCap project. Overwrites current data dictionary.

#### `parseLogging.py`
Parse logging CSV files exported from REDCap using the "Export all logging (CSV)" button. The information can be filtered by record ID or field. Multiple logging files can be parsed at once.

E.g. See all changes to record `123` stored in `log.csv`:
```
python parseLogging.py -l log.csv -r 123
```
E.g. See all changes to fields `sex` and `weight` for records `123` and `345` stored in `log.csv`:
```
python parseLogging.py -l log.csv -r 123 345 -f sex weight
```
E.g. See all changes to record `123` stored in `log1.csv` and `log2.csv`; save parsed data to a new CSV:
```
python parseLogging.py -l log1.csv log2.csv -r 123 -o parsed_data.csv
```

#### `setFormCompleteBlanks.py`
An instrument's completion status can be set to `0`/`Incomplete` (red), `1`/`Unverified` (yellow), or `2`/`Complete` (green), even if the instrument contains no data. In such cases, it is often desired to set the completion status to blank. This script finds all empty forms, and replaces their completion statuses with blanks. The user may also generate CSV files which can be manually imported to overwrite the completion statuses with blanks (safer; recommended).

E.g. Generate CSV files which can be imported to overwrite `0`/`Incomplete` form completion statuses to blank for every empty instrument in project `ipss_v4`:
```
python setFormCompleteBlanks.py -n ipss_v4 -o /directory/to/save/csv/files/to/
```
E.g. Automatically overwrite `0`/`Incomplete` form completion statuses to blank for every empty instrument in project `ipss_v4`:
```
python setFormCompleteBlanks.py -n ipss_v4
```
E.g. Automatically overwrite `0`/`Incomplete`, `1`/`Unverified`, and `2`/`Complete` form completion statuses to blank for every empty instrument in project `ipss_v4`:
```
python setFormCompleteBlanks.py -n ipss_v4 -s 0 1 2
```
#### `transferUsers.py`
Transfer users between two projects. This function can be useful when creating a new version of a project and all users in the original project need to be added to the new one.

E.g. Transfer all users from project `ipss_v3` to `ipss_v4`:
```
python transferUsers.py -n ipss_v3 ipss_v4
```
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
* `labelRecords.py` - Method which attempts to replace values in exported records. Values are replaced with the label `rr_hidden` if the field is hidden by branching logic; `rr_invalid` if the field cannot contain data in the current row (e.g. if the field is not part of the event to which the current row corresponds); and `rr_blerror` if there is an error in the field's branching logic or the branching logic cannot be parsed. The branching logic labels (`rr_hidden`) are not always consistent with REDCap (i.e. a field may be marked hidden, but be visible in REDCap).
* `parseMetadata.py` - Method that reads a data dictionary and returns a dictionary mapping field names to instances of the `Field` class (defined in `Field.py`)
* `tokenizeBranchingLogic.py` - Helper method used in `writeBranchingLogicFunction.py`
* `translateTokens.py` - Helper method used in `writeBranchingLogicFunction.py`
* `writeBranchingLogicFunction.py` - Attempts to create a Python function mimicking the behaviour of a field's branching logic function. The returned function will not behave identically to the REDCap branching logic in all cases.

## qc - Quality control scripts for any REDCap project
The primary command line tool is `mainIntraProject.py`, which performs quality checks within a single project. This script reads YAML configuration files. The `.yml` files are example configurations. There are a few old scripts which may no longer be useful and are kept only for reference

There are two old scripts, `mainInterProject.py` and `mainInterProject_vipsspecial.py` which perform quality checks that compare data between two REDCap projects. These old scripts are kept for reference, and instructions for their use are not provided. The rest of the scripts are helpers.
### How to perform quality control checks on a project.
### Helper scripts in `qc`
* `Check.py` -
* `checkDriver.py` -
* `checkDriverInterProject.py` -
* `checklist_default.py` -
* `checklist_hidden_data.py` -
* `checklist_extra.py` -
* other `checklist_` files -
* `createChecklist.py` -
* `dates.py` -
* `formatStrings.py` -
* `isProjectCompatible.py` -
* `readConfig.py` -
* `recordsFromFile.py` -
* `reportCheckResults.py` -
* `saveData.py` -
* `saveRecords.py` -
### Old scripts in `qc`
* `mainInterProject.py` - Performs quality checks that compare data between two REDCap projects. This script may still work, but instructions for its use are not provided.
* `mainInterProject_vipsspecial.py` - Performs quality checks that compare data between IPSS V3 and VIPS II. This script may still work, but instructions for its use are not provided.
* `combineSiteReports.py` - This script can be used to combine site-specific reports output by the `mainIntraProject.py` into a single file.

## ipss - Scripts for special tasks related to the Stroke Team at SickKids
This directory contains a few useful command line tools, helper scripts used in various places throughout this repository, and some old scripts which are no longer useful and are kept only for reference.
### Command-line tools in `ipss`
#### `enrollmentReportIPSS.py`
Generate a report on patient enrolment in the IPSS, broken down by stroke type, data access group, and year of admission.
#### `makeDataPackage.py`
Generate a formatted data package based on a user-specified configuration file. Data can be taken from multiple projects. The package can include specific instruments, events, forms, fields, and records. The user can specify settings which apply to the whole data package, and specific settings for each project included.

To generate a data package, first create a configuration YAML file. An example configuration file for a package containing data from two projects is given in `dataPackageExample.yml`. The configuration file must obey the format described below:

```
options:
  file_split_type: <none, projects, chunks>
  out_dir: </directory/to/save/package/to/>

projects:
  - code_name: <code name of first project, defined in user's api_keys.yml file>
    options:
      split_type: <none, events_only, repeat_forms_events, all_forms_events>
      use_getIPSSIDs: <True, False>
    getIPSSIDs_args:
      [arguments accepted by the getIPSSIDs function]
    exportRecords_args:
      [arguments accepted by the exportRecords function]

  - code_name: <code name of second project, defined in user's api_keys.yml file>
...
```
The package-wide settings, specified in the `options` section, are defined as follows:
* `file_split_type` - Determines how data will be separated into files. Can be set to:
  * `none` - A single file is generated, containing data from all projects.
  * `projects` - The data from each project is saved to a separate file.
  * `chunks` - The data from each "chunk" of data (determined by the project `split_type`; defined below) is saved to a separate file.
* `out_dir` - The directory to which the data package will be saved.

In the `projects` section, a separate entry must be created for each project included in the package. The project-specific settings are defined as follows:
  * `code_name` - The code name of the project. This must appear in the user's `api_keys.yml` file.
  * `options`
    * `split_type` - Determines how data from the current project will be separated into chunks. Each chunk of data will appear on a separate tab of the spreadsheet or in a separate file, depending on the package-wide setting `file_split_type`. `split_type` can be set to:
      * `none` - All data for the current project will appear in a single chunk.
      * `events_only` - Data from different events will be separated.
      * `repeat_forms_events` - Data will be separated based on the REDCap columns `redcap_event_name` and `redcap_repeat_instrument` (e.g. two repeating instruments in a single event will be separated into two chunks; all non-repeating instruments in a single event will appear in a single chunk; all instruments in a repeating event will appear in a single chunk).
      * `all_forms_events` - A separate chunk will be created for each instrument, and each event in which the instrument appears.
    * `use_getIPSSIDs` - Whether or not the `getIPSSIDs` function will be used to determine the set of record IDs whose data will be included for the current project.
  * `getIPSSIDs_args` - Arguments passed to the `getIPSSIDs` function, defined in `getIPSSIDs.py`. These options can be used to specify which record IDs to include for the current project. See the documentation on `getIPSSIDs.py` for more information. If the project setting `use_getIPSSIDs` is `False`, these options will be ignored.
  * `exportRecords_args` - Arguments passed to the `exportRecords` function, defined in `exportRecords.py`. These options can be used to specify which events, instruments, fields (and record IDs) to include for the current project. See documentation on `exportRecords.py` for more information. If the project setting `use_getIPSSIDs` is `True`, the `record_id_list` argument passed to `exportRecords` will be ignored (i.e. the set of record IDs to include will be solely determined by `getIPSSIDs`).
#### `transferPSOMToIPSS.py`
Transfer data from the REDCap project PSOM V2 into IPSS V4.
### Helper scripts in `ipss`
* `dataPackageExample.yml` - example YAML configuration file for the `makeDataPackage.py` script.
* `getIPSSIDs.py` - tool which generates a list of record IDs satisfying user-defined conditions based on data in IPSS-associated projects. This function first generates a list of all records in the project specified in the `from_code_name` argument, which must be defined in the user's `api_keys.yml` file. It then removes records from the list using specific exclusion criteria based on data stored in various IPSS-associated projects.

  Note that exclusions are generally based on existing data in a project, so the user should ensure that the list of IDs is being filtered using data which exists for all IDs in the list. For example, suppose we start with the list of IDs `[1, 2, 3]`. We want to exclude IDs with `sex=1` in the project `example_project`. If ID `3` does not exist in `example_project`, it will not be excluded by the filter regardless of the patient's sex. Usually, the exclusions should be based on fields that exist in the project specified in the `from_code_name`.
### Old scripts in `ipss`
* `combineDates_sips_final.py` - date-matching tool used in creation of a data package for the SIPS study
* `combineDates_sips_final_exact.py` - date-matching tool used in creation of a data package for the SIPS study
* `ids_mod_from_arch.py` - used in generation of an old data package
* `ids_mod_from_arch.txt` - used in generation of an old data package
* `ipss_conf_2019_enrollment_report.py` - generates reports on patient enrolment and REDCap users. This has been replaced by `enrollmentReportIPSS.py'
* `ipss_conf_2019_var_completion_report.py` - generates reports on patient enrolment and REDCap users. This has been replaced by `enrollmentReportIPSS.py'
* `ipss_conf_20200211_enrollment_report.py` - generates reports on patient enrolment and REDCap users. This has been replaced by `enrollmentReportIPSS.py'
* `makeDataPackage_2019.py` - generates an old data package
* `makeEegDataPackage_garbage.py` - generates an old data package
* `sips_both_groups.txt` - used in generation of an old data package
