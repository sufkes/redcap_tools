#!/usr/bin/env python


# Standard modules
import os
import sys
import argparse
import yaml # this might need to be installed?
from pprint import pprint
from StringIO import StringIO
import warnings

# Non-standard modules
import pandas
import redcap # PyCap

# My modules from current directory
from getIPSSIDs import getIPSSIDs

# My modules from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import misc
from misc.ApiSettings import ApiSettings
from misc.exportRecords import exportRecords
from misc.exportProjectInfo import exportProjectInfo
from misc.getEvents import getEvents
from misc.exportFormEventMapping import exportFormEventMapping
from misc.exportRepeatingFormsEvents import exportRepeatingFormsEvents
from misc.exportFormsOrdered import exportFormsOrdered
from misc.createFormRepetitionMap import createFormRepetitionMap
from misc.parseMetadata import parseMetadata
from misc.Timer import Timer

#### Set default formatting options. The default options will be used for all projects except those projects which override them in the YAML configuration file.
format_options_defaults = {
    "split_type":"none"
}


#### Read configuration.
## Read YAML configuration file.
def readConfig(config_path):
    """
    Read YAML configuration file

    Parameters
    ----------
    config_path : str
        path to YAML configuration file
    
    Returns
    -------
    config : dict
        configuration for data data package
    """
    
    with open(args.config_path, "r") as handle:
        config = yaml.load(handle, Loader=yaml.SafeLoader)
    
    ## Verify that YAML file has the required entries and format.
    # Required format for YAML file:
    #options:
    #  file_split_type: none, projects, or chunks
    #  out_dir: any string
    #projects:
    #  - code_name: [code name of a project in user's API keys file]
    #    options:
    #      split_type: none, events_only, repeat_forms_events, all_forms_events
    #      use_getIPSSIDs: True, False
    #    exportRecords_args:         
    #    getIPSSIDs_args:       <- optional; required if use_getIPSSIDs is True for this project.
    #  - code_name: [code name of a project in user's API keys file]
    #  ...
    
    required_keys = ["options", "projects"]
    for key in required_keys:
        if (not key in config):
            raise Exception("YAML configuration file is missing required key: '"+str(key)+"'")
    required_options_keys = ["file_split_type", "out_dir"]
    for key in required_options_keys:
        if (not key in config["options"]):
            raise Exception("YAML configuration file 'options' key is missing required key: '"+str(key)+"'")
    allowed_options_file_split_types = ["none", "projects", "chunks"]
    if (not config["options"]["file_split_type"] in allowed_options_file_split_types):
        raise Exception("YAML configuration file 'options' key has invalid 'file_split_type'. Choose from: "+str(allowed_options_file_split_types))
    required_project_keys = ["code_name", "options"]
    for key in required_project_keys:
        for project in config["projects"]:
            if (not key in project):
                raise Exception("In YAML configuration file, project is missing required key: '"+key+"'")
    required_project_options_keys = ["split_type", "use_getIPSSIDs"]
    for key in required_project_options_keys:
        for project in config["projects"]:
            code_name = project["code_name"]
            if (not key in project["options"]):
                raise Exception("YAML configuration file, project '"+code_name+"' is missing required key: '"+key+"'")
    allowed_project_options_split_types = ["none", "events_only", "repeat_forms_events", "all_forms_events"]
    for project in config["projects"]:
        if (not project["options"]["split_type"] in allowed_project_options_split_types):
            raise Exception("YAML configuration file, project '"+code_name+"' has an invalid split type. Choose from "+str(allowed_project_options_split_types))

    return config

