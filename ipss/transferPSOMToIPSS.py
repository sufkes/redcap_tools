#!/usr/bin/env python


######## MODIFY api_url_key_list_path TO POINT TO YOUR LIST OF API KEYS AND URLS (IF YOU WANT THE SCRIPT TO RUN WITHOUT ANY COMMAND LINE ARGUMENTS). ########
## THE FILE SHOULD BE TWO LINES OF TEXT (NOT INCLUDING THE #):
#PSOM_API_URL PSOM_API_KEY
#IPSS_API_URL IPSS_API_KEY
api_url_key_list_path = "/Users/steven ufkes/Documents/stroke/data_packages/api_url_key_list.txt"
######## ^ MODIFY ^ #########################################################################################################################################


#### Import modules
# Standard modules 
import os, sys
import argparse
import warnings

# My modules from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # this line makes the 'misc' folder available via 'import misc'
import misc
from misc.exportRecords import exportRecords
from misc.importRecords import importRecords
from misc.getRecordIDList import getRecordIDList
from misc.ApiSettings import ApiSettings

#### Define function which transfers data from PSOM V2 to IPSS V4.
def transferPSOMToIPSS(url_psom, key_psom, url_ipss, key_ipss, import_non_ipss_ids=False):
    """
    Transfer Summary of Impressions data from PSOM V2 to IPSS V4.
    Parameters:
        url_psom: str, API URL for PSOM V2
        key_psom: str, API key for PSOM V2
        url_ipss: str, API URL for IPSS V4
        key_ipss: str, API key for IPSS V4
    Returns:
        None
    """

    ## Define function which modifies PSOM data prior to import to IPSS.
    def modifyRecords(from_psom, url_ipss, key_ipss, import_non_ipss_ids=False):
        """
        Take data exported from PSOM V2, and modify it such that it can be imported to IPSS V4.
        Parameters:
            from_psom: list of dicts; all records in the PSOM V2 database.
        Returns:
            to_ipss: list of dicts; all PSOM data to be imported into IPSS V3, after changing variable, event names etc.
        """

        # In PSOM V2:
        # - The Summary of Impressions assessment is included only in the 'summary_of_impressions' instrument, which is part of the following events:
        #     - 'acute_hospitalizat_arm_1' (repeating event) - all data collected during initial hospitalization
        #     - 'initial_psom_arm_1' (non repeating) - data collected during first "initial PSOM" which occurred outside of the initial hospitalization
        #     - 'follow_up_psom_arm_1' (repeating event) - all subsequently collected data.
        # In IPSS V4:
        # - The Summary of Impressions assessment is found in the instrument:
        #     - 'summary_of_impressions' (non-repeating in event 'acute_arm_1'; repeating instrument in event 'followup_arm_1') 
        #
        # Link PSOM to IPSS as follows:
        # - Map the instance of the PSOM V2 'summary_of_impressions' form which has the latest 'fuionset_soi' date in the 'acute_hospitalizat_arm_1' event to the IPSS V4 'summary_of_impressions' form in event 'acute_arm_1'.
        #   - SOIs in the 'acute_hospitalizat_arm_1' event with earlier 'fuionset_soi' dates will not be mapped to IPSS V4.
        # - Map the PSOM V2 'summary_of_impressions' form in the 'initial_psom_arm_1' and 'follow_up_psom_arm_1' events to the IPSS V4 'summary_of_impression" form in event 'followup_arm_1'.
        #   - Order the instances in IPSS V4 according to ascending 'fuionset_soi' dates in PSOM V2.
        # - All PSOM V2 summary of impressions (from any event), which have a blank 'fuionset_soi' date will be excluded from IPSS V4. 

        #### Perform record-specific modifications to a few records. Ideally, there will be nothing in this section.
        
        #### Remove data from PSOM which will not be imported into IPSS V4.
        ## Remove all rows (any event) which do not have a PSOM assessment date.
        from_psom_after_exclusions = []
        for row in from_psom:
            soi_date = row['fuionset_soi']
            if (soi_date.strip() != ''): # if the summary of impressions date is not blank
                from_psom_after_exclusions.append(row)
        from_psom = from_psom_after_exclusions
    
        ## Remove all rows for records which do not exist in IPSS V4.
        if (not import_non_ipss_ids):
            from_psom_after_exclusions = []
            excluded_ids = set() # set of IPSSIDs which exist in PSOM, but not in IPSS, and will not be imported.
            record_ids_ipss = getRecordIDList(url_ipss, key_ipss) # list of all records in IPSS.
            for row in from_psom:
                id = row['ipssid']
                if (id in record_ids_ipss):
                    from_psom_after_exclusions.append(row)
                elif (not id in excluded_ids): # if excluded ID has not already been identified and a warning printed.
                    #warnings.warn("IPSSID not found in IPSS, not importing this patient's data: " + id)
                    excluded_ids.add(id)
            from_psom = from_psom_after_exclusions
        
        
        #### Create dictionaries which map IPSSIDs to row numbers in PSOM for (a) the 'acute_hospitalizat_arm_1' event; and (b) the 'initial_psom_arm_1' and 'followup_arm_psom_arm_1' events. These dictionaries are used to determine which rows in PSOM V2 will be mapped to which (instances of which) events in IPSS V4.
        ## Create dictionary for the 'acute_hospitalizat_arm_1' event. Take only the acute_hospitalization row with the latest non-blank 'fuionset_soi' date.
        acute_dict = {}
        for row_index in range(len(from_psom)):
            row = from_psom[row_index]
            id = row['ipssid']
            if (row['redcap_event_name'] == 'acute_hospitalizat_arm_1'): # if row corresponds to 'acute_hospitalizat_arm_1' event
                psom_instance = row['redcap_repeat_instance']
                psom_date = int(row['fuionset_soi'].replace('-','')) # Convert the string '2003-04-05' to the integer 20030405 for comparison later.
                if (not id in acute_dict.keys()): # if there is not yet an entry for this ID in acute_dict
                    acute_dict[id] = (row_index, psom_instance, psom_date)
                elif (psom_date > acute_dict[id][2]): # if ID already in acute_dict and row corresponds to a more recent acute hospitalization instance
                    acute_dict[id] = (row_index, psom_instance, psom_date)

        ## Create dictionary for the 'initial_psom_arm_1' and 'followup_psom_arm_1' events.
        followup_dict = {}
        for row_index in range(len(from_psom)):
            row = from_psom[row_index]
            id = row['ipssid']
            psom_date = int(row['fuionset_soi'].replace('-',''))
            if (row['redcap_event_name'] == 'initial_psom_arm_1'):
                followup_dict[id] = [(row_index, 0, psom_date)] # Assign a fake instance number of 0 to the initial_psom_arm_1 event (this was used in the old method of ordering based on instance number; now order based on 'fuionset_soi').
        for row_index in range(len(from_psom)):
            row = from_psom[row_index]
            id = row['ipssid']
            psom_instance = row['redcap_repeat_instance']
            psom_date = int(row['fuionset_soi'].replace('-',''))
            if (row['redcap_event_name'] == 'follow_up_psom_arm_1'):
                if (not id in followup_dict.keys()):
                    followup_dict[id] = [(row_index, psom_instance, psom_date)]
                else:
                    followup_dict[id].append((row_index, psom_instance, psom_date))
        
        ## Reorder the lists of (row index, PSOM instance) tuples in order of ascending PSOM instance number, so that the correct order will be retained in IPSS.
        for id, row_tuple_list_psom in followup_dict.iteritems():
            row_tuple_list_psom.sort(key=lambda list_element:list_element[2]) # Sort list of tuples using the 'fuionset_soi' values.

        ## Check that follow-up rows are arranged in order of ascending 'fuisonset_soi'. Raise AssertionError if this is not true. This section has no effect on the data; it just checks for errors.
        for id, row_tuple_list_psom in followup_dict.iteritems():
            last_date = 0 # fake date to compare the first date to.
            for row_tuple_psom in row_tuple_list_psom:
                current_date = row_tuple_psom[2]
                assert (current_date >= last_date)
                last_date = current_date

        #### Create functions and dictionaries for field mappings. 
        ## Create a dictionary for Summary of Impressions (PSOM) -> 'summary_of_impressions' (IPSS V4)). The dictionary is of the form {field_name_in_PSOM: field_name_in_IPSS}. This dictionary only includes fields which are directly mapped to a corresponding IPSS V4 field. Fields which are modified prior to transfer are dealt with separately.
        psom_to_ipss_soi = {'fuionset_soi':'psomdate',
                            'fpsomr':'psomr',
                            'fpsoml':'psoml',
                            'fpsomlae':'psomlae',
                            'fpsomlar':'psomlar',
                            'fpsomcb':'psomcb',
                            'psomsen___1':'psomsens___3',
                            'psomsen___2':'psomsens___4',
                            'psomsen___3':'psomsens___5',
                            'psomsen___4':'psomsens___6',
                            'psomsen___5':'psomsens___7',
                            'psomsen___6':'psomsens___8',
                            'psomsen___7':'psomsens___9',
                            'psomsen___8':'psomsens___10',
                            'psomsen___9':'psomsens___11',
                            'psomsen___10':'psomsens___12',
                            'psomsen___11':'psomsens___13',
                            'psomsen___12':'psomsens___14',
                            'othsens':'senssp',
                            'fpsomco___1':'psomcog___1',
                            'fpsomco___2':'psomcog___2',
                            'totpsom':'psomscr',
                            'summary_of_impressions_complete':'summary_of_impressions_complete'
                            }

        ## Create functions which perform the many-to-one mappings.
        def combineComments(row_psom):
            """
            Combine multiple comment fields in PSOM into a single string to be imported into a single IPSS field.
            Parameters:
                row_psom: list of dicts, row in PSOM.
            Returns:
                combined_comments: str, value to be imported into a single IPSS field.
            """

            ## Initialize the combined comments field.
            combined_comments = ''

            ## Add text from the PSOM 'lang_pro_det' (text) field if it is nonempty.
            if (row_psom['lang_pro_det'].strip() != ''):
                combined_comments += 'Language production deficits: ' + row_psom['lang_pro_det'] + '. '

            ## Add text from the PSOM 'lang_comp_det' (text) field if it is nonempty.
            if (row_psom['lang_comp_det'].strip() != ''):
                combined_comments += 'Language comprehension deficits: ' + row_psom['lang_comp_det']+'. '

            ## Add text from the PSOM 'cog_beh_det' (checkbox) field if any options are checked.
            # Create dictionary mapping checkbox number to checkbox option text.
            cog_beh_det_dict = {1:'Remembering what he/she learned', 2:'Staying focused', 3:'Sad or low moods', 4:'Excessive worries', 5:'Getting along with other children', 6:'Other'}

            # Keep note of whether any of the checkboxes are checked for this row.
            any_checked = False

            # Loop over the checkbox option numbers. 
            for box_number in range(1, 6+1):
                box_var = 'cog_beh_det___'+str(box_number) # field name for current checkbox option
                if (row_psom[box_var] == '1'): # if checkbox is checked
                    if (not any_checked): # if this is the first checked option found for the current row
                        combined_comments += 'Cognitive/behavioural deficits: '
                        any_checked = True
                    combined_comments += cog_beh_det_dict[box_number]+', '
            
            # Replace trailing comma with trailing period
            if (combined_comments[-2:] == ', '):
                combined_comments = combined_comments[:-2] + '. '
    
            ## Add text from the PSOM 'cbcomm' (text) field if it is nonempty.
            if (row_psom['cbcomm'].strip() != ''):
                combined_comments += 'Other cognitive/behavioural deficits: ' + row_psom['cbcomm'] + '. '

            ## Add text from the PSOM 'stroke_cause_y_n' (yesno) field if it is nonempty.
            if (row_psom['stroke_cause_y_n'] != ''):
                combined_comments += 'Are all neurologic deficits attributable to stroke?: '
                if (row_psom['stroke_cause_y_n'] == '1'):
                    combined_comments += 'Yes. '
                else:
                    combined_comments += 'No. '

            ## Add text from the PSOM 'cause_det' (notes) field if it is nonempty.
            if (row_psom['cause_det'].strip() != ''):
                combined_comments += 'Specify which deficits are not attributable to stroke, and state responsible diagnosis: ' + row_psom['cause_det']

            ## Strip trailing comma.
            if (combined_comments[-2:] in [', ', '. ']):
                combined_comments = combined_comments[:-2]
            
            return combined_comments
        

        #### Build the import data for IPSS V4 using the IPPSID-to-row-number mappings.
        ## Initialize data to be imported into IPSS V4.
        to_ipss = []
    
        ## Map data to IPSS 'acute_arm_1' event.
        for id, row_tuple_psom in acute_dict.iteritems(): # Loop over IPSSIDs which have at least one 'acute_hospitalizat_arm_1' event in PSOM V2.
            row_index_psom = row_tuple_psom[0]
            row_psom = from_psom[row_index_psom] # PSOM row to be imported into IPSS.
            assert (row_psom['redcap_event_name'] == 'acute_hospitalizat_arm_1') # Check that PSOM row corresponds to the appropriate PSOM event.

            # Initialize the row to be imported into IPSS.
            row_ipss = {'ipssid':id, 'redcap_event_name':'acute_arm_1', 'redcap_repeat_instrument':'', 'redcap_repeat_instance':''}
            
            # Add the variables with a one-to-one mapping.
            for field_name_psom, field_name_ipss in psom_to_ipss_soi.iteritems():
                value = row_psom[field_name_psom]
                row_ipss[field_name_ipss] = value
            
            # Add the variables with a many-to-one mapping
            sdcom = combineComments(row_psom)
            row_ipss['sdcom'] = sdcom
            
            # Append row to IPSS data.
            to_ipss.append(row_ipss)

        ## Map data to IPSS 'followup_arm_1' evemt. Note that the followup rows have already been ordered based on fuionset_soi at this point.
        for id, row_tuple_list_psom in followup_dict.iteritems():
            instance_ipss = 1 # instance number for current row in IPSS
            for row_tuple_psom in row_tuple_list_psom:
                row_index_psom = row_tuple_psom[0]
                row_psom = from_psom[row_index_psom]
                assert (row_psom['redcap_event_name'] != 'acute_hospitalizat_arm_1') # Check that PSOM row corresponds to the appropriate PSOM events.
                
                # Initialize the row to be imported into IPSS.
                row_ipss = {'ipssid':id, 'redcap_event_name':'followup_arm_1', 'redcap_repeat_instrument':'summary_of_impressions', 'redcap_repeat_instance':str(instance_ipss)}

                # Add the variables with a one-to-one mapping.
                for field_name_psom, field_name_ipss in psom_to_ipss_soi.iteritems():
                    value = row_psom[field_name_psom]
                    row_ipss[field_name_ipss] = value
            
                # Add the variables with a many-to-one mapping
                sdcom = combineComments(row_psom)
                row_ipss['sdcom'] = sdcom

                ## Append row to IPSS data.
                to_ipss.append(row_ipss)

                ## Increment the IPSS instance number
                instance_ipss += 1

        return to_ipss
    
    ## Export Summary of Impressions data from PSOM.
    from_psom = exportRecords(url_psom, key_psom, fields=None, forms=None, quiet=True, export_form_completion=True)

    ## Map the PSOM data to IPSS fields.
    to_ipss = modifyRecords(from_psom, url_ipss, key_ipss, import_non_ipss_ids=import_non_ipss_ids)

    ## Import data to IPSS.
    importRecords(url_ipss, key_ipss, to_ipss, overwrite='overwrite', quick=True, return_content='count')

    return

