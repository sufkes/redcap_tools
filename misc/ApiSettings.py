#!/usr/bin/env python

import os, sys
import warnings
import yaml
import argparse

class ApiSettings(object):
    def __init__(self):
        # Always look in <installation directory>/settings.yml for the user's settings file.
        self.settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'settings.yml'))

        # The settings template path is <installation directory>/settings_template.yml. This is only used for getting the settings fields if the user's settings.yml file does not yet exist.
        self.settings_template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'settings_template.yml'))

        # Read the settings.yml file once, and use that information to map project code names to API URLs and tokens.
        self.settings = self.readSettings()

    def readSettings(self):
        """
Reads file at <installation directory>/settings.yml

Returns
-------
    settings : dict
        The settings.yml file converted to a dict.
"""
        # Verify that the settings.yml file exists
        if (self.settings_path is None) or (not os.path.exists(self.settings_path)):
            warnings.warn("Settings file not found at path '"+str(self.settings_path)+"'. Copy the file <installation directory>/settings_template.yml, to <installation directory>/settings.yml and enter appropatiate values in settings.yml.")

            # If no settings.yml file exists in the installation directory, set the values of the settings fields to None, but set the default API URL to that stored in settings_template.yml.
            with open(self.settings_template_path, 'r') as handle:
                settings = yaml.load(handle, Loader=yaml.SafeLoader)
                for key in settings.keys():
                    if (key != 'default_api_url'):
                        settings[key] = None
        else:
            with open(self.settings_path, 'r') as handle:
                settings = yaml.load(handle, Loader=yaml.SafeLoader)
    
        return settings

    def addApiArgs(self, parser, num_projects=1):
        """
Add arguments for API URL, API token, and the code name of a project specified in a users api_keys.yml file, which is used to retreive the API URL and token.

Parameters
----------
parser : argparse.ArgumentParser object
    The ArgumentParser to which the options will be added.
num_projects : int
    If num_projects>1, separate arguments will be added for each project. E.g. if num_projects=2, arguments '-n1 --code_name1' and '-n2 --code_name2' will be added.

Returns
-------
parser : argparse.ArgumentParser object
    The ArumentParser after adding the three arguments.
"""
        # Read the users settings.yml file.
        default_api_url = self.settings['default_api_url']
    
        # Must provide either the project codename or the API key, not both.
        project_id_group = parser.add_mutually_exclusive_group(required=True)

        if (num_projects == 1):
            project_id_group.add_argument("-n", "--code_name", help="Code name of project in user's api_keys.yml file.")
            project_id_group.add_argument("-k", "--api_key", help="API token of the project")

            # API URL argument
            parser.add_argument("-u", "--api_url", help="API URL of project. Default: '"+str(default_api_url)+"'", default=default_api_url)
        elif (num_projects > 1):
            project_id_group.add_argument("-n", "--code_names", help="Code names of projects in user's api_keys.yml file.", nargs=num_projects, metavar='CODE_NAME', default=[None]*num_projects)
            project_id_group.add_argument("-k", "--api_keys", help="API tokens of the projects", nargs=num_projects, metavar='API_KEY', default=[None]*num_projects)

            # API URL argument
            parser.add_argument("-u", "--api_urls", help="API URLs of projects. Default: '"+str(default_api_url)+"'", default=[default_api_url]*num_projects, nargs=num_projects, metavar='API_URL')
        else:
            raise ValueError("num_projects must be an integer greater than 0")
        return parser

    def getApiCredentials(self, api_url=None, api_key=None, code_name=None, api_key_path=None):
        ## Get settings
        # If a custom api_key_path was not specified, use the path stored in settings.yml
        if (api_key_path is None):
            api_key_path = self.settings['api_key_path']
        
        ## Check for input errors.
        # Raise error if neither an API token nor a project ID were specified.
        if ((api_key is None) and (code_name is None)):
            raise Exception('Must specify either an API token or a project ID.')
    
        # Raise error if user specified both an API token and and project ID.
        if ((not api_key is None) and (not code_name is None)):
            raise Exception('Must specify either an API token or a project ID, not both.')
    
        # Raise error if user specified an API key and no API URL.
        if ((not api_key is None) and (api_url is None)):
            raise Exception('If an API key is specified, must also specify an API URL.')
    
        # If user specifed an API URL and token, find the code name for the project, if it exists.
        msg_api_key_path_not_found = "Path to API keys file does not exist: '"+str(api_key_path)+"'"
        msg_code_name_not_found = "Code name corresponding to input (API URL, API token) not found in '"+str(api_key_path)+"'. Returning code_name=None"
        if ((not api_key is None) and (not api_url is None)):
            if (api_key_path is None) or (not os.path.exists(api_key_path)):
                warnings.warn(msg_api_key_path_not_found)
                code_name = None
                return api_url, api_key, code_name
            else:
                with open(api_key_path, 'r') as handle:
                    api_map = yaml.load(handle, Loader=yaml.SafeLoader)
                for code_name_from_map, entry in api_map.iteritems():
                    if ((entry['url'] == api_url) and (entry['key'] == api_key)):
                        return api_url, api_key, code_name_from_map
                # If code_name was not found in map, set it to None and return.
                warnings.warn(msg_code_name_not_found)
                code_name = None
                return api_url, api_key, code_name
                    
        # If user specifed a project code_name defined in their api_key.yml file, attempt to retreive the API URL and token from file.
        if ((not code_name is None) and (api_key_path is None)):
            raise Exception("If a project ID is specified, must also specify a path to a YAML file which maps project IDs to API URLS and tokens. See the example in '"+os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'redcap_directory_template', 'api_keys.yml'))+"'")

        if ((not code_name is None) and (not api_key_path is None)):
            if (not os.path.exists(api_key_path)):
                raise Exception(msg_api_key_path_not_found)
            with open(api_key_path, 'r') as handle:
                api_map = yaml.load(handle, Loader=yaml.SafeLoader)
            try:
                api_url = api_map[code_name]['url']
                api_key = api_map[code_name]['key']
            except KeyError:
                raise Exception("Code name '"+str(code_name)+"' does not appear in '"+str(api_key_path)+"'.")

            return api_url, api_key, code_name

        
if (__name__ == '__main__'):
    # If called directly, print the API URL and key associated with the input arguments
    api_settings = ApiSettings()
    print api_settings.settings
    code_name_list = sys.argv[1:]
    for code_name in code_name_list:
        api_url, api_key, code_name_ret = api_settings.getApiCredentials(code_name=code_name)
        print "code name: "+str(code_name)
        print "code_name: "+str(code_name_ret)
        print "API URL  : "+str(api_url)
        print "API token: "+str(api_key)