def buildProjects(config):
    #### Read user's settings.yml file, which will be used to get API tokens and URLs.
    api_settings = ApiSettings()
    
    ## Build a list of "projects" - dicts which store data and settings for the project.
    projects = config["projects"]
    
    ## Verify the settings for each project.
    for project in projects:
        code_name = project["code_name"]

        # Get args to pass to exportRecords.
        if (not "exportRecords_args" in project) or (project["exportRecords_args"] is None):
            project["exportRecords_args"] = {}

        # If use_getIPSSIDs is True, get list of record IDs to export.
        if project["options"]["use_getIPSSIDs"]:
            # If use_getIPSSIDs is True, but no options provided, raise warning.
            if (not "getIPSSIDs_args" in project) or (project["getIPSSIDs_args"] is None):
                print "Warning: in project '"+code_name+"', 'use_getIPSSIDs' is True, but 'getIPSSIDs_args' not provided for project. Exporting all record IDs from project."
                record_id_list = None
            else:
                getIPSSIDs_args = project["getIPSSIDs_args"]
                record_id_list = getIPSSIDs(**getIPSSIDs_args)

            # If exportRecords_args has an entry for record_id_list, but use_getIPSSIDs is True, raise warning.
            if (project["options"]["use_getIPSSIDs"]) and ("record_id_list" in project["exportRecords_args"]):
                print "Warning: in project '"+code_name+"', the specified 'record_id_list' will be ignored, since 'use_getIPSSIDs' is True."

            # Overwrite the record_id_list argument in exportRecords_args
            project["exportRecords_args"]["record_id_list"] = record_id_list
                
        ## Get args to pass to exportRecords. If key does not exist, or it is not set to a value, set it to an empty dict (i.e. 
        exportRecords_args = project["exportRecords_args"] # has a value (possibly {}).

        # Convert exportRecords_args arguments to strings as needed.
        convert_to_strings = ["fields", "forms", "events", "record_id_list"]
        for arg in convert_to_strings:
            if arg in exportRecords_args.keys():
                if (exportRecords_args[arg] == 'None'): # these arguments could be lists or None
                    # Convert string 'None' to Python None.
                    exportRecords_args[arg] = None
                else: 
                    # Convert list to list of strings. Currently, list might contain integers etc.
                    new_list = [str(val) for val in exportRecords_args[arg]]
                    exportRecords_args[arg] = new_list
        

        ## Get API credentials for current project.
        api_url, api_key, code_name = api_settings.getApiCredentials(code_name=code_name)
        project["api_url"] = api_url
        project["api_key"] = api_key

        
        ## Export requested data for current project        
        data_csv = exportRecords(api_url, api_key, format="csv", **exportRecords_args)
        data_csv_file = StringIO(data_csv)
        data_df = pandas.read_csv(data_csv_file, dtype=unicode, encoding='utf-8').fillna('')

        project["chunks"] = [data_df] # this list of dataframes will be broken into pieces, each piece containing data to be placed in a different tab.

        ## Retrieve project settings and add them to the dict for the current project
        pycap_project = redcap.Project(api_url, api_key)
        def_field = pycap_project.def_field
        project_info = exportProjectInfo(api_url, api_key)
        longitudinal = bool(project_info["is_longitudinal"])
        repeating = bool(project_info["has_repeating_instruments_or_events"])
        events = getEvents(api_url, api_key, quiet=True)
        metadata_raw = pycap_project.export_metadata()
        form_event_mapping = exportFormEventMapping(pycap_project, longitudinal)
        repeating_forms_events = exportRepeatingFormsEvents(api_url, api_key, repeating)
        forms = exportFormsOrdered(api_url, api_key)
        form_repetition_map = createFormRepetitionMap(longitudinal, repeating, form_event_mapping, repeating_forms_events, forms)
        metadata = parseMetadata(pycap_project.def_field, project_info, longitudinal, repeating, events, metadata_raw, form_event_mapping, repeating_forms_events, forms, form_repetition_map, write_branching_logic_function=False)

        project["pycap_project"] = pycap_project
        project["def_field"] = def_field
        project["project_info"] = project_info
        project["longitudinal"] = longitudinal
        project["repeating"] = repeating
        project["events"] = events
        project["form_event_mapping"] = form_event_mapping
        project["repeating_forms_events"] = repeating_forms_events
        project["forms"] = forms
        project["form_repetition_map"] = form_repetition_map
        project["metadata"] = metadata
    
        # Create dict which maps each form to a list of events containing that form.
        if longitudinal:
            form_to_events_dict = {}
            for form_event_entry in form_event_mapping:
                form = form_event_entry['form']
                event = form_event_entry['unique_event_name']
                if (not form in form_to_events_dict):
                    form_to_events_dict[form] = [event]
                else:
                    form_to_events_dict[form].append(event)
        else:
            form_to_events_dict = None    
        project["form_to_events_dict"] = form_to_events_dict
        
        ## Build lists of variables which appear in the export data.
        # columns which uniquely identify a row
        primary_key = [def_field]
        if project["longitudinal"]:
            primary_key.append("redcap_event_name")
        if project["repeating"]:
            primary_key.append("redcap_repeat_instrument")
            primary_key.append("redcap_repeat_instance")
        project["primary_key"] = primary_key
    
        primary_key_and_dag = primary_key
        if ("redcap_data_access_group" in data_df.columns):
            primary_key_and_dag.append("redcap_data_access_group")
        project["primary_key_and_dag"] = primary_key_and_dag
        
        # form_complete fields
        form_complete_fields = [field for field in data_df.columns if ((field.endswith("_complete")) and (not field in metadata) and (not field in primary_key) and (not field=="redcap_data_access_group"))]
        project["form_complete_fields"] = form_complete_fields
    
        # data fields
        data_fields = [field for field in data_df.columns if ((not field in primary_key+form_complete_fields) and (not field=="redcap_data_access_group"))]
        project["data_fields"] = data_fields
    
    return projects    
    
                
