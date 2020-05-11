import os
import sys
import yaml

def readConfig(config_path):
    """Verify that the configuration file passed to the intra-project check script is valid."""

    # Open the config file.
    with open(config_path, 'r') as handle:
        config = yaml.load(handle, Loader=yaml.SafeLoader)

    # Verify that the required options are set.
    required_keys = ["out_dir", "code_name", "checks", "use_custom_record_id_list", "use_getIPSSIDs"]
    for key in required_keys:
        if (not key in config):
            raise Exception("YAML configuration file is missing required key: '"+str(key)+"'")

#    # Ensure that all specified check scripts exist.
#    for check in config["checks"]:
#        if (not os.path.exists(check+".py")):
#            raise Exception("Python script for check specified in YAML configuration file does not exist: "+str(check)+".py")
        
    ## Ensure that the options for checking specific IDs are set correctly.
    # Cannot set both use_custom_record_id_list use_getIPSSIDs to True.
    if ("use_custom_record_id_list" in config) and (config["use_custom_record_id_list"] is True) and ("use_getIPSSIDs" in config) and (config["use_getIPSSIDs"] is True):
        raise Exception("In YAML configuration file, cannot set both 'use_custom_record_id_list' and 'use_getIPSSIDs' to True.")

    # If use_custom_record_id_list is True, must specify record_id_list.
    if ("use_custom_record_id_list" in config) and (config["use_custom_record_id_list"] is True):
        if (not "record_id_list" in config) or (config["record_id_list"] is None):
            msg = """In YAML configuration file, 'use_custom_record_id_list' is True, but 'record_id_list' is not specified. To check only specific IDs, add a YAML list of IDs under the entry 'record_id_list'. 

For example, to check the IDs "ID_1" and "ID_2", add the following to your configuration file:

use_custom_record_id_list: True
record_id_list:
  - ID_1
  - ID_2
"""
            raise Exception(msg)
        
    # If use_getIPSSIDs is True, must specify getIPSSIDs_args.
    if ("use_getIPSSIDs" in config) and (config["use_getIPSSIDs"] is True):
        if (not "getIPSSIDs_args" in config):
            msg="""In YAML configuration file, if 'use_getIPSSIDs' is True, you must specify 'getIPSSIDs_args'. The 'getIPSSIDs_args' section specifies the options to pass to the function getIPSSIDs(). 

For example, to get all IDs in IPSS V4 except registry-only patients, add the following to your configuration file:

use_getIPSSIDs: True
getIPSSIDs_args:
  from_code_name: ipss_v4
  ex_registry_only: True
"""
            raise Exception(msg)

    ## Interpret data types (most of the defaults are already correct).
    # If record_id_list specified, convert the record IDs to unicode. (already verified the list is not None)
    if ("record_id_list" in config):
        config["record_id_list"] = [str(ii) for ii in config["record_id_list"]]

    # If, for some reason, the user wants to use getIPSSIDs with default settings, convert the args from None to an empty dict.
    if (config["getIPSSIDs_args"] is None):
        config["getIPSSIDs_args"] = {}
    return config
