import warnings
def getEventIDs(unique_event_name, project_info):
    project_id = project_info["project_id"]

    warnings.warn('Need to add event_id numbers for IPSS V4. To do this, access the "acute_arm_1" and "followup_arm_1" events online, look in the address bar for the "event_id" number, and add those numbers to the appropriate lines below.')
    warnings.warn('These should be put in a json file and read in, instead of having the mapping inside the script itself.')
    warnings.warn('URLs should be generated using the REDCap version number exported from the API call.')
    
    # IPSS V3 mapping
    if (project_id == 3091):
        if (unique_event_name == "acute_arm_1"):
            event_id = "24670"
        elif (unique_event_name == "followup_arm_1"):
            event_id = "24671"
        else:
            event_id = None

    # IPSS V4 mapping - FILL THIS IN BY ACCESSING THE EVENTS IN V4, AND LOOKING IN THE ADDRESS BAR FOR THE event_id NUMBER. 
    elif (project_id == 4342):
        if (unique_event_name == "acute_arm_1"):
            event_id = "32695" # put event_id for the IPSS V4 'acute_arm_1' event here.
        elif (unique_event_name == "followup_arm_1"):
            event_id = "32696" # put event_id for the IPSS V4 'followup_arm_1' event here.
        else:
            event_id = None
            
    # SIPS II mapping
    elif (project_id == 3293):
        if (unique_event_name == "confirmation_and_t_arm_1"):
            event_id = "28070"
        elif (unique_event_name == "neuroimaging_arm_1"):
            event_id = "28135"
        elif (unique_event_name == "acute_arm_1"):
            event_id = "28092"
        elif (unique_event_name == "3_month_arm_1"):
            event_id = "28071"
        elif (unique_event_name == "12_month_arm_1"):
            event_id = "28072"
        elif (unique_event_name == "additional_fup1_arm_1"):
            event_id = "28087"
        elif (unique_event_name == "additional_fup2_arm_1"):
            event_id = "28088"
        elif (unique_event_name == "additional_fup3_arm_1"):
            event_id = "28089"
        elif (unique_event_name == "additional_fup4_arm_1"):
            event_id = "28090"
        elif (unique_event_name == "additional_fup5_arm_1"):
            event_id = "28091"
        elif (unique_event_name == "additional_fup6_arm_1"):
            event_id = "28078"
        else:
            event_id = None

    # VIPS II mapping
    elif (project_id == 2401):
        if (unique_event_name == "confirmation_and_t_arm_1"):
            event_id = "28163"
        elif (unique_event_name == "biosamples_arm_1"):
            event_id = "28166"
        elif (unique_event_name == "neuroimaging_arm_1"):
            event_id = "28165"
        elif (unique_event_name == "acute_arm_1"):
            event_id = "18585"
        elif (unique_event_name == "recurrence_arm_1"):
            event_id = "28172"
        elif (unique_event_name == "12_month_arm_1"):
            event_id = "18587"
        elif (unique_event_name == "arteriopathy_class_arm_1"):
            event_id = "28237"
        elif (unique_event_name == "additional_fup_1_arm_1"):
            event_id = "18618"
        elif (unique_event_name == "additional_fup_2_arm_1"):
            event_id = "18619"
        elif (unique_event_name == "additional_fup_3_arm_1"):
            event_id = "18620"
        elif (unique_event_name == "additional_fup_4_arm_1"):
            event_id = "18621"
        elif (unique_event_name == "confirmation_and_t_arm_2"):
            event_id = "28164"
        elif (unique_event_name == "biosamples_arm_2"):
            event_id = "28167"
        elif (unique_event_name == "clinical_requireme_arm_2"):
            event_id = "20714"
        else:
            event_id = None
    
    # UNMAPPED PROJECT
    else:
        event_id = None
    return event_id