#### Split the data into chunks based on project-specific arguments
## Define function for splitting chunks based on instrument.
def splitForms(project):
    """Separate project["chunks"] such that the fields in each new chunk belong to a single form. Do not split on rows or remove any rows."""
    # Initialize a list to store the new data chunks.
    new_chunks = []

    # Split chunks such that each new chunk only contains fields from a single form.
    for chunk in project["chunks"]:
        # Generate a list of all forms to which fields in the current chunk belong.
        forms = []
        for field in chunk.columns:
            if (field in project["primary_key_and_dag"]):
                continue
            elif (field in project["form_complete_fields"]):
                form = field.rstrip("_complete")
            elif (field in project["data_fields"]):
                form = project["metadata"][field].form_name
            if (not form in forms):
                forms.append(form)

        # Split current chunk 
        if (len(forms) == 1):
            new_chunks.append(chunk) # change nothing if all forms in current chunk belong to a single form.
        else:
            for new_chunk_form in forms:
                fields_to_include = []
                for field in chunk.columns:
                    if (field in project["primary_key_and_dag"]):
                        # If field is in the primary key or is the DAG field, include it.
                        fields_to_include.append(field)
                        continue
                    elif (field in project["form_complete_fields"]):
                        form = field.rstrip("_complete")
                    elif (field in project["data_fields"]):
                        form = project["metadata"][field].form_name
                    if (form == new_chunk_form):
                        # If the field belongs to the current new chunk's form, inlcude it.
                        fields_to_include.append(field)
                new_chunks.append(chunk[fields_to_include])
    project["chunks"] = new_chunks
    return project

# Define function for splitting chunks such that each contains data from only one instrument, with no invalid rows. NOT SUPPORTED YET.
def splitFormsOnly(project):
    print warnings.warn("This splitting method is not currently supported.")
    return project

## Define function for splitting chunks by redcap_event_name column.
def splitEvents(project):
    """Separate project["chunks"] such that each new chunk has a single value for redcap_event_name"""
    if project["longitudinal"]: # if not longitudinal, nothing to be done.
        # Initialize list to store the new data chunks.
        new_chunks = []

        # Split rows according to redcap_event_name.
        for chunk in project["chunks"]:
            event_vals = chunk["redcap_event_name"].unique()
            for event_val in event_vals:
                new_chunk = chunk.loc[(chunk["redcap_event_name"] == event_val), :]
                new_chunks.append(new_chunk)

        # Remove columns not part of chunk's event.
        for ii in range(len(new_chunks)):
            new_chunk = new_chunks[ii]
            fields_to_include = []
            event_val = new_chunk["redcap_event_name"].unique()[0] # Should only contain a single value.
            for field in new_chunk.columns:
                if (field in project["primary_key_and_dag"]):
                    # Always inlcude these fields.
                    fields_to_include.append(field)
                elif (field in project["form_complete_fields"]):
                    # Include if associated form is part of event.
                    form = field.rstrip("_complete")
                    if (event_val in project["form_to_events_dict"][form]):
                        fields_to_include.append(field)
                elif (field in project["data_fields"]):
                    # Include if field is part of event.
                    if (event_val in project["metadata"][field].events_containing_field):
                        fields_to_include.append(field)
            new_chunks[ii] = new_chunk[fields_to_include]
        project["chunks"] = new_chunks
    return project

