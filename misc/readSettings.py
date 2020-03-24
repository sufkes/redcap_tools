#!/usr/bin/env python

import os
import json

def readSettings():
    """
Reads file at <sufkes_redcap installation directory>/settings.json

Returns
-------
    settings : dict
        The settings.json file converted to a dict.
"""
    settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'settings.json'))

    # Verify that the settings file exists.
    with open(settings_path) as handle:
        settings = json.load(handle)

    return settings


if (__name__ == '__main__'):
    settings = readSettings()
    print settings
        
