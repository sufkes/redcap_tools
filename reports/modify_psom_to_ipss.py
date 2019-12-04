def modifyRecords(from_psom):
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
    # In IPSS V3:
    # - The Summary of Impressions assessment is included in the instruments:
    #     - 'status_at_discharge' (only in event 'acute_arm_1', non-repeating) 
    #     - 'outcome' (only in event 'followup_arm_1', independently repeating form).
    # Link PSOM to IPSS as follows:
    # - Most recent acute hospitalization SOI should be mapped to status at discharge (only appears in acute event). Previous SOIs will not be mapped to IPSS at all.
    # - From PSOM, all initial and followup PSOM data should be mapped to IPSS followup event, 
    # outcome form. When there is no PSOM initial SOI, the first followup SOI should be mapped to 
    # instance 1 etc. If there is an initial PSOM SOI, the first PSOM followup SOI will be mapped to 
    # instance 2 in IPSS.
    #
    # This script must determine the event/form mapping separately for each record.
    
    # Create field name mappings. Need one for SOI (PSOM) -> status at discharge (IPSS V3), and one for SOI (PSOM) -> Outcome (IPSS V3)
    # Both dicts will be of the form {field_name_in_PSOM: field_name_in_IPSS}
    psom_to_status_dict = {}
    psom_to_outcome_dict = {}

    # Map the 'acute_hospitalizat_arm_1' event first
    acute_dict = {}
    print 'WARNING: Figure out what criteria should determine whether an acute_hospitalizat_arm_1 Summary of Impressions will be mapped to V3. Currently importing SOI data from all initial_psom_arm_1 rows for which summary_of_impressions_complete is not zero. At the time of writing (2019-08-28), this will exclude only empty rows, and will include ~1 row with no data.'
    for row_index in range(len(from_psom)): # loop through all 'initial_hospitalizat_arm_1' event rows.
        row = from_psom[row_index]
        id = row['ipssid']
        if (row['redcap_event_name'] == 'acute_hospitalizat_arm_1'):
            psom_instance = row['redcap_repeat_instance']
            if (not id in acute_dict.keys()):
                acute_dict[id] = (row_index, psom_instance)
            elif (psom_instance > acute_dict[id][1]): # if ID already in acute_dict and row corresponds to a newer acute hospitalization instance
                acute_dict[id] = (row_index, psom_instance)

    followup_dict = {}
    print 'WARNING: Figure out what criteria should determine whether an initial_psom_arm_1 Summary of Impressions will be mapped to V3. Currently importing SOI data from all initial_psom_arm_1 rows for which summary_of_impressions_complete is not zero. At the time of writing (2019-08-28), this will exclude only empty rows, and will include ~1 row with no data.'
    for row_index in range(len(from_psom)): # loop through all 'initial_psom_arm_1' event rows.
        row = from_psom[row_index]
        id = row['ipssid']
        # NEED TO DECIDE WHAT CRITERIA SHOULD DETERMINE WHETHER THE initial_psom_arm_1 SOI WILL BE MAPPED TO IPSS V3
        if (row['redcap_event_name'] == 'initial_psom_arm_1'):
            followup_dict[id] = [(row_index, 0)]]
    for row_index in range(len(from_psom)): # loop through all 'initial_psom_arm_1' event rows.
        row = from_psom[row_index]
        id = row['ipssid']
        psom_instance = row['redcap_repeat_instance']
        # NEED TO DECIDE WHAT CRITERIA SHOULD DETERMINE WHETHER THE initial_psom_arm_1 SOI WILL BE MAPPED TO IPSS V3
        if (row['redcap_event_name'] == 'follow_up_psom_arm_1'): # if the row corresponds to the initial_psom event, and the Summary of Impressions was completed for this event.
            if (not id in followup_dict.keys()):
                followup_dict[id] = [(row_index, psom_instance)]
            else:
                followup_dict[id].append((row_index, psom_instance))

    ## Now, the PSOM rows to take for each record, and their final ordering in IPSS V3 is known.
    ## Next, build the import data for IPSS V3 using these mappings.
    to_ipss = []

    # Map data to 'status_at_discharge':
    for id, row_tuple_psom in acute_dict.iteritems():
        row_index_psom = row_tuple_psom[0]
        instance_psom = row_tuple_psom[0] # not used.

        row_ipss = {'ipssid':id, 'redcap_event_name':'acute_arm_1', 'redcap_repeat_instrument':'', 'redcap_repeat_instance':''} # initialize the row to be imported into IPSS.
        for field_name_psom, field_value_psom in from_psom[row_index_psom]:
            if (field_name_psom in ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance']):
                continue

    # Map data to 'outcome'
    for id, row_tuple_psom in followup_dict.iteritems():
        pass

    return to_ipss
