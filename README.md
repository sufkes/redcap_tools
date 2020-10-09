# sufkes_redcap
Scripts for REDCap API functions, quality control, report generation, and special-purpose scripts for the Stroke team at SickKids.

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

Most scripts allow the user to specify an API token and URL as arguments. To limit the need to retrieve passwords, a user can instead configure their settings.yml file and an api_keys.yml file so that API Tokens and URLs can be retrieved using a short, user-defined keyword ("code name"). To do this:
1. Create an `api_keys.yml` file. This is a YAML file which assigns a code name to each (API URL, API token) pair. An entry should be created for each project with which the user will interact. The `api_keys.yml` file can be saved in any safe location on your computer, but should not be readable to other users.

   Each entry must be of the form:
   ```
   my_code_name_for_this_project:
     url: <API URL for this project>
     key: <MY API token for this project>
   ```
   E.g.
   ```
   ipss_v4:
     url: https://redcapexternal.research.sickkids.ca/api/
     key: 1234567890ABCDEFGHIJKLMNOPQRSTUV
   ```
   Note that the URL and token must be indented from the code name using the same number of spaces, and tab characters must not be used.

   **Note for Stroke team:** This repository has a template `api_keys.yml` file, which has an entry for most projects associated with the Stroke team at SickKids. If you are using this repository in the Stroke team, simply copy that file to another location, and replace the API key entries with your own tokens. For consistency within the Stroke team, do not change the code names from the values used in the template.
2. Create a `settings.yml` file. This is a YAML file in which a user can specify defaults to be used in the functions in this repository. Create a copy of the `settings_template.yml`, name it `settings.yml`, and place it in the root directory of this repository (i.e. the directory in which the `settings_template.yml` file sits). Modify the values of the new `settings.yml` file, which will be used in scripts automatically.
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
   * (**Optional**) The `event_ids_path` can be set to the full path of the `event_ids.yml` file which sits in the root directory of this repository, or to the path of a user's own `event_ids.yml` file. The `event_ids.yml` file associates the human-readable event name defined in the REDCap (e.g. `acute_arm_1`), with the numeric code associated with that event which appears in the URL address for pages corresponding to that event (e.g. `34247`). This is *only* used in the quality control script. Its sole purpose enable automatic generation of REDCap links for specific record, instrument, and event name. This file must be updated for each project for which a user wishes to automatically generate links in the quality control script. Note that the code names used in this file must match the code names used in the the user's `api_keys.yml` file.

     **Note for Stroke team:** This file already contains entries for all REDCap projects associated with the Stroke team as of April 2020. You simply need to modify the `event_ids_path` entry in your `settings.yml` file to point to it.
   * (**Optional**) Set the `default_backups_dir`. This is the default directory to which project backups will be saved by backupProjects.py.
