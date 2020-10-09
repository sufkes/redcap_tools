# sufkes_redcap
Scripts for REDCap API functions, quality control, report generation, and special-purpose scripts for the Stroke team at SickKids.

# Getting started
## Installation
All scripts require Python 2.7.

Most of the scripts require the Python module "PyCap". See https://github.com/redcap-tools/PyCap

PyCap requires the module "requests". See https://pypi.org/project/requests

Some scripts require the Python module "pyyaml". See https://pypi.org/project/PyYAML

Some scripts require the Python module "Pandas". See https://pandas.pydata.org/pandas-docs/stable/install.html
## Configuring settings.yml and api_keys.yml.
Most scripts use REDCap API functions. To interact with a REDCap project through the API, a user must have API rights (set in the User Rights tab of the REDCap project) and an API token. Users can then interact with the project using their API token and the API URL for the project. The API URL for a project can be found in the API Playground of the project. The API URLs for the REDCap instances at SickKids are:
| Instance | API URL |
|-|-|
| External | https://redcapexternal.research.sickkids.ca/api/ |
| Internal | https://redcapinternal.research.sickkids.ca/api/ |
| Internal Survey | https://staffsurveys.sickkids.ca/api/ |

Most scripts allow the user to specify an API token and URL as arguments. To
