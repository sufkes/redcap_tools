import os
import warnings
import json
import argparse

class ApiSettings(object):
    def __init__(self):
        # Always look in <installation directory>/settings.json for the user's settings file.
        self.settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'settings.json'))

        # The settings template path is <installation directory>/settings_templte.json. This is only used for getting the settings fields if the user's settings.json file does not yet exist.
        self.settings_template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'settings_template.json'))

        # Read the settings.json file once, and use that information to map project code names to API URLs and tokens.
        self.settings = self.readSettings()

    def readSettings(self):
        """
Reads file at <installation directory>/settings.json

Returns
-------
    settings : dict
        The settings.json file converted to a dict.
"""
        # Verify that the settings.json file exists
        if (not os.path.exists(self.settings_path)):
            warnings.warn("Settings file not found at path '"+self.settings_path+"'. Copy the file <installation directory>/settings_template.json, to <installation directory>/settings.json and enter appropatiate values in settings.json.")

            # If no settings.json file exists in the installation directory, set the values of the settings fields to None, but set the default API url to that stored in settings_template.json.
            with open(self.settings_template_path) as handle:
                settings = json.load(handle)
                for key in settings.keys():
                    if (key != 'default_api_url'):
                        settings[key] = None
        else:
            with open(self.settings_path) as handle:
                settings = json.load(handle)
    
        return settings

    def addApiArgs(self, parser):
        """
Add arguments for API URL, API token, and the code name of a project specified in a users api_keys.json file, which is used to retreive the API URL and token.

Parameters
----------
parser : argparse.ArgumentParser object
    The ArgumentParser to which the options will be added.

Returns
-------
parser : argparse.ArgumentParser object
    The ArumentParser after adding the three arguments.
"""
        # Read the users settings.json file.
        default_api_url = self.settings['default_api_url']
    
        # Must provide either the project codename or the API key, not both.
        project_id_group = parser.add_mutually_exclusive_group(required=True)
        project_id_group.add_argument("-n", "--code_name", help="Code name of project in users api_keys.json file.")
        project_id_group.add_argument("-k", "--api_key", help="API token of the project from which you wish to export data")

        # API URL argument
        parser.add_argument("-u", "--api_url", help="API URL. Default: '"+str(default_api_url)+"'", default=default_api_url)
        return parser

    def getApiCredentials(self, api_url=None, api_key=None, code_name=None, api_key_path=None):
        ## Get settings
        if (api_key_path is None):
            api_key_path = self.settings['api_key_path']
        
        ## Check for input errors.
        # Raise error if neither an API token nor a project ID were specified.
        if ((api_key is None) and (code_name is None)):
            raise ValueError('Must specify either an API token or a project ID.')
    
        # Raise error if user specified both an API token and and project ID.
        if ((not api_key is None) and (not code_name is None)):
            raise ValueError('Must specify either an API token or a project ID, not both.')
    
        # Raise error if user specified an API key and no API URL.
        if ((not api_key is None) and (api_url is None)):
            raise ValueError('If an API key is specified, must also specify an API URL.')
    
        # If user specifed an API URL and token, simply return them
        if ((not api_key is None) and (not api_url is None)):
            return api_url, api_key
        
        # If user specifed a project ID, attempt to retreive the API URL and token from file.
        if ((not code_name is None) and (api_key_path is None)):
            raise ValueError("If a project ID is specified, must also specify a path to a json file which maps project IDs to API URLS and tokens. See the example in '"+os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'redcap_directory_template', 'api_keys.json'))+"'")

        if ((not code_name is None) and (not api_key_path is None)):
            if (not os.path.exists(api_key_path)):
                raise ValueError("Path to API keys file does not exist: '"+api_key_path+"'")
            with open(api_key_path) as handle:
                api_map = json.load(handle)
            try:
                api_url = api_map[code_name]['url']
                api_key = api_map[code_name]['key']
            except KeyError:
                raise KeyError("Error: Code name '"+code_name+"' does not appear in '"+api_key_path+"'.")
            return api_url, api_key