## Define function for splitting chunks by redcap_repeat_instrument column.
def splitRepeatForms(project):
    """Separate project["chunks"] such that each new chunk has a single value for redcap_repeat_instrument. Assumes that the input project["chunks"] each have only a single value for redcap_repeat_instance."""
    if project["repeating"]: # If project does not have repeating instruments or events, nothing to do.
        # Initialize list to store the new data chunks.
        new_chunks = []
        
        # Split rows according to redcap_repeat_instrument.
        for chunk in project["chunks"]:
            rpt_form_vals = chunk["redcap_repeat_instrument"].unique()
            for rpt_form_val in rpt_form_vals:
                new_chunk = chunk.loc[(chunk["redcap_repeat_instrument"] == rpt_form_val), :]
                new_chunks.append(new_chunk)

        # Remove columns not part of chunk's (event, repeat_instrument) pair
        for ii in range(len(new_chunks)):
            new_chunk = new_chunks[ii]
            fields_to_include = []
            rpt_form_val = new_chunk["redcap_repeat_instrument"].unique()[0] # can be empty string
            
            ## Build list of fields to include in current chunk.
            for field in new_chunk.columns:
                # If the current field is in the primary key, or is the DAG field, include it.
                if (field in project["primary_key_and_dag"]):
                    fields_to_include.append(field)
                    continue
                
                # Determine which form the current field is in.
                if (field in project["data_fields"]):
                    form = project["metadata"][field].form_name
                elif (field in project["form_complete_fields"]):
                    form = field.rstrip("_complete")

                # Determine whether to include the current field.
                if (rpt_form_val != ''): # if chunk contains repeating forms
                    # Include if field is part of this chunk's repeating form.
                    if (form == rpt_form_val):
                        fields_to_include.append(field)
                else: # if chunk contains non-repeating data, or a repeating event
                    if (not project["longitudinal"]):
                        # Include if form containing field is non-repeating.
                        if project["form_repetition_map"][form]["non_repeat"]:
                            fields_to_include.append(field)
                    else: # if project is longitudinal and repeating
                        # Determine whether chunk contains data for a repeating event.
                        rpt_instance_vals = new_chunk["redcap_repeat_instance"].tolist() # should either contain only blanks, or else '1', '2', '3' ...
                        assert (not (('' in rpt_instance_vals) and ('1' in rpt_instance_vals))) # non-functional sanity check
                        if (rpt_instance_vals[0] == ''): # if chunk contains non-repeating data for the current event.
                            # Include if form containing field is non-repeating in the chunk's event.
                            event_val = new_chunk["redcap_event_name"].tolist()[0]
                            if (event_val in project["form_repetition_map"][form]["events_non_repeat"]):
                                fields_to_include.append(field)
                        else: # if chunk contains data for a repeating event (repeat_instrument=='' and repeat_instance!='')
                            # Include, because all fields in this chunk are guaranteed to be part of the chunks event, and all fields in a repeating event are repeating.
                            fields_to_include.append(field)
            new_chunks[ii] = new_chunk[fields_to_include] # remove all excluded columns
        project["chunks"] = new_chunks
    return project

#### Define main function for splitting the data into chunks.
def splitData(config, projects):
    for project in projects:
        code_name = project["code_name"]
        if (project["options"]["split_type"] == "none"):
            continue
        elif (project["options"]["split_type"] == "forms_only"):
            print "Warning: This split_type setting is not currently supported. Choose another."
            project = splitFormsOnly(project)
        elif (project["options"]["split_type"] in ["events_only", "repeat_forms_events", "all_forms_events"]):
            ## Split rows on redcap_event_name.
            project = splitEvents(project)
            
            if (project["options"]["split_type"] in ["repeat_forms_events", "all_forms_events"]):
                ## Split rows on redcap_repeat_instrument.
                project = splitRepeatForms(project)
                
            if (project["options"]["split_type"] == "all_forms_events"):
                ## Split columns where redcap_repeat_instrument is blank.
                project = splitForms(project)
    return projects