#### If this script was called , run transferPSOMToIPSS() using API keys and URLs stored in the default location defined near the start of this 
if (__name__ == '__main__'):
    #### Handle command-line argumnets
    ## Create argument parser.
    description = """Transfer data from PSOM V2 'Summary of Impressions' form to IPSS V4 'Status at Discharge' and 'Outcome - PSOM' forms"""
    parser = argparse.ArgumentParser(description=description)

    ## Define optional arguments.
    # arguments for API URLs and keys of PSOM and IPSS.
    parser.add_argument('--url_psom', help="API URL for PSOM project to map from. Default: Read from api_keys.yml file under code name 'psom_v2'", type=str)
    parser.add_argument('--key_psom', help="API key for PSOM project to map from. Default: Read from api_keys.yml file under code name 'psom_v2'", type=str)
    parser.add_argument('--url_ipss', help="API URL for IPSS project to map to. Default: Read from api_keys.yml file under code name 'ipss_v4'", type=str)
    parser.add_argument('--key_ipss', help="API key for IPSS project to map to. Default: Read from api_keys.yml file under code name 'ipss_v4'", type=str)

    parser.add_argument('--import_non_ipss_ids', help='Import of records which do not exist in the IPSS (i.e. create new records in IPSS). By default, records are only imported to IPSS if there ID already exists in IPSS. This option exists for debugging purposes only.', action='store_true')
    
    ## Parse arguments.
    args = parser.parse_args()

    #### Read API keys and URLS from file, to be used as the default arguments for this command line function.
    if (None in [args.url_psom, args.key_psom, args.url_ipss, args.key_ipss]):
        print "At least one API URL or token was not specified. Attempting to read from user's api_keys.yml file. Any URLs or tokens specified as arguments will be ignored."
        print
        api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find file containing API keys and URLs.
        url_psom, key_psom, code_name_psom = api_settings.getApiCredentials(code_name="psom_v2")
        url_ipss, key_ipss, code_name_ipss = api_settings.getApiCredentials(code_name="ipss_v4")

    else:
        url_psom = args.url_psom
        key_psom = args.key_psom
        url_ipss = args.url_ipss
        key_ipss = args.key_ipss
    # If, for some reason, user specified only certain keys as arguments, use those keys instead of the ones read from 

    
    ## Transfer data from PSOM to IPSS.
    transferPSOMToIPSS(url_psom, key_psom, url_ipss, key_ipss, import_non_ipss_ids=args.import_non_ipss_ids)
