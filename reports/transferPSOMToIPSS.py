#!/usr/bin/env python

#### Import modules
# Standard modules 
import os, sys
import argparse
import warnings
from pprint import pprint

# My modules from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import misc
from misc.exportRecords import exportRecords
from misc.importRecords import importRecords
from misc.getRecordIDList import getRecordIDList

#### Read API keys and URLS from file, to be used as the default arguments for this command line function.
dir_data_packages = "/Users/steven ufkes/Documents/stroke/data_packages" # directory containing IPSS data
api_url_key_list_path = os.path.join(dir_data_packages, "api_url_key_list.txt") # list of api keys, urls 
with open(api_url_key_list_path, 'r') as fh:
    try:
        api_pairs = [(p.split()[0], p.split()[1]) for p in fh.readlines() if (p.strip() != "") and (p.strip()[0] != "#")] # separate lines by spaces; look only at first two items; skip whitespace lines.
    except IndexError:
        print "Error: cannot parse list of API (url, key) pairs. Each line in text file must contain the API url and API key for a single project separated by a space."
        sys.exit()
url_psom2_default = api_pairs[5][0]
key_psom2_default = api_pairs[5][1]
url_ipss4_default = api_pairs[6][0]
key_ipss4_default = api_pairs[6][1]

#### Define function which transfers data from PSOM V2 to IPSS V4.
def transferPSOMToIPSS(url_psom=url_psom2_default, key_psom=key_psom2_default, url_ipss=url_ipss4_default, key_ipss=key_ipss4_default):
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
    def modifyRecords(from_psom, url_ipss, key_ipss):
        """
        Parameters:
            from_psom: list of dicts; all records in the PSOM V2 database.
        Returns:
            to_ipss: list of dicts; all PSOM data to be imported into IPSS V3, after changing variable, event names etc.
        """

        # In PSOM V2:
        # - The Summary of Impressions assessment is included only in the 'summary_of_impressions' instrument, which is part of the following events:
        #     - 'acute_hospitalizat_arm_1' (dependently repeating event) - all data collected during initial hospitalization
        #     - 'initial_psom_arm_1' (non repeating) - data collected during first "initial PSOM" which occurred outside of the initial hospitalization
        #     - 'follow_up_psom_arm_1' (dependently repeating event) - all subsequently collected data.
        # In IPSS V4:
        # - The Summary of Impressions assessment is found in the instrument:
        #     - 'summary_of_impressions' (non-repeating in event 'acute_arm_1'; independently repeating in event 'followup_arm_1') 
        #
        # Link PSOM to IPSS as follows:
        # - Map the highest instance of the PSOM V2 'summary_of_impressions' form in the 'acute_hospitalizat_arm_1' event to the IPSS V4 'summary_of_impressions' form in event 'acute_arm_1'.
        #   - Earlier SOIs in the acute_hospitalizat_arm_1 event will not be mapped to IPSS V4.
        # - Map the PSOM V2 'summary_of_impressions' form in the 'initial_psom_arm_1' and 'follow_up_psom_arm_1' events to the IPSS V4 'summary_of_impression" form in event 'followup_arm_1'.
        #   - When there is no PSOM initial SOI (i.e. the PSOM assessment date is blank), the first followup SOI should be mapped to instance 1 etc. If there is an initial PSOM SOI, the first PSOM followup SOI will be mapped to instance 2 in IPSS.
        # - All PSOM V2 summary of impressions (from any event), which have a blank PSOM assessment date will be excluded from IPSS V4. 


        #### Perform record-specific modifications to a few records. Ideally, there will be nothing in this section.
        warnings.warn("Need to perform record-specific modifications per Alex's spreadsheet.")
        warnings.warn("Should delete all Summary of Impressions data for SickKids patients before importing.")
        warnings.warn("Currently there is no method to ensure that a SOI in PSOM V2 actually corresponds to the correct row in IPSS V4.")
        
        #### Remove data from PSOM which will not be imported into IPSS V4.
        ## Remove all rows (any event) which do not have a PSOM assessment date.
        from_psom_after_exclusions = []
        for row in from_psom:
            soi_date = row['fuionset_soi']
            if (soi_date.strip() != ''): # if the summary of impressions date is not blank
                from_psom_after_exclusions.append(row)
        from_psom = from_psom_after_exclusions
    
        ## Remove all rows for records which do not exist in IPSS V4.
        from_psom_after_exclusions = []
        excluded_ids = set() # set of IPSSIDs which exist in PSOM, but not in IPSS, and will not be imported.
        record_ids_ipss = getRecordIDList(url_ipss, key_ipss) # list of all records in IPSS.
        for row in from_psom:
            id = row['ipssid']
            if (id in record_ids_ipss):
                from_psom_after_exclusions.append(row)
            elif (not id in excluded_ids): # if excluded ID has not already been identified and a warning printed.
                warnings.warn("IPSSID not found in IPSS, not importing this patient's data: " + id)
                excluded_ids.add(id)
        from_psom = from_psom_after_exclusions
        
        
        #### Create dictionaries which map IPSSIDs to row numbers in PSOM for (a) the 'acute_hospitalizat_arm_1' event; and (b) the 'initial_psom_arm_1' and 'followup_arm_psom_arm_1' events. These dictionaries are used to determine which rows in PSOM V2 will be mapped to which (instances of which) events in IPSS V4.
        ## Create dictionary for the 'acute_hospitalizat_arm_1' event. By default, take the acute_hospitalization row with the highest instance number.
        acute_dict = {}
   #     special_ids = {'1554':('1','2000-10-02'), '1804':(1, '2006-03-11')} # key: ipssid, value: (instance to use, fuionset to use)
        for row_index in range(len(from_psom)): # loop through all 'initial_hospitalizat_arm_1' event rows.
            row = from_psom[row_index]
            id = row['ipssid']
            if (row['redcap_event_name'] == 'acute_hospitalizat_arm_1'):
                psom_instance = row['redcap_repeat_instance']            
                if (not id in acute_dict.keys()):
                    acute_dict[id] = (row_index, psom_instance) # key = IPSSID; value = tuple(PSOM row index, psom instance number)
                elif (psom_instance > acute_dict[id][1]): # if ID already in acute_dict and row corresponds to a newer acute hospitalization instance
                    acute_dict[id] = (row_index, psom_instance)

        ## Create dictionary for the 'initial_psom_arm_1' and 'followup_psom_arm_1' events.
        followup_dict = {}
        for row_index in range(len(from_psom)):
            row = from_psom[row_index]
            id = row['ipssid']
            if (row['redcap_event_name'] == 'initial_psom_arm_1'):
                followup_dict[id] = [(row_index, 0)] # Assign a fake instance number of 0 to the initial_psom_arm_1 event.
        for row_index in range(len(from_psom)):
            row = from_psom[row_index]
            id = row['ipssid']
            psom_instance = row['redcap_repeat_instance']
            if (row['redcap_event_name'] == 'follow_up_psom_arm_1'):
                if (not id in followup_dict.keys()):
                    followup_dict[id] = [(row_index, psom_instance)] # key = IPSSID; value = list of tuple(PSOM row index, psom instance number)
                else:
                    followup_dict[id].append((row_index, psom_instance))
        
        ## Reorder the lists of (row index, PSOM instance) tuples in order of ascending PSOM instance number, so that the correct order will be retained in IPSS.
        for id, row_tuple_list_psom in followup_dict.iteritems():
            row_tuple_list_psom.sort(key=lambda list_element:list_element[1]) # Sort list of tuples using the second element in each tuple.

        ## Check that follow-up rows are arranged in order of ascending instance number. Raise AssertionError if this is not true.
        for id, row_tuple_list_psom in followup_dict.iteritems():
            last_instance = -1
            for row_tuple_psom in row_tuple_list_psom:
                current_instance = row_tuple_psom[1]
                assert (current_instance > last_instance)
                last_instance = current_instance

        #### Create functions and dictionaries for field mappings. 
        ## Create a dictionary for Summary of Impressions (PSOM) -> 'summary_of_impressions' (IPSS V4)). The dictionary is of the form {field_name_in_PSOM: field_name_in_IPSS}. This dictionary only includes fields which are directly mapped to a corresponding IPSS V4 field. Fields which are modified prior to transfer are dealt with separately.
        psom_to_ipss_soi = {'fuionset_soi':'psomdate',
                            'fpsomr':'psomr',
                            'fpsoml':'psoml',
                            'fpsomlae':'psomlae',
                            'fpsomlar':'psomlar',
                            'fpsomcb':'psomcb',
                            'psomsen___1':'psomsens___3', # would be good to change this to start at one, and be consistent with PSOM V2. Should add this to transferData.py
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
                            'totpsom':'psomscr'
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
#            instance_psom = row_tuple_psom[1]
            row_psom = from_psom[row_index_psom] # PSOM row to be imported into IPSS.
            assert (row_psom['redcap_event_name'] == 'acute_hospitalizat_arm_1') # Check that PSOM row corresponds to the appropriate PSOM event.

            # Initialize the row to be imported into IPSS.
            row_ipss = {'ipssid':id, 'redcap_event_name':'acute_arm_1', 'redcap_repeat_instrument':'', 'redcap_repeat_instance':''}
            
            # Add the variables with a one-to-one mapping.
#            for field_name_psom, field_name_ipss in psom_to_status_dict.iteritems(): # METHOD USED BEFORE MOVING SUMMARY OF IMPRESSIONS TO A SEPARATE FORM.
            for field_name_psom, field_name_ipss in psom_to_ipss_soi.iteritems():
                value = row_psom[field_name_psom]
                row_ipss[field_name_ipss] = value
            
            # Add the variables with a many-to-one mapping
            sdcom = combineComments(row_psom)
            row_ipss['sdcom'] = sdcom
            
            # Append row to IPSS data.
            to_ipss.append(row_ipss)

        ## Map data to IPSS 'followup_arm_1' evemt.
        for id, row_tuple_list_psom in followup_dict.iteritems():
            instance_ipss = 1 # instance number for current row in IPSS
            for row_tuple_psom in row_tuple_list_psom:
                row_index_psom = row_tuple_psom[0]
#                instance_psom = row_tuple_psom[1]
                row_psom = from_psom[row_index_psom]
                assert (row_psom['redcap_event_name'] != 'acute_hospitalizat_arm_1') # Check that PSOM row corresponds to the appropriate PSOM event.
                
                # Initialize the row to be imported into IPSS.
                row_ipss = {'ipssid':id, 'redcap_event_name':'followup_arm_1', 'redcap_repeat_instrument':'summary_of_impressions', 'redcap_repeat_instance':str(instance_ipss)}

                # Add the variables with a one-to-one mapping.
#                for field_name_psom, field_name_ipss in psom_to_outcome_dict.iteritems(): # METHOD USED BEFORE MOVING SUMMARY OF IMPRESSIONS TO A SEPARATE FORM.
                for field_name_psom, field_name_ipss in psom_to_ipss_soi.iteritems():
                    value = row_psom[field_name_psom]
                    row_ipss[field_name_ipss] = value
            
                # Add the variables with a many-to-one mapping
#                fucomm = combineComments(row_psom) # METHOD USED BEFORE MOVING SUMMARY OF IMPRESSIONS TO A SEPARATE FORM.
#                row_ipss['fucomm'] = fucomm
                sdcom = combineComments(row_psom)
                row_ipss['sdcom'] = sdcom

                ## Append row to IPSS data.
                to_ipss.append(row_ipss)

                ## Increment the IPSS instance number
                instance_ipss += 1

        return to_ipss
    
    ## Export Summary of Impressions data from PSOM.
    from_psom = exportRecords(url_psom, key_psom, fields=None, forms=None, quiet=True)

    ## Map the PSOM data to IPSS fields.
    to_ipss = modifyRecords(from_psom, url_ipss, key_ipss)

    ## Import data to IPSS.
    importRecords(url_ipss, key_ipss, to_ipss, overwrite='overwrite', quick=True)

    return

#### If this script was called directly, run transferPSOMToIPSS() using API keys and URLs stored in the default location defined near the start of this 
if (__name__ == '__main__'):
    #### Handle command-line argumnets
    ## Create argument parser.
    description = """Transfer data from PSOM V2 'Summary of Impressions' form to IPSS V4 'Status at Discharge' and 'Outcome - PSOM' forms"""
    parser = argparse.ArgumentParser(description=description)

    ## Define optional arguments.
    # arguments for API URLs and keys of PSOM and IPSS.
    parser.add_argument('--url_psom', help='API URL for PSOM project to map from', type=str, default=url_psom2_default)
    parser.add_argument('--key_psom', help='API key for PSOM project to map from', type=str, default=key_psom2_default)
    parser.add_argument('--url_ipss', help='API URL for IPSS project to map to', type=str, default=url_ipss4_default)
    parser.add_argument('--key_ipss', help='API key for IPSS project to map to', type=str, default=key_ipss4_default)

    ## Parse arguments.
    args = parser.parse_args()

    ## Transfer data from PSOM to IPSS.
    transferPSOMToIPSS(url_psom=args.url_psom, key_psom=args.key_psom, url_ipss=args.url_ipss, key_ipss=args.key_ipss)