#### Define function for saving the data.
def saveData(config, projects):
    #### Save the chunks in Excel file(s).
    out_dir = config["options"]["out_dir"]
    ## If not splitting project data into separate files, initialize XLSX file.
    if (config["options"]["file_split_type"] == "none"):
        # Choose path to save file to.
        file_name = "all_projects.xlsx"
        out_path = os.path.join(out_dir, file_name)

        # Initialize writer.
        writer = pandas.ExcelWriter(out_path, engine='xlsxwriter')
    for project in projects:
        code_name = project["code_name"]
        ## If saving all data for a given project in one file, intialize XLSX file.
        if (config["options"]["file_split_type"] == "projects"):
            # Choose path to save file to.
            file_name = code_name+".xlsx"
            out_path = os.path.join(out_dir, file_name)

            # Initialize writer.
            writer = pandas.ExcelWriter(out_path, engine='xlsxwriter')
        
        ## Save each data chunk as a tab in an XLSX file, or a separate file.
        chunk_number = 1
        t_write_chunks = Timer("Adding chunks to package")
        for chunk in project["chunks"]:
            ## Add chunk to appropriate location.
            if (config["options"]["file_split_type"] == "none"):
                # Add chunk to the single XLSX file containing all data.
                sheet_name = code_name+"_chunk"+str(chunk_number)
                chunk.to_excel(writer, sheet_name=sheet_name, index=False, encoding='utf-8')
            elif (config["options"]["file_split_type"] == "projects"):
                # Add chunk to the XLSX file for the current project.
                sheet_name = "chunk"+str(chunk_number)
                chunk.to_excel(writer, sheet_name=sheet_name, index=False, encoding='utf-8')
            elif (config["options"]["file_split_type"] == "chunks"):
                ## Save chunk to a separate XLSX file.
                # Choose path to save file to.
                file_name = code_name+"_chunk"+str(chunk_number)+".xlsx"
                out_path = os.path.join(out_dir, file_name)

                # Save file.
                writer = pandas.ExcelWriter(out_path, engine='xlsxwriter')
                chunk.to_excel(writer, index=False, encoding='utf-8')
                writer.close()
    
            chunk_number += 1
            print chunk_number
        t_write_chunks.stop()

        if (config["options"]["file_split_type"] == "projects"):
            
            # Save and close the XLSX, which now has a tab for each chunk.
            writer.close()
    if (config["options"]["file_split_type"] == "none"):
        
        # Save and close the XLSX, which now has a tab for each chunk.
        t_save = Timer("Saving data package to file")
        writer.close()
        t_save.stop()
    

def makeDataPackage(config_path):
    # Read the configuration file.
    t_readConfig = Timer("Running readConfig")
    config = readConfig(config_path)
    t_readConfig.stop()
    
    # Build the list of projects, containing data and format settings.
    t_buildProjects = Timer("Running buildProjects")
    projects = buildProjects(config)
    t_buildProjects.stop()
    
    # Split the data into pieces for each project.
    t_splitData = Timer("Running splitData")
    projects = splitData(config, projects)
    t_splitData.stop()
    
    # Save the data package.
    t_saveData= Timer("Running saveData")
    saveData(config, projects)
    t_saveData.stop()
        
## Use script from command line.
if (__name__ == "__main__"):    
    #### Parse command-line arguments.
    ## Create argument parser
    description = "Create data package using settings specified in YAML configuration file."
    parser = argparse.ArgumentParser(description=description)
    
    ## Define positional arguments.
    parser.add_argument("config_path", help="path to YAML configuration file.")
    
    ## Parse arguments.
    args = parser.parse_args()

    ## Make the data package
    makeDataPackage(args.config_path)
