
# Standard modules
import os
import warnings
import yaml

# Non-standard modules
import redcap # PyCap

# My modules from current directory
#from getEventIDs import getEventIDs # REDCAP API APPARENTLY DOESN'T EXPORT event_id; THIS FUNCTION IS A MAPPING BETWEEN EVENT NAMES AND event_id's
from exportProjectInfo import exportProjectInfo
from ApiSettings import ApiSettings

def getEvents(api_url, api_key, event_ids_path=None, quiet=False):

    # Get project information
    project = redcap.Project(api_url, api_key)
    project_info = exportProjectInfo(api_url, api_key)
    project_longitudinal = bool(project_info["is_longitudinal"])
    
    if project_longitudinal:
        # Read the mapping from event name to event IDs at the path indicated in settings.yml
        api_settings = ApiSettings()
        api_url, api_key, code_name = api_settings.getApiCredentials(api_url=api_url, api_key=api_key) # code_name will be None if the entry does not exist in api_keys.yml
        if (event_ids_path is None): # if a path to an event IDs map yaml file was specified explicitly, use that instead of the path specified in settings.yml
            event_ids_path = api_settings.settings['event_ids_path']
        if (not os.path.exists(event_ids_path)):
            if (not quiet):
                warnings.warn("Path to event ID map does not exist: '"+event_ids_path+"'")
            event_ids_map = {}
        elif (code_name is None):
            event_ids_map = {}
        else:
            with open(event_ids_path, 'r') as handle:
                event_ids_map_all = yaml.load(handle, Loader=yaml.SafeLoader)

                # Convert the event_ids to strings.
                for ii, event_ids_map in event_ids_map_all.iteritems():
                    if (not event_ids_map is None):
                        event_ids_map_all[ii] = {k:str(v) for k,v in event_ids_map.iteritems()}
            try:
                event_ids_map = event_ids_map_all[code_name]
            except KeyError: # if project_code name does not have an entry in event_ids.yml
                if (not quiet):
                    warnings.warn("code_name '"+code_name+"' is not an entry in '"+event_ids_path+"'")
                event_ids_map = {}
        
        events = {} # dict with unique_event_name as keys. Items include the 'pretty' event name.

        pycap_events = project.events # Includes days_offset, custom_event_label etc. So far only want unique_event_name
        for pycap_event_index in range(len(pycap_events)):
            pycap_event = pycap_events[pycap_event_index]
#            pycap_events[pycap_event_index] = pycap_event["unique_event_name"]
            events[pycap_event["unique_event_name"]] = {}
            events[pycap_event["unique_event_name"]]["day_offset"] = pycap_event["day_offset"]
            events[pycap_event["unique_event_name"]]["custom_event_label"] = pycap_event["custom_event_label"]
            events[pycap_event["unique_event_name"]]["event_name"] = pycap_event["event_name"]
            events[pycap_event["unique_event_name"]]["arm_num"] = pycap_event["arm_num"]
            events[pycap_event["unique_event_name"]]["offset_min"] = pycap_event["offset_min"]
            events[pycap_event["unique_event_name"]]["offset_max"] = pycap_event["offset_max"]

#            events[pycap_event["unique_event_name"]]["event_id"] = getEventIDs(api_url, api_key, pycap_event["unique_event_name"]) # NOT SURE HOW TO GET THIS INFORMATION AUTOMATICALLY.
            if (event_ids_map != {}):
                try:
                    event_id = event_ids_map[pycap_event["unique_event_name"]] 
                except KeyError:
                    if (not quiet):
                        warnings.warn("Event named '"+pycap_event["unique_event_name"]+"' not found in '"+event_ids_path+"'")
                    event_id = None
            else:
                event_id = None
            events[pycap_event["unique_event_name"]]["event_id"] = event_id
    else:
        events = None
    return events

